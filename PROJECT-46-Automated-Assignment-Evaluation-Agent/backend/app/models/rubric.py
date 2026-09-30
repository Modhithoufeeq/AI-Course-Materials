from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    total_points = Column(Float, default=100.0, nullable=False)
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    assignment = relationship("Assignment", back_populates="rubrics")
    criteria = relationship("RubricCriterion", back_populates="rubric", cascade="all, delete-orphan", order_by="RubricCriterion.order_index")

    def __repr__(self):
        return f"<Rubric {self.id}: {self.title} (Total: {self.total_points})>"


class RubricCriterion(Base):
    __tablename__ = "rubric_criteria"

    id = Column(Integer, primary_key=True, index=True)
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., Understanding, Implementation
    description = Column(Text, nullable=True)
    max_points = Column(Float, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    evaluation_guidelines = Column(Text, nullable=True)  # Detailed standards for high vs low scores

    # Relationships
    rubric = relationship("Rubric", back_populates="criteria")
    criterion_scores = relationship("EvaluationCriterionScore", back_populates="criterion", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Criterion {self.id}: {self.name} (Max: {self.max_points})>"
