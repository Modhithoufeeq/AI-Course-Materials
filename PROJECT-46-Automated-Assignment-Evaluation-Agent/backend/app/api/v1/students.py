from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserResponse, UserCreate
from backend.app.core.security import get_password_hash
from backend.app.api.deps import require_teacher

router = APIRouter()


@router.get("", response_model=List[UserResponse])
def list_students(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """List all registered student profiles in the institution."""
    students = db.query(User).filter(User.role == UserRole.STUDENT).order_by(User.full_name.asc()).all()
    return [UserResponse.model_validate(s) for s in students]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: UserCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    """Add a student to the roster."""
    existing = db.query(User).filter(User.email == student_in.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    student = User(
        email=student_in.email.lower(),
        hashed_password=get_password_hash(student_in.password),
        full_name=student_in.full_name,
        role=UserRole.STUDENT,
        student_id=student_in.student_id,
        department=student_in.department,
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return UserResponse.model_validate(student)
