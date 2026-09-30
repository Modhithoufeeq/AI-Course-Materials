from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class SimilarityMatchItem(BaseModel):
    source_type: str  # "peer_submission" or "reference_document"
    source_title: str
    student_name: Optional[str] = None
    similarity_score: float  # 0.0 - 1.0
    similarity_percentage: float  # 0 - 100
    overlap_snippet: Optional[str] = None
    matched_ranges: Optional[List[Dict[str, Any]]] = None


class OriginalityReportResponse(BaseModel):
    id: int
    submission_id: int
    similarity_percentage: float
    risk_level: str  # low, medium, high
    status_label: str
    match_summary: Optional[str] = None
    matched_submission_count: int = 0
    matches_json: Optional[List[Dict[str, Any]]] = None
    disclaimer: str
    created_at: datetime

    class Config:
        from_attributes = True
