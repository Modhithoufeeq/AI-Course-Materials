from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from backend.app.models.evaluation import EvaluationStatus
from backend.app.schemas.originality import OriginalityReportResponse
from backend.app.schemas.user import UserResponse


class CriterionScoreInput(BaseModel):
    criterion_id: int
    score: float = Field(..., ge=0)
    teacher_comment: Optional[str] = None


class EvaluationCriterionScoreResponse(BaseModel):
    id: int
    evaluation_id: int
    criterion_id: int
    criterion_name: str
    score: float
    max_points: float
    percentage: float
    rationale: Optional[str] = None
    evidence_quote: Optional[str] = None
    teacher_modified_score: Optional[float] = None
    teacher_comment: Optional[str] = None

    class Config:
        from_attributes = True


class AgentDecisionLogResponse(BaseModel):
    id: int
    evaluation_id: int
    step_name: str
    agent_name: str
    status: str
    details: str
    execution_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    id: int
    evaluation_id: int
    executive_summary: str
    strengths_json: List[str]
    weaknesses_json: List[str]
    improvements_json: List[str]
    action_items_json: Optional[List[str]] = None
    teacher_custom_feedback: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PublishedResultResponse(BaseModel):
    id: int
    evaluation_id: int
    assignment_id: int
    student_id: int
    final_score: float
    max_score: float
    percentage: float
    letter_grade: Optional[str] = None
    is_visible_to_student: bool
    student_viewed_at: Optional[datetime] = None
    published_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    submission_id: int
    total_score: float
    max_possible_score: float
    percentage: float
    letter_grade: Optional[str] = None
    status: EvaluationStatus
    evaluation_summary: Optional[str] = None
    detailed_explanation: Optional[str] = None
    teacher_notes: Optional[str] = None
    teacher_modified_score: Optional[float] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Nested details
    criterion_scores: List[EvaluationCriterionScoreResponse] = []
    feedback: Optional[FeedbackResponse] = None
    originality_report: Optional[OriginalityReportResponse] = None
    decision_logs: List[AgentDecisionLogResponse] = []
    published_result: Optional[PublishedResultResponse] = None

    class Config:
        from_attributes = True


class EvaluationReviewRequest(BaseModel):
    criterion_scores: Optional[List[CriterionScoreInput]] = None
    teacher_notes: Optional[str] = None
    teacher_custom_feedback: Optional[str] = None
    approve: bool = False
    publish_now: bool = False


class EvaluationApproveRequest(BaseModel):
    teacher_notes: Optional[str] = None
    teacher_custom_feedback: Optional[str] = None
    publish_to_student: bool = True
