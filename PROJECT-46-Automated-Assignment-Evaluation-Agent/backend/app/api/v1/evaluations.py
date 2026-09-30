from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.evaluation import Evaluation, EvaluationStatus, EvaluationCriterionScore, AgentDecisionLog
from backend.app.models.feedback import Feedback, PublishedResult
from backend.app.schemas.evaluation import (
    EvaluationResponse, EvaluationReviewRequest, EvaluationApproveRequest
)
from backend.app.api.deps import get_current_user, require_teacher
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.scoring_agent import scoring_agent

router = APIRouter()


@router.post("/{submission_id}/start", response_model=EvaluationResponse)
async def start_evaluation(
    submission_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """
    Start the Agentic AI Evaluation pipeline for a submission.
    Runs extraction, rubric analysis, RAG retrieval, criterion scoring,
    originality analysis, deterministic scoring, and feedback synthesis.
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    try:
        evaluation = await orchestrator.run_evaluation_pipeline(
            db=db,
            submission_id=submission_id,
            triggered_by_user_id=teacher.id
        )
        return EvaluationResponse.model_validate(evaluation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation pipeline failed: {str(e)}"
        )


@router.post("/{submission_id}/reevaluate", response_model=EvaluationResponse)
async def reevaluate_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Trigger re-evaluation of a submission."""
    return await start_evaluation(submission_id=submission_id, db=db, teacher=teacher)


@router.get("/{submission_id}", response_model=EvaluationResponse)
def get_evaluation(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full evaluation details, criterion scores, originality report, and decision logs."""
    evaluation = db.query(Evaluation).filter(Evaluation.submission_id == submission_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation record not found for this submission.")

    # Authorization guard: Student can only view if published or authorized
    if current_user.role == UserRole.STUDENT:
        if evaluation.submission.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied.")
        if evaluation.status != EvaluationStatus.PUBLISHED:
            raise HTTPException(status_code=403, detail="Evaluation results are currently under teacher review.")

    return EvaluationResponse.model_validate(evaluation)


@router.put("/{evaluation_id}/review", response_model=EvaluationResponse)
def review_evaluation(
    evaluation_id: int,
    review_in: EvaluationReviewRequest,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """
    Teacher review endpoint: Allows modifying individual criterion scores,
    updating teacher notes, adjusting feedback, and optionally approving/publishing.
    """
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    # 1. Update criterion scores if provided
    if review_in.criterion_scores:
        total_recomputed = 0.0
        for item in review_in.criterion_scores:
            c_score = db.query(EvaluationCriterionScore).filter(
                EvaluationCriterionScore.evaluation_id == evaluation.id,
                EvaluationCriterionScore.criterion_id == item.criterion_id
            ).first()
            if c_score:
                bounded = max(0.0, min(item.score, c_score.max_points))
                c_score.teacher_modified_score = bounded
                c_score.score = bounded
                c_score.percentage = round((bounded / c_score.max_points * 100.0) if c_score.max_points > 0 else 0.0, 1)
                if item.teacher_comment is not None:
                    c_score.teacher_comment = item.teacher_comment
                total_recomputed += bounded
            
        # Deterministic recomputation of total
        evaluation.total_score = round(total_recomputed, 1)
        evaluation.percentage = round((total_recomputed / evaluation.max_possible_score * 100.0) if evaluation.max_possible_score > 0 else 0.0, 1)
        evaluation.letter_grade = scoring_agent.calculate_letter_grade(evaluation.percentage)

    # 2. Update teacher notes
    if review_in.teacher_notes is not None:
        evaluation.teacher_notes = review_in.teacher_notes

    # 3. Update feedback custom notes
    if review_in.teacher_custom_feedback is not None and evaluation.feedback:
        evaluation.feedback.teacher_custom_feedback = review_in.teacher_custom_feedback

    evaluation.reviewed_by_id = teacher.id
    evaluation.reviewed_at = datetime.now(timezone.utc)

    # 4. Handle approve / publish
    if review_in.approve or review_in.publish_now:
        evaluation.status = EvaluationStatus.APPROVED if not review_in.publish_now else EvaluationStatus.PUBLISHED
        evaluation.submission.status = SubmissionStatus.APPROVED if not review_in.publish_now else SubmissionStatus.PUBLISHED
        
        if review_in.publish_now:
            _publish_result_internal(db, evaluation, teacher.id)

    db.commit()
    db.refresh(evaluation)
    return EvaluationResponse.model_validate(evaluation)


@router.post("/{evaluation_id}/approve", response_model=EvaluationResponse)
def approve_evaluation(
    evaluation_id: int,
    approve_in: EvaluationApproveRequest,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Teacher approves the evaluation and optionally publishes the result to the student."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    if approve_in.teacher_notes:
        evaluation.teacher_notes = approve_in.teacher_notes
    if approve_in.teacher_custom_feedback and evaluation.feedback:
        evaluation.feedback.teacher_custom_feedback = approve_in.teacher_custom_feedback

    evaluation.reviewed_by_id = teacher.id
    evaluation.reviewed_at = datetime.now(timezone.utc)

    if approve_in.publish_to_student:
        evaluation.status = EvaluationStatus.PUBLISHED
        evaluation.submission.status = SubmissionStatus.PUBLISHED
        _publish_result_internal(db, evaluation, teacher.id)
    else:
        evaluation.status = EvaluationStatus.APPROVED
        evaluation.submission.status = SubmissionStatus.APPROVED

    db.commit()
    db.refresh(evaluation)
    return EvaluationResponse.model_validate(evaluation)


def _publish_result_internal(db: Session, evaluation: Evaluation, teacher_id: int):
    """Helper to upsert PublishedResult record."""
    pub_result = db.query(PublishedResult).filter(PublishedResult.evaluation_id == evaluation.id).first()
    if not pub_result:
        pub_result = PublishedResult(
            evaluation_id=evaluation.id,
            assignment_id=evaluation.submission.assignment_id,
            student_id=evaluation.submission.student_id,
            published_by_id=teacher_id,
            final_score=evaluation.total_score,
            max_score=evaluation.max_possible_score,
            percentage=evaluation.percentage,
            letter_grade=evaluation.letter_grade,
            is_visible_to_student=True,
            published_at=datetime.now(timezone.utc)
        )
        db.add(pub_result)
    else:
        pub_result.final_score = evaluation.total_score
        pub_result.max_score = evaluation.max_possible_score
        pub_result.percentage = evaluation.percentage
        pub_result.letter_grade = evaluation.letter_grade
        pub_result.is_visible_to_student = True
        pub_result.published_at = datetime.now(timezone.utc)
