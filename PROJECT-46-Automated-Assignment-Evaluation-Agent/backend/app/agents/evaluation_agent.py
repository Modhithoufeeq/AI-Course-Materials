import logging
from typing import List, Dict, Any
from backend.app.services.rag_service import rag_service
from backend.app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """Agent responsible for conducting criterion-level evaluation grounded in RAG context."""

    async def evaluate_criteria(
        self,
        assignment_id: int,
        assignment_title: str,
        criteria: List[Dict[str, Any]],
        submission_text: str,
    ) -> List[Dict[str, Any]]:
        """Evaluates each criterion sequentially, retrieving semantic RAG context for grounding."""
        results = []

        for crit in criteria:
            c_name = crit["name"]
            c_desc = crit.get("description", "")
            max_points = crit["max_points"]
            guidelines = crit.get("guidelines", "")

            # 1. Retrieve RAG context specifically relevant to this criterion
            rag_query = f"{assignment_title} {c_name} {c_desc}"
            rag_context = rag_service.query_context(assignment_id=assignment_id, query=rag_query, n_results=3)

            logger.info(f"Evaluating criterion '{c_name}' with {len(rag_context)} RAG context chunks.")

            # 2. Call LLM Service
            eval_result = await llm_service.evaluate_criterion(
                criterion_name=c_name,
                criterion_description=c_desc,
                max_points=max_points,
                evaluation_guidelines=guidelines,
                submission_text=submission_text,
                rag_context=rag_context,
                assignment_title=assignment_title,
            )

            results.append({
                "criterion_id": crit["id"],
                "criterion_name": c_name,
                "max_points": max_points,
                "score": eval_result.get("score", 0.0),
                "rationale": eval_result.get("rationale", f"Evaluated according to standard criteria for {c_name}."),
                "evidence_quote": eval_result.get("evidence_quote", ""),
                "strength": eval_result.get("strength", ""),
                "improvement": eval_result.get("improvement", ""),
            })

        return results


evaluation_agent = EvaluationAgent()
