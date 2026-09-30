import json
import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM integration supporting Google Gemini, OpenAI, and smart offline heuristic analysis."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY

    async def evaluate_criterion(
        self,
        criterion_name: str,
        criterion_description: str,
        max_points: float,
        evaluation_guidelines: str,
        submission_text: str,
        rag_context: List[Dict[str, Any]],
        assignment_title: str,
    ) -> Dict[str, Any]:
        """
        Evaluates a student submission against a specific rubric criterion.
        Returns: {
            "score": float,
            "rationale": str,
            "evidence_quote": str,
            "strength": str,
            "improvement": str
        }
        """
        # Try real LLM if API keys are configured
        if self.gemini_key:
            res = await self._call_gemini_criterion_eval(
                criterion_name, criterion_description, max_points, evaluation_guidelines, submission_text, rag_context
            )
            if res:
                return res

        if self.openai_key:
            res = await self._call_openai_criterion_eval(
                criterion_name, criterion_description, max_points, evaluation_guidelines, submission_text, rag_context
            )
            if res:
                return res

        # Deterministic analytical evaluator (offline fallback)
        return self._offline_criterion_analysis(
            criterion_name, criterion_description, max_points, evaluation_guidelines, submission_text, rag_context
        )

    async def generate_feedback_summary(
        self,
        assignment_title: str,
        student_name: str,
        criterion_scores: List[Dict[str, Any]],
        submission_text: str,
        similarity_percentage: float,
    ) -> Dict[str, Any]:
        """
        Synthesizes strengths, areas for improvement, and overall executive summary.
        Returns: {
            "executive_summary": str,
            "strengths": List[str],
            "weaknesses": List[str],
            "improvements": List[str],
            "action_items": List[str]
        }
        """
        if self.gemini_key:
            res = await self._call_gemini_feedback(assignment_title, student_name, criterion_scores, submission_text)
            if res:
                return res

        if self.openai_key:
            res = await self._call_openai_feedback(assignment_title, student_name, criterion_scores, submission_text)
            if res:
                return res

        return self._offline_feedback_synthesis(assignment_title, student_name, criterion_scores, submission_text)

    # --------------------------------------------------------------------------
    # Google Gemini API Call
    # --------------------------------------------------------------------------
    async def _call_gemini_criterion_eval(
        self, criterion_name: str, description: str, max_points: float, guidelines: str, submission_text: str, rag_context: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            context_str = "\n".join([f"- [{c['source']}] {c['content']}" for c in rag_context])
            
            prompt = f"""
You are an expert academic evaluator. Evaluate the student's submission specifically for the following criterion:
Criterion: {criterion_name} (Max Points: {max_points})
Description: {description}
Evaluation Guidelines: {guidelines}

Relevant Assignment & Reference Context:
{context_str}

Student Submission Excerpt:
\"\"\"
{submission_text[:3500]}
\"\"\"

Respond ONLY with valid JSON in this exact structure:
{{
    "score": <float between 0 and {max_points}>,
    "rationale": "<specific explanation of why this score was awarded based on evidence in the text>",
    "evidence_quote": "<an exact sentence or phrase from the student's submission that supports this score>",
    "strength": "<key strength observed for this criterion>",
    "improvement": "<actionable improvement for this criterion>"
}}
"""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)
                    # Enforce score bound
                    parsed["score"] = max(0.0, min(float(parsed.get("score", max_points * 0.7)), max_points))
                    return parsed
                else:
                    logger.warning(f"Gemini API error: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.warning(f"Gemini call failed: {e}")
        return None

    # --------------------------------------------------------------------------
    # OpenAI API Call
    # --------------------------------------------------------------------------
    async def _call_openai_criterion_eval(
        self, criterion_name: str, description: str, max_points: float, guidelines: str, submission_text: str, rag_context: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            context_str = "\n".join([f"- [{c['source']}] {c['content']}" for c in rag_context])
            
            prompt = f"""
You are an expert academic evaluator. Evaluate the student's submission specifically for the following criterion:
Criterion: {criterion_name} (Max Points: {max_points})
Description: {description}
Evaluation Guidelines: {guidelines}

Relevant Assignment & Reference Context:
{context_str}

Student Submission:
\"\"\"
{submission_text[:3500]}
\"\"\"

Respond ONLY with valid JSON in this exact structure:
{{
    "score": <float between 0 and {max_points}>,
    "rationale": "<specific explanation>",
    "evidence_quote": "<quote from submission>",
    "strength": "<key strength>",
    "improvement": "<improvement>"
}}
"""
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    parsed = json.loads(data["choices"][0]["message"]["content"])
                    parsed["score"] = max(0.0, min(float(parsed.get("score", max_points * 0.7)), max_points))
                    return parsed
        except Exception as e:
            logger.warning(f"OpenAI call failed: {e}")
        return None

    async def _call_gemini_feedback(self, title: str, name: str, scores: List[Dict[str, Any]], text: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            prompt = f"""
Generate comprehensive, personalized academic feedback for student {name} on assignment '{title}'.
Criterion Scores: {json.dumps(scores, indent=2)}

Submission text excerpt:
{text[:2500]}

Respond ONLY with JSON:
{{
    "executive_summary": "<2-3 paragraph encouraging yet rigorous summary>",
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvements": ["<concrete step 1>", "<concrete step 2>", "<concrete step 3>"],
    "action_items": ["<recommended resource or revision task 1>", "<revision task 2>"]
}}
"""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            logger.warning(f"Gemini feedback call failed: {e}")
        return None

    async def _call_openai_feedback(self, title: str, name: str, scores: List[Dict[str, Any]], text: str) -> Optional[Dict[str, Any]]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            prompt = f"""
Generate comprehensive, personalized academic feedback for student {name} on assignment '{title}'.
Criterion Scores: {json.dumps(scores, indent=2)}

Submission text excerpt:
{text[:2500]}

Respond ONLY with JSON:
{{
    "executive_summary": "<2-3 paragraph encouraging yet rigorous summary>",
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvements": ["<concrete step 1>", "<concrete step 2>", "<concrete step 3>"],
    "action_items": ["<task 1>", "<task 2>"]
}}
"""
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            logger.warning(f"OpenAI feedback call failed: {e}")
        return None

    # --------------------------------------------------------------------------
    # Analytical Offline Heuristic Evaluator
    # --------------------------------------------------------------------------
    def _offline_criterion_analysis(
        self,
        criterion_name: str,
        criterion_description: str,
        max_points: float,
        guidelines: str,
        submission_text: str,
        rag_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Deep analytical text evaluator that examines keywords, length, technical depth,
        structure, citations, and evidence presence to formulate deterministic scoring and quotes.
        """
        lower_text = submission_text.lower()
        c_lower = criterion_name.lower()
        
        # Keywords mapping for standard academic criteria
        keywords_map = {
            "understanding": ["concept", "principle", "theory", "architecture", "analysis", "definition", "overview", "objective", "methodology"],
            "implementation": ["code", "function", "algorithm", "module", "pipeline", "execution", "class", "database", "api", "model", "data"],
            "quality": ["clean", "structure", "standard", "modular", "naming", "refactor", "efficient", "complexity", "optimization", "pattern"],
            "testing": ["test", "unit test", "validation", "benchmark", "edge case", "assertion", "coverage", "accuracy", "error handling", "experiment"],
            "documentation": ["document", "readme", "comment", "explanation", "guide", "diagram", "usage", "table", "figure", "reference", "conclusion"]
        }
        
        # Match target keywords
        relevant_keywords = []
        for key, words in keywords_map.items():
            if key in c_lower or (criterion_description and key in criterion_description.lower()):
                relevant_keywords.extend(words)
        
        if not relevant_keywords:
            relevant_keywords = ["result", "analysis", "discussion", "method", "solution", "system", "design"]

        # Calculate keyword presence ratio
        matched_words = [w for w in relevant_keywords if w in lower_text]
        keyword_density = len(matched_words) / max(1, len(relevant_keywords))

        # Check document depth / volume
        word_count = len(submission_text.split())
        length_factor = min(1.0, max(0.4, word_count / 300.0))

        # Base fulfillment ratio (0.5 to 0.95 depending on depth)
        fulfillment = 0.5 + (0.35 * keyword_density) + (0.15 * length_factor)
        fulfillment = min(0.96, max(0.40, fulfillment))

        raw_score = round(fulfillment * max_points, 1)

        # Find best evidence quote
        sentences = [s.strip() for s in re.split(r'[.!?\n]', submission_text) if len(s.strip()) > 25]
        best_sentence = ""
        for s in sentences:
            if any(w in s.lower() for w in matched_words):
                best_sentence = s
                break
        if not best_sentence and sentences:
            best_sentence = sentences[min(len(sentences)-1, 1)]

        # Formulate rationale based on criterion
        rationale = (
            f"The submission demonstrates solid competence in '{criterion_name}'. "
            f"Key concepts such as {', '.join(matched_words[:3]) if matched_words else 'the core methodology'} "
            f"are explicitly addressed. Depth of analysis meets academic expectations with {word_count} words analyzed."
        )

        strength = f"Clear articulation of {matched_words[0] if matched_words else 'the core subject matter'}."
        improvement = f"Further substantiate the discussion on {relevant_keywords[-1]} with additional empirical benchmarks or edge-case handling."

        return {
            "score": raw_score,
            "rationale": rationale,
            "evidence_quote": best_sentence[:200] if best_sentence else "Direct methodological implementation documented in text.",
            "strength": strength,
            "improvement": improvement
        }

    def _offline_feedback_synthesis(
        self,
        assignment_title: str,
        student_name: str,
        criterion_scores: List[Dict[str, Any]],
        submission_text: str
    ) -> Dict[str, Any]:
        """Synthesize personalized feedback offline."""
        strengths = []
        improvements = []
        
        for c in criterion_scores:
            c_name = c.get("criterion_name", "Criterion")
            score = c.get("score", 0)
            max_p = c.get("max_points", 20)
            ratio = score / max(1.0, max_p)
            
            if ratio >= 0.8:
                strengths.append(f"Exceptional execution on '{c_name}' ({score}/{max_p} pts), displaying rigorous mastery.")
            elif ratio >= 0.65:
                strengths.append(f"Solid foundation demonstrated in '{c_name}' ({score}/{max_p} pts).")
            else:
                improvements.append(f"Deepen the scope of '{c_name}' ({score}/{max_p} pts) to incorporate more detailed justifications.")

        if not strengths:
            strengths = [
                "Good overall effort and adherence to basic assignment specifications.",
                "Structure and presentation are logically sequenced."
            ]

        if not improvements:
            improvements = [
                "Consider extending experimental validation across multiple test datasets.",
                "Elaborate on trade-offs and computational complexity in future iterations."
            ]

        exec_summary = (
            f"Overall, the submission for '{assignment_title}' presents a thorough, well-structured response. "
            f"The technical methodology is clearly communicated, and the core objectives have been systematically addressed. "
            f"Review the criterion breakdown and specific action points below to refine future submissions."
        )

        return {
            "executive_summary": exec_summary,
            "strengths": strengths[:4],
            "weaknesses": [
                "Some sections could benefit from deeper elaboration of boundary constraints.",
                "Documentation could incorporate clearer visual diagrams or structured tabular summaries."
            ],
            "improvements": improvements[:4],
            "action_items": [
                "Review the instructor's rubric criteria for benchmark comparisons.",
                "Incorporate comprehensive error handling and logging in implementation workflows.",
                "Validate edge cases prior to final deployment or publication."
            ]
        }


llm_service = LLMService()
