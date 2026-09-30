from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from backend.app.database.session import Base


class OriginalityReport(Base):
    __tablename__ = "originality_reports"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    similarity_percentage = Column(Float, nullable=False, default=0.0)  # e.g., 13.5
    risk_level = Column(String(50), nullable=False, default="low")  # low, medium, high
    status_label = Column(String(100), nullable=False, default="Low Similarity")
    match_summary = Column(Text, nullable=True)
    matched_submission_count = Column(Integer, default=0)
    
    # Detailed match breakdown (sources, snippets, overlap scores)
    matches_json = Column(JSON, nullable=True)
    disclaimer = Column(
        Text,
        default="AI-assisted similarity indicator. This metric represents lexical and semantic overlap with existing course submissions and reference materials. It is not a definitive judgment of plagiarism.",
        nullable=False
    )
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="originality_report")

    def __repr__(self):
        return f"<OriginalityReport {self.id}: {self.similarity_percentage}% ({self.risk_level})>"
