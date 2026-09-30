from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RubricCriterionBase(BaseModel):
    name: str = Field(..., description="Name of the criterion, e.g., Understanding, Implementation")
    description: Optional[str] = None
    max_points: float = Field(..., gt=0, description="Max points for this criterion")
    weight: float = Field(1.0, gt=0)
    order_index: int = 0
    evaluation_guidelines: Optional[str] = None


class RubricCriterionCreate(RubricCriterionBase):
    pass


class RubricCriterionResponse(RubricCriterionBase):
    id: int
    rubric_id: int

    class Config:
        from_attributes = True


class RubricBase(BaseModel):
    title: str
    description: Optional[str] = None
    total_points: float = 100.0
    is_template: bool = False


class RubricCreate(RubricBase):
    assignment_id: Optional[int] = None
    criteria: List[RubricCriterionCreate]


class RubricUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_points: Optional[float] = None
    criteria: Optional[List[RubricCriterionCreate]] = None


class RubricResponse(RubricBase):
    id: int
    assignment_id: int
    created_at: datetime
    updated_at: datetime
    criteria: List[RubricCriterionResponse] = []

    class Config:
        from_attributes = True
