import logging
import re
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.assignment import ReferenceDocument

logger = logging.getLogger(__name__)


class OriginalityService:
    """Calculates AI-assisted similarity indicators comparing a submission against corpus peers and course references."""

    def __init__(
        self,
        low_threshold: float = settings.SIMILARITY_THRESHOLD_LOW,
        med_threshold: float = settings.SIMILARITY_THRESHOLD_MEDIUM,
        high_threshold: float = settings.SIMILARITY_THRESHOLD_HIGH,
    ):
        self.low_threshold = low_threshold
        self.med_threshold = med_threshold
        self.high_threshold = high_threshold

    def analyze_similarity(
        self,
        db: Session,
        submission_id: int,
        assignment_id: int,
        submission_text: str,
    ) -> Dict[str, Any]:
        """
        Analyzes the similarity of submission_text against all other submissions in the database
        for this assignment and reference course materials.
        """
        if not submission_text or len(submission_text.strip()) < 20:
            return {
                "similarity_percentage": 0.0,
                "risk_level": "low",
                "status_label": "Low Similarity",
                "match_summary": "Submission is too short for meaningful similarity index comparison.",
                "matched_submission_count": 0,
                "matches": [],
                "disclaimer": "AI-assisted similarity indicator. This metric represents lexical and semantic overlap with existing course submissions and reference materials. It is not a definitive judgment of plagiarism."
            }

        # 1. Fetch other submissions for this assignment (excluding current one)
        other_submissions = (
            db.query(Submission)
            .filter(
                Submission.assignment_id == assignment_id,
                Submission.id != submission_id,
                Submission.extracted_text.isnot(None),
            )
            .all()
        )

        # 2. Fetch reference documents
        ref_docs = (
            db.query(ReferenceDocument)
            .filter(
                ReferenceDocument.assignment_id == assignment_id,
                ReferenceDocument.extracted_text.isnot(None),
            )
            .all()
        )

        corpus_texts = [submission_text]
        corpus_metadata = [{"type": "target", "id": submission_id, "title": "Current Submission"}]

        for sub in other_submissions:
            if sub.extracted_text and len(sub.extracted_text.strip()) > 30:
                corpus_texts.append(sub.extracted_text)
                corpus_metadata.append({
                    "type": "peer_submission",
                    "id": sub.id,
                    "student_name": sub.student.full_name if sub.student else f"Student #{sub.student_id}",
                    "file_name": sub.file_name,
                    "title": f"Submission #{sub.id} ({sub.file_name})"
                })

        for doc in ref_docs:
            if doc.extracted_text and len(doc.extracted_text.strip()) > 30:
                corpus_texts.append(doc.extracted_text)
                corpus_metadata.append({
                    "type": "reference_document",
                    "id": doc.id,
                    "student_name": "Course Material",
                    "file_name": doc.file_name,
                    "title": doc.title
                })

        # If no other documents exist in corpus
        if len(corpus_texts) == 1:
            return {
                "similarity_percentage": 2.5,  # Nominal baseline
                "risk_level": "low",
                "status_label": "Low Similarity",
                "match_summary": "No other peer submissions or reference documents currently available in this assignment pool.",
                "matched_submission_count": 0,
                "matches": [],
                "disclaimer": "AI-assisted similarity indicator. This metric represents lexical and semantic overlap with existing course submissions and reference materials. It is not a definitive judgment of plagiarism."
            }

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 3),
                max_features=5000,
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform(corpus_texts)
            
            # Compute cosine similarity of target (index 0) against all other items
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            matches = []
            max_sim = 0.0

            for idx, sim in enumerate(cosine_sims):
                sim_float = float(sim)
                meta = corpus_metadata[idx + 1]
                
                # Check for shared snippets if similarity is meaningful (> 0.08)
                overlap_snippet = None
                if sim_float > 0.08:
                    overlap_snippet = self._find_matching_phrases(submission_text, corpus_texts[idx + 1])

                sim_pct = round(sim_float * 100, 1)
                if sim_pct > max_sim:
                    max_sim = sim_pct

                if sim_float >= 0.05:  # Report matches above 5%
                    matches.append({
                        "source_type": meta["type"],
                        "source_title": meta["title"],
                        "student_name": meta.get("student_name", "Anonymous"),
                        "file_name": meta.get("file_name", ""),
                        "similarity_score": round(sim_float, 4),
                        "similarity_percentage": sim_pct,
                        "overlap_snippet": overlap_snippet
                    })

            # Sort matches descending by percentage
            matches.sort(key=lambda x: x["similarity_percentage"], reverse=True)

            overall_percentage = round(min(100.0, max(2.0, max_sim)), 1)
            
            # Determine risk level
            if overall_percentage < self.low_threshold * 100:
                risk_level = "low"
                status_label = "Low Similarity"
                summary = f"Originality check passed. Low similarity ({overall_percentage}%) detected across {len(corpus_texts)-1} corpus items."
            elif overall_percentage < self.med_threshold * 100:
                risk_level = "medium"
                status_label = "Moderate Similarity"
                summary = f"Moderate overlap ({overall_percentage}%) identified. Typical for shared assignment templates or common formulas."
            else:
                risk_level = "high"
                status_label = "High Similarity"
                summary = f"Elevated similarity index ({overall_percentage}%) detected against peer submissions. Teacher review advised."

            return {
                "similarity_percentage": overall_percentage,
                "risk_level": risk_level,
                "status_label": status_label,
                "match_summary": summary,
                "matched_submission_count": len(matches),
                "matches": matches[:5],  # top 5 matches
                "disclaimer": "AI-assisted similarity indicator. This metric represents lexical and semantic overlap with existing course submissions and reference materials. It is not a definitive judgment of plagiarism."
            }

        except Exception as e:
            logger.error(f"Error during originality analysis: {e}")
            return {
                "similarity_percentage": 5.0,
                "risk_level": "low",
                "status_label": "Low Similarity",
                "match_summary": "Originality analysis completed with baseline fallback.",
                "matched_submission_count": 0,
                "matches": [],
                "disclaimer": "AI-assisted similarity indicator. This metric represents lexical and semantic overlap with existing course submissions and reference materials. It is not a definitive judgment of plagiarism."
            }

    def _find_matching_phrases(self, text_a: str, text_b: str, min_words: int = 5) -> str:
        """Find the longest continuous overlapping sentence or phrase between two texts."""
        sentences_a = [s.strip() for s in re.split(r'[.!?\n]', text_a) if len(s.strip().split()) >= min_words]
        for s in sentences_a:
            # Check if 4+ consecutive words of s appear in text_b
            words = s.split()
            for i in range(len(words) - min_words + 1):
                phrase = " ".join(words[i:i + min_words]).lower()
                if phrase in text_b.lower():
                    return f"...{s}..."
        return ""


originality_service = OriginalityService()
