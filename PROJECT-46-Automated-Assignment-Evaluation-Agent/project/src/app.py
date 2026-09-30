"""Application wiring for the end-to-end evaluation pipeline."""

from __future__ import annotations

from typing import Dict, List

from agents.agent import (
    Assignment,
    Criterion,
    EvaluationAgent,
    FeedbackAgent,
    OriginalityAgent,
    Rubric,
    RubricAnalysisAgent,
    Submission,
)
from config.config import settings
from src.utils import build_text_report, grade_for


def build_default_assignment() -> Assignment:
    rubric = Rubric(
        title="Scientific Writing & Methodology",
        criteria=[
            Criterion(
                name="Clarity of Writing",
                description="Logical flow, grammar and readability.",
                max_points=20,
                keywords=["clear", "structure", "concise", "organized", "flow"],
            ),
            Criterion(
                name="Originality",
                description="Independent thinking and genuine contribution.",
                max_points=20,
                keywords=["independent", "insight", "contribution", "novel", "own"],
            ),
            Criterion(
                name="Argument Depth",
                description="Depth of analysis and critical evaluation.",
                max_points=30,
                keywords=["analysis", "evidence", "argument", "critical", "evaluate"],
            ),
            Criterion(
                name="Referencing",
                description="Proper citation and use of supporting sources.",
                max_points=15,
                keywords=["cite", "source", "reference", "bibliography", "literature"],
            ),
            Criterion(
                name="Technical Accuracy",
                description="Technical correctness and domain expertise.",
                max_points=15,
                keywords=["technical", "accurate", "methodology", "expertise", "link"],
            ),
        ],
    )

    return Assignment(
        title="Individual Research Essay on Multi-Agent Systems",
        prompt=(
            "Write a 800-1200 word essay on the architecture and societal impact "
            "of multi-agent systems in automated evaluation."
        ),
        rubric=rubric,
    )


SAMPLE_REFERENCE = (
    "Modern multi-agent systems coordinate specialized independent agents that "
    "each contribute expert analysis towards a shared automated evaluation "
    "objective, using evidence-based reasoning."
)


def run_pipeline(assignment: Assignment, submission: Submission) -> Dict:
    rubric_agent = RubricAnalysisAgent()
    evaluation_agent = EvaluationAgent()
    originality_agent = OriginalityAgent()
    feedback_agent = FeedbackAgent()

    rubric_report = rubric_agent.analyze(assignment.rubric)
    criterion_results: List[Dict] = evaluation_agent.evaluate(assignment, submission)
    originality = originality_agent.analyze(submission, [SAMPLE_REFERENCE])
    feedback = feedback_agent.synthesize(assignment, submission, criterion_results)

    total = sum(c["score"] for c in criterion_results)
    max_total = sum(c["max_points"] for c in criterion_results)
    percentage = (total / max_total) if max_total else 0.0

    return {
        "assignment_title": assignment.title,
        "student_name": submission.student_name,
        "pipeline": f"{settings.describe()}; rubric balanced={rubric_report['is_balanced']}",
        "criteria": criterion_results,
        "originality": originality,
        "feedback": feedback,
        "total_score": round(total, 2),
        "max_score": float(max_total) if max_total else 0.0,
        "percentage": round(percentage, 4),
        "grade": grade_for(percentage),
    }


def render(payload: Dict) -> str:
    return build_text_report(payload)