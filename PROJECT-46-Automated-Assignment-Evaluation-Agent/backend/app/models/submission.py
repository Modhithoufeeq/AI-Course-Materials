import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    FAILED = "failed"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size_bytes = Column(BigInteger, default=0)
    
    extracted_text = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    extraction_error = Column(Text, nullable=True)
    
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False, index=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions", foreign_keys=[student_id])
    evaluation = relationship("Evaluation", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    originality_report = relationship("OriginalityReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Submission {self.id}: Assignment={self.assignment_id}, Student={self.student_id}, Status={self.status}>"
