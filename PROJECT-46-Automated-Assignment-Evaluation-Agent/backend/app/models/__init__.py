from backend.app.database.session import Base
from backend.app.models.user import User, UserRole
from backend.app.models.assignment import Assignment, AssignmentStatus, ReferenceDocument, assignment_students
from backend.app.models.rubric import Rubric, RubricCriterion
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.evaluation import Evaluation, EvaluationStatus, EvaluationCriterionScore, AgentDecisionLog
from backend.app.models.originality import OriginalityReport
from backend.app.models.feedback import Feedback, PublishedResult

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Assignment",
    "AssignmentStatus",
    "ReferenceDocument",
    "assignment_students",
    "Rubric",
    "RubricCriterion",
    "Submission",
    "SubmissionStatus",
    "Evaluation",
    "EvaluationStatus",
    "EvaluationCriterionScore",
    "AgentDecisionLog",
    "OriginalityReport",
    "Feedback",
    "PublishedResult",
]
