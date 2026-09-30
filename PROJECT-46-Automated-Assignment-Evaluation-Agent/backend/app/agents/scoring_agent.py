import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class ScoringAgent:
    """
    Deterministic Scoring Engine.
    Enforces that total scores, percentages, and grade bounds are computed
    PROGRAMMATICALLY from criterion scores and NOT invented or hallucinated by LLMs.
    """

    @staticmethod
    def calculate_letter_grade(percentage: float) -> str:
        """Derive standard academic letter grade from percentage."""
        if percentage >= 97.0:
            return "A+"
        elif percentage >= 93.0:
            return "A"
        elif percentage >= 90.0:
            return "A-"
        elif percentage >= 87.0:
            return "B+"
        elif percentage >= 83.0:
            return "B"
        elif percentage >= 80.0:
            return "B-"
        elif percentage >= 77.0:
            return "C+"
        elif percentage >= 70.0:
            return "C"
        elif percentage >= 60.0:
            return "D"
        else:
            return "F"

    def compute_evaluation_score(
        self,
        criterion_evaluations: List[Dict[str, Any]],
        expected_total_points: float = 100.0
    ) -> Dict[str, Any]:
        """
        Computes exact deterministic total score, bounds-checked criterion scores,
        percentage, and letter grade.
        """
        processed_criteria = []
        total_awarded = 0.0
        total_max_points = 0.0

        for item in criterion_evaluations:
            criterion_id = item.get("criterion_id")
            criterion_name = item.get("criterion_name", "Criterion")
            max_points = float(item.get("max_points", 20.0))
            raw_score = float(item.get("score", 0.0))

            # Strictly enforce non-negative and max bound
            bounded_score = round(max(0.0, min(raw_score, max_points)), 1)
            criterion_percentage = round((bounded_score / max_points * 100.0) if max_points > 0 else 0.0, 1)

            total_awarded += bounded_score
            total_max_points += max_points

            processed_criteria.append({
                "criterion_id": criterion_id,
                "criterion_name": criterion_name,
                "score": bounded_score,
                "max_points": max_points,
                "percentage": criterion_percentage,
                "rationale": item.get("rationale", ""),
                "evidence_quote": item.get("evidence_quote", ""),
                "strength": item.get("strength", ""),
                "improvement": item.get("improvement", ""),
            })

        # Calculate final total and overall percentage
        total_awarded = round(total_awarded, 1)
        max_possible = round(total_max_points if total_max_points > 0 else expected_total_points, 1)
        overall_percentage = round((total_awarded / max_possible * 100.0) if max_possible > 0 else 0.0, 1)
        letter_grade = self.calculate_letter_grade(overall_percentage)

        logger.info(
            f"Deterministic Scoring: Awarded {total_awarded}/{max_possible} ({overall_percentage}%, Grade: {letter_grade}) across {len(processed_criteria)} criteria."
        )

        return {
            "total_score": total_awarded,
            "max_possible_score": max_possible,
            "percentage": overall_percentage,
            "letter_grade": letter_grade,
            "criterion_scores": processed_criteria,
        }


scoring_agent = ScoringAgent()
