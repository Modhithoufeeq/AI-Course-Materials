from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.feedback import PublishedResult
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.evaluation import PublishedResultResponse, EvaluationResponse
from backend.app.api.deps import get_current_user, require_teacher

router = APIRouter()


@router.get("", response_model=List[PublishedResultResponse])
def list_results(
    assignment_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List published results with role-based access control."""
    query = db.query(PublishedResult)

    if current_user.role == UserRole.STUDENT:
        query = query.filter(
            PublishedResult.student_id == current_user.id,
            PublishedResult.is_visible_to_student == True
        )
    elif student_id:
        query = query.filter(PublishedResult.student_id == student_id)

    if assignment_id:
        query = query.filter(PublishedResult.assignment_id == assignment_id)

    results = query.order_by(PublishedResult.published_at.desc()).all()
    return [PublishedResultResponse.model_validate(r) for r in results]


@router.get("/{result_id}", response_model=EvaluationResponse)
def get_result_detail(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full evaluation breakdown of a published result."""
    result = db.query(PublishedResult).filter(PublishedResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Published result not found.")

    if current_user.role == UserRole.STUDENT:
        if result.student_id != current_user.id or not result.is_visible_to_student:
            raise HTTPException(status_code=403, detail="Access denied.")
        
        # Record student view timestamp
        if not result.student_viewed_at:
            result.student_viewed_at = datetime.now(timezone.utc)
            db.commit()

    evaluation = db.query(Evaluation).filter(Evaluation.id == result.evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Underlying evaluation record not found.")

    return EvaluationResponse.model_validate(evaluation)
