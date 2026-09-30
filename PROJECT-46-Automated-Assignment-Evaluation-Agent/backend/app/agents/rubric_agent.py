import logging
from typing import List, Dict, Any, Optional
from backend.app.models.rubric import Rubric, RubricCriterion

logger = logging.getLogger(__name__)


class RubricAnalysisAgent:
    """Agent responsible for analyzing, parsing, and validating rubric criteria and standards."""

    def analyze_rubric(self, rubric: Rubric) -> Dict[str, Any]:
        """
        Validates rubric criteria distribution, checks for consistency,
        and generates structured evaluation targets.
        """
        if not rubric.criteria or len(rubric.criteria) == 0:
            raise ValueError("Rubric contains no criteria to evaluate.")

        criteria_list = []
        calculated_total = 0.0

        for crit in rubric.criteria:
            calculated_total += crit.max_points
            criteria_list.append({
                "id": crit.id,
                "name": crit.name,
                "description": crit.description or f"Evaluation of {crit.name}",
                "max_points": crit.max_points,
                "weight": crit.weight,
                "order_index": crit.order_index,
                "guidelines": crit.evaluation_guidelines or (
                    f"Evaluate depth, technical precision, clarity, and completeness of {crit.name}. "
                    f"Award up to {crit.max_points} points based on substantiated evidence."
                )
            })

        is_balanced = abs(calculated_total - rubric.total_points) < 0.01

        summary = (
            f"Rubric '{rubric.title}' analyzed: {len(criteria_list)} criteria totaling {calculated_total} points. "
            f"Status: {'Balanced (matches target total)' if is_balanced else f'Target total is {rubric.total_points}'}."
        )

        return {
            "rubric_id": rubric.id,
            "title": rubric.title,
            "target_total_points": rubric.total_points,
            "calculated_total_points": calculated_total,
            "criteria_count": len(criteria_list),
            "is_balanced": is_balanced,
            "criteria": criteria_list,
            "analysis_summary": summary
        }

    def generate_guidelines_text(self, rubric: Rubric) -> str:
        """Serializes rubric into text for RAG indexing."""
        lines = [f"Rubric: {rubric.title} (Total Points: {rubric.total_points})"]
        for c in rubric.criteria:
            lines.append(f"- Criterion: {c.name} | Max Points: {c.max_points} | Details: {c.description or ''} | Guidelines: {c.evaluation_guidelines or ''}")
        return "\n".join(lines)


rubric_agent = RubricAnalysisAgent()
