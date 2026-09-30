from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.models.submission import SubmissionStatus
from backend.app.schemas.user import UserResponse


class SubmissionBase(BaseModel):
    assignment_id: int
    student_id: int


class SubmissionUploadResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    file_name: str
    file_type: str
    file_size_bytes: int
    status: SubmissionStatus
    word_count: int
    character_count: int
    submitted_at: datetime
    extraction_preview: Optional[str] = None

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    file_name: str
    file_path: str
    file_type: str
    file_size_bytes: int
    extracted_text: Optional[str] = None
    word_count: int
    character_count: int
    extraction_error: Optional[str] = None
    status: SubmissionStatus
    submitted_at: datetime
    updated_at: datetime
    student: Optional[UserResponse] = None
    evaluation_id: Optional[int] = None
    total_score: Optional[float] = None
    max_possible_score: Optional[float] = None
    similarity_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    total: int
    items: List[SubmissionResponse]
