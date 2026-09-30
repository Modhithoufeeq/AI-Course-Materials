BbmFseXNpc0FnZW50YXRlZCA9IHN1bShjLm1heF9wb2ludHMgZm9yIGMgaW4gcnVicmljLmNyaXRlcmlhKQogICAgICAgIGlzX2JhbGFuY2VkID0gYWJzKGNhbGN1bGF0ZWQgLSBydWJ"""Multi-agent evaluation pipeline.

Mirrors the production architecture: a Rubric Analysis agent, an Evaluation
agent, an Originality agent and a Feedback agent cooperate to score a student
submission deterministically. No external LLM is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from agents.tools import (
    cosine_similarity,
    extract_evidence,
    fmt_pct,
    keyword_coverage,
    sentence_count,
    word_count,
)


# --------------------------------------------------------------------------
# Data models
# --------------------------------------------------------------------------

@dataclass
class Criterion:
    name: str
    description: str
    max_points: float
    keywords: List[str]


@dataclass
class Rubric:
    title: str
    criteria: List[Criterion]
    total_points: float = 0.0

    def __post_init__(self):
        if not self.total_points:
            self.total_points = sum(c.max_points for c in self.criteria)


@dataclass
class Assignment:
    title: str
    prompt: str
    rubric: Rubric


@dataclass
class Submission:
    student_name: str
    text: str


# --------------------------------------------------------------------------
# Agent 1: Rubric Analysis Agent
# --------------------------------------------------------------------------

class RubricAnalysisAgent:
    """Validates a rubric and produces structured analysis targets."""

    def analyze(self, rubric: Rubric) -> Dict:
        if not rubric.criteria:
            raise ValueError("Rubric contains no criteria to evaluate.")
        calculated = sum(c.max_points for c in rubric.criteria)
        is_balanced = abs(calculated - rubric.total_points) < 1e-6
        return {
            "title": rubric.title,
            "criteria_count": len(rubric.criteria),
            "total_points": rubric.total_points,
            "calculated_points": calculated,
            "is_balanced": is_balanced,
            "summary": (
                f"Rubric '{rubric.title}' analyzed: {len(rubric.criteria)} criteria "
                f"totalling {calculated} points. "
                f"{'Balanced (matches target).' if is_balanced else 'Target mismatch.'}"
            ),
        }


# --------------------------------------------------------------------------
# Agent 2: Evaluation Agent (deterministic, rubric-grounded)
# --------------------------------------------------------------------------

class EvaluationAgent:
    def evaluate(self, assignment: Assignment, submission: Submission) -> List[Dict]:
        results = []
        text = submission.text
        words = word_count(text)
        sentences = sentence_count(text)

        for criterion in assignment.rubric.criteria:
            coverage = keyword_coverage(text, criterion.keywords)
            raw = coverage["coverage"] * criterion.max_points

            # Small quality bonus for demonstrable depth (word count).
            depth_bonus = min(0.15 * criterion.max_points, words / 250.0)
            score = min(criterion.max_points, raw + depth_bonus)
            score = round(score, 2)

            matched = coverage["matched"]
            evidence = extract_evidence(text, matched) if matched else (
                "No direct keyword match found; evaluated on overall structure."
            )
            rationale = (
                f"Scored {score:.1f}/{criterion.max_points} for '{criterion.name}'. "
                f"Matched {len(matched)}/{len(criterion.keywords)} rubric keywords "
                f"({coverage['coverage']:.0%} coverage) across {words} words and "
                f"{sentences} sentences."
            )
            strength = f"Clear demonstration of {', '.join(matched[:3]) or 'core concepts'}."
            improvement = (
                f"Go deeper on: {', '.join(coverage['missing'][:2]) or 'edge cases and trade-offs'}."
            )

            results.append({
                "criterion": criterion.name,
                "max_points": criterion.max_points,
                "score": score,
                "coverage": coverage["coverage"],
                "matched_keywords": matched,
                "missing_keywords": coverage["missing"],
                "rationale": rationale,
                "evidence": evidence,
                "strength": strength,
                "improvement": improvement,
            })
        return results
# --------------------------------------------------------------------------
# Agent 3: Originality Agent
# --------------------------------------------------------------------------

class OriginalityAgent:
    """Estimates text originality by comparing against a small reference corpus."""

    def analyze(self, submission: Submission, references: List[str]) -> Dict:
        if not references:
            return {"similarity": 0.0, "status": "No reference corpus provided."}
        scores = [cosine_similarity(submission.text, ref) for ref in references]
        sim = max(scores)
        if sim < 0.20:
            status = "HIGH ORIGINALITY"
        elif sim < 0.45:
            status = "MODERATE SIMILARITY"
        elif sim < 0.70:
            status = "ELEVATED SIMILARITY"
        else:
            status = "POTENTIAL COPY REPLICATION"
        return {"similarity": round(sim, 4), "status": status}


# --------------------------------------------------------------------------
# Agent 4: Feedback Agent
# --------------------------------------------------------------------------

class FeedbackAgent:
    def synthesize(self, assignment: Assignment, submission: Submission,
                   criterion_results: List[Dict]) -> Dict:
        strengths = []
        improvements = []
        for r in criterion_results:
            ratio = r["score"] / max(1.0, r["max_points"])
            label = r["criterion"]
            if ratio >= 0.7:
                strengths.append(f"Strong command of '{label}' ({r['score']:.1f}/{r['max_points']}).")
            else:
                improvements.append(r["improvement"])

        if not strengths:
            strengths = ["Solid overall structure and effort."]
        if not improvements:
            improvements = ["Consider adding benchmarks or comparisons."]

        total = sum(r["score"] for r in criterion_results)
        max_total = sum(r["max_points"] for r in criterion_results)
        percentage = (total / max_total) if max_total else 0.0

        return {
            "executive_summary": (
                f"{submission.student_name} scored {total:.1f}/{max_total:.1f} "
                f"({fmt_pct(percentage)}) on '{assignment.title}'. "
                f"Review the criterion breakdown and action points below."
            ),
            "strengths": strengths[:4],
            "improvements": improvements[:4],
            "action_items": [
                "Address the missing keyword areas noted per criterion.",
                "Add concrete examples and empirical justification.",
                "Revise for clarity and structure before resubmission.",
            ],
        }