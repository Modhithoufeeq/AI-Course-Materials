import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    student_id = Column(String(100), nullable=True, index=True)  # For student ID numbers
    department = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_assignments = relationship("Assignment", back_populates="teacher", foreign_keys="Assignment.teacher_id")
    submissions = relationship("Submission", back_populates="student", foreign_keys="Submission.student_id")
    published_results_received = relationship("PublishedResult", back_populates="student", foreign_keys="PublishedResult.student_id")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
