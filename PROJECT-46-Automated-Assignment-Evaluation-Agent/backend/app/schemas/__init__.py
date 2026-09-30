from backend.app.schemas.user import (
    UserBase, UserCreate, UserLogin, UserResponse, Token, TokenPayload
)
from backend.app.schemas.rubric import (
    RubricBase, RubricCreate, RubricUpdate, RubricResponse,
    RubricCriterionBase, RubricCriterionCreate, RubricCriterionResponse
)
from backend.app.schemas.assignment import (
    AssignmentBase, AssignmentCreate, AssignmentUpdate, AssignmentResponse, ReferenceDocumentResponse
)
from backend.app.schemas.submission import (
    SubmissionBase, SubmissionResponse, SubmissionListResponse, SubmissionUploadResponse
)
from backend.app.schemas.originality import (
    OriginalityReportResponse, SimilarityMatchItem
)
from backend.app.schemas.evaluation import (
    EvaluationResponse, EvaluationCriterionScoreResponse, AgentDecisionLogResponse,
    FeedbackResponse, PublishedResultResponse, EvaluationReviewRequest, EvaluationApproveRequest,
    CriterionScoreInput
)
from backend.app.schemas.dashboard import (
    TeacherDashboardStats, StudentDashboardStats, ScoreDistributionItem, RecentActivityItem
)

__all__ = [
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "Token", "TokenPayload",
    "RubricBase", "RubricCreate", "RubricUpdate", "RubricResponse",
    "RubricCriterionBase", "RubricCriterionCreate", "RubricCriterionResponse",
    "AssignmentBase", "AssignmentCreate", "AssignmentUpdate", "AssignmentResponse", "ReferenceDocumentResponse",
    "SubmissionBase", "SubmissionResponse", "SubmissionListResponse", "SubmissionUploadResponse",
    "OriginalityReportResponse", "SimilarityMatchItem",
    "EvaluationResponse", "EvaluationCriterionScoreResponse", "AgentDecisionLogResponse",
    "FeedbackResponse", "PublishedResultResponse", "EvaluationReviewRequest", "EvaluationApproveRequest", "CriterionScoreInput",
    "TeacherDashboardStats", "StudentDashboardStats", "ScoreDistributionItem", "RecentActivityItem"
]
