from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ScoreDistributionItem(BaseModel):
    grade_range: str  # "90-100% (A)", "80-89% (B)", etc.
    count: int
    percentage: float


class RecentActivityItem(BaseModel):
    id: int
    title: str
    student_name: str
    assignment_title: str
    status: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    timestamp: str


class TeacherDashboardStats(BaseModel):
    total_assignments: int
    total_students: int
    pending_evaluations: int
    under_review_evaluations: int
    completed_evaluations: int
    published_results: int
    average_score_percentage: float
    grade_distribution: List[ScoreDistributionItem]
    recent_submissions: List[RecentActivityItem]


class StudentDashboardStats(BaseModel):
    enrolled_assignments_count: int
    submitted_count: int
    graded_count: int
    published_results_count: int
    student_average_percentage: float
    recent_results: List[Dict[str, Any]]
    pending_assignments: List[Dict[str, Any]]
