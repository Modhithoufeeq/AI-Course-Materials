import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class EvaluationStatus(str, enum.Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    FAILED = "failed"


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Programmatically computed scores
    total_score = Column(Float, nullable=False, default=0.0)
    max_possible_score = Column(Float, nullable=False, default=100.0)
    percentage = Column(Float, nullable=False, default=0.0)
    letter_grade = Column(String(5), nullable=True)  # A+, A, B, C, D, F
    
    # Status and workflow
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.PENDING, nullable=False, index=True)
    evaluation_summary = Column(Text, nullable=True)
    detailed_explanation = Column(Text, nullable=True)
    
    # Teacher Review controls
    teacher_notes = Column(Text, nullable=True)
    teacher_modified_score = Column(Float, nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="evaluation")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    criterion_scores = relationship("EvaluationCriterionScore", back_populates="evaluation", cascade="all, delete-orphan", order_by="EvaluationCriterionScore.id")
    feedback = relationship("Feedback", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")
    decision_logs = relationship("AgentDecisionLog", back_populates="evaluation", cascade="all, delete-orphan", order_by="AgentDecisionLog.created_at")
    published_result = relationship("PublishedResult", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")

    @property
    def originality_report(self):
        """Helper property to access the submission's originality report directly from the evaluation."""
        return self.submission.originality_report if self.submission else None

    def __repr__(self):
        return f"<Evaluation {self.id}: Submission={self.submission_id}, Score={self.total_score}/{self.max_possible_score}, Status={self.status}>"


class EvaluationCriterionScore(Base):
    __tablename__ = "evaluation_criterion_scores"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    criterion_id = Column(Integer, ForeignKey("rubric_criteria.id", ondelete="CASCADE"), nullable=False)
    
    criterion_name = Column(String(255), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    max_points = Column(Float, nullable=False, default=20.0)
    percentage = Column(Float, nullable=False, default=0.0)
    
    rationale = Column(Text, nullable=True)
    evidence_quote = Column(Text, nullable=True)
    teacher_modified_score = Column(Float, nullable=True)
    teacher_comment = Column(Text, nullable=True)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="criterion_scores")
    criterion = relationship("RubricCriterion", back_populates="criterion_scores")

    def __repr__(self):
        return f"<CriterionScore {self.id}: {self.criterion_name} ({self.score}/{self.max_points})>"


class AgentDecisionLog(Base):
    __tablename__ = "agent_decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_name = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # started, completed, warning, failed
    details = Column(Text, nullable=False)
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="decision_logs")

    def __repr__(self):
        return f"<DecisionLog {self.id}: [{self.step_name}] {self.status}>"
