from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.models.assignment import AssignmentStatus
from backend.app.schemas.rubric import RubricResponse, RubricCriterionCreate
from backend.app.schemas.user import UserResponse


class ReferenceDocumentResponse(BaseModel):
    id: int
    assignment_id: int
    title: str
    file_name: str
    file_type: str
    is_vectorized: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    instructions: str = Field(..., min_length=10)
    max_score: float = 100.0
    due_date: Optional[datetime] = None
    status: AssignmentStatus = AssignmentStatus.ACTIVE


class AssignmentCreate(AssignmentBase):
    rubric_title: Optional[str] = None
    rubric_criteria: Optional[List[RubricCriterionCreate]] = None
    enrolled_student_ids: Optional[List[int]] = None


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: Optional[float] = None
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    enrolled_student_ids: Optional[List[int]] = None


class AssignmentResponse(AssignmentBase):
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime
    teacher: Optional[UserResponse] = None
    rubrics: List[RubricResponse] = []
    reference_documents: List[ReferenceDocumentResponse] = []
    submission_count: Optional[int] = 0
    evaluated_count: Optional[int] = 0

    class Config:
        from_attributes = True
