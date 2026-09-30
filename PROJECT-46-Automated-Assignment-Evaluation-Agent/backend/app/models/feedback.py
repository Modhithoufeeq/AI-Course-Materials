from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    executive_summary = Column(Text, nullable=False)
    strengths_json = Column(JSON, nullable=False)  # List[str]
    weaknesses_json = Column(JSON, nullable=False)  # List[str]
    improvements_json = Column(JSON, nullable=False)  # List[str]
    action_items_json = Column(JSON, nullable=True)  # List[str]
    
    teacher_custom_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback {self.id}: Evaluation={self.evaluation_id}>"


class PublishedResult(Base):
    __tablename__ = "published_results"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    published_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    final_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    letter_grade = Column(String(5), nullable=True)
    
    is_visible_to_student = Column(Boolean, default=True, nullable=False)
    student_viewed_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="published_result")
    student = relationship("User", back_populates="published_results_received", foreign_keys=[student_id])
    published_by = relationship("User", foreign_keys=[published_by_id])
    assignment = relationship("Assignment")

    def __repr__(self):
        return f"<PublishedResult {self.id}: Assignment={self.assignment_id}, Student={self.student_id}, Score={self.final_score}/{self.max_score}>"
