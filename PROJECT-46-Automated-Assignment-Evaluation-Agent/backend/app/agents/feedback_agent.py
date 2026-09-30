import logging
from typing import List, Dict, Any
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class FeedbackAgent:
    """Agent responsible for synthesizing actionable, encouraging, and personalized academic feedback."""

    async def generate_feedback(
        self,
        assignment_title: str,
        student_name: str,
        criterion_scores: List[Dict[str, Any]],
        submission_text: str,
        similarity_percentage: float = 0.0,
    ) -> Dict[str, Any]:
        """Synthesizes strengths, areas for improvement, and executive summary."""
        logger.info(f"Synthesizing personalized feedback for student '{student_name}' on '{assignment_title}'")
        
        feedback_data = await llm_service.generate_feedback_summary(
            assignment_title=assignment_title,
            student_name=student_name,
            criterion_scores=criterion_scores,
            submission_text=submission_text,
            similarity_percentage=similarity_percentage,
        )

        return feedback_data


feedback_agent = FeedbackAgent()
