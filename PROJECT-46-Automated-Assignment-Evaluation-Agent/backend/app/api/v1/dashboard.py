from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.assignment import Assignment, AssignmentStatus
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.evaluation import Evaluation, EvaluationStatus
from backend.app.models.feedback import PublishedResult
from backend.app.schemas.dashboard import (
    TeacherDashboardStats, StudentDashboardStats, ScoreDistributionItem, RecentActivityItem
)
from backend.app.api.deps import require_teacher, require_student, get_current_user

router = APIRouter()


@router.get("/teacher", response_model=TeacherDashboardStats)
def get_teacher_dashboard(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Aggregate KPI metrics, pending review queues, and score distributions for the Teacher Dashboard."""
    assignments = db.query(Assignment).filter(Assignment.teacher_id == teacher.id).all()
    assign_ids = [a.id for a in assignments]

    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()

    if not assign_ids:
        return TeacherDashboardStats(
            total_assignments=0,
            total_students=total_students,
            pending_evaluations=0,
            under_review_evaluations=0,
            completed_evaluations=0,
            published_results=0,
            average_score_percentage=0.0,
            grade_distribution=[
                ScoreDistributionItem(grade_range="A (90-100%)", count=0, percentage=0.0),
                ScoreDistributionItem(grade_range="B (80-89%)", count=0, percentage=0.0),
                ScoreDistributionItem(grade_range="C (70-79%)", count=0, percentage=0.0),
                ScoreDistributionItem(grade_range="D (60-69%)", count=0, percentage=0.0),
                ScoreDistributionItem(grade_range="F (<60%)", count=0, percentage=0.0),
            ],
            recent_submissions=[]
        )

    submissions = db.query(Submission).filter(Submission.assignment_id.in_(assign_ids)).all()
    sub_ids = [s.id for s in submissions]

    evaluations = db.query(Evaluation).filter(Evaluation.submission_id.in_(sub_ids)).all() if sub_ids else []
    published = db.query(PublishedResult).filter(PublishedResult.assignment_id.in_(assign_ids)).all()

    pending_evals = len([s for s in submissions if s.status in (SubmissionStatus.PENDING, SubmissionStatus.EXTRACTED, SubmissionStatus.PROCESSING)])
    under_review = len([e for e in evaluations if e.status == EvaluationStatus.UNDER_REVIEW])
    completed = len([e for e in evaluations if e.status in (EvaluationStatus.APPROVED, EvaluationStatus.PUBLISHED)])
    published_count = len(published)

    # Average score
    scores = [e.percentage for e in evaluations if e.percentage > 0]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Grade distribution
    a_cnt = len([s for s in scores if s >= 90])
    b_cnt = len([s for s in scores if 80 <= s < 90])
    c_cnt = len([s for s in scores if 70 <= s < 80])
    d_cnt = len([s for s in scores if 60 <= s < 70])
    f_cnt = len([s for s in scores if s < 60])
    tot_evals = max(1, len(scores))

    grade_dist = [
        ScoreDistributionItem(grade_range="A (90-100%)", count=a_cnt, percentage=round(a_cnt / tot_evals * 100, 1)),
        ScoreDistributionItem(grade_range="B (80-89%)", count=b_cnt, percentage=round(b_cnt / tot_evals * 100, 1)),
        ScoreDistributionItem(grade_range="C (70-79%)", count=c_cnt, percentage=round(c_cnt / tot_evals * 100, 1)),
        ScoreDistributionItem(grade_range="D (60-69%)", count=d_cnt, percentage=round(d_cnt / tot_evals * 100, 1)),
        ScoreDistributionItem(grade_range="F (<60%)", count=f_cnt, percentage=round(f_cnt / tot_evals * 100, 1)),
    ]

    # Recent submissions
    recent_subs = (
        db.query(Submission)
        .filter(Submission.assignment_id.in_(assign_ids))
        .order_by(Submission.submitted_at.desc())
        .limit(6)
        .all()
    )

    recent_activity = []
    for r in recent_subs:
        recent_activity.append(RecentActivityItem(
            id=r.id,
            title=r.file_name,
            student_name=r.student.full_name if r.student else f"Student #{r.student_id}",
            assignment_title=r.assignment.title if r.assignment else "Assignment",
            status=r.status.value,
            score=r.evaluation.total_score if r.evaluation else None,
            max_score=r.evaluation.max_possible_score if r.evaluation else None,
            timestamp=r.submitted_at.strftime("%b %d, %H:%M")
        ))

    return TeacherDashboardStats(
        total_assignments=len(assignments),
        total_students=total_students,
        pending_evaluations=pending_evals,
        under_review_evaluations=under_review,
        completed_evaluations=completed,
        published_results=published_count,
        average_score_percentage=avg_score,
        grade_distribution=grade_dist,
        recent_submissions=recent_activity
    )


@router.get("/student", response_model=StudentDashboardStats)
def get_student_dashboard(
    db: Session = Depends(get_db),
    student: User = Depends(require_student)
):
    """Aggregate KPIs, pending submissions, and published results for Student Dashboard."""
    enrolled_assignments = (
        db.query(Assignment)
        .filter(
            (Assignment.enrolled_students.any(User.id == student.id)) |
            (Assignment.status == AssignmentStatus.ACTIVE)
        )
        .all()
    )

    my_submissions = db.query(Submission).filter(Submission.student_id == student.id).all()
    submitted_assignment_ids = {s.assignment_id for s in my_submissions}

    published_results = (
        db.query(PublishedResult)
        .filter(
            PublishedResult.student_id == student.id,
            PublishedResult.is_visible_to_student == True
        )
        .order_by(PublishedResult.published_at.desc())
        .all()
    )

    scores = [p.percentage for p in published_results]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    recent_results_data = []
    for p in published_results[:5]:
        recent_results_data.append({
            "id": p.id,
            "assignment_id": p.assignment_id,
            "assignment_title": p.assignment.title if p.assignment else "Assignment",
            "score": p.final_score,
            "max_score": p.max_score,
            "percentage": p.percentage,
            "letter_grade": p.letter_grade,
            "published_at": p.published_at.strftime("%b %d, %Y")
        })

    pending_assignments_data = []
    for a in enrolled_assignments:
        if a.id not in submitted_assignment_ids:
            pending_assignments_data.append({
                "id": a.id,
                "title": a.title,
                "code": a.code,
                "due_date": a.due_date.strftime("%b %d, %Y") if a.due_date else "No due date",
                "max_score": a.max_score,
                "status": "not_submitted"
            })

    return StudentDashboardStats(
        enrolled_assignments_count=len(enrolled_assignments),
        submitted_count=len(my_submissions),
        graded_count=len(published_results),
        published_results_count=len(published_results),
        student_average_percentage=avg_score,
        recent_results=recent_results_data,
        pending_assignments=pending_assignments_data[:5]
    )
