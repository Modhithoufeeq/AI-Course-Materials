from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class QueryMode(str, Enum):
    auto = "auto"  # follow AGENTIC_MODE setting
    basic = "basic"  # retrieve → compress → generate
    agentic = "agentic"  # CrewAI multi-agent pipeline


class QueryRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        examples=["What is the remote work policy?"],
    )
    mode: QueryMode = QueryMode.auto
    top_k: int | None = Field(default=None, ge=1, le=20)
    temperature: float | None = Field(default=None, ge=0.0, le=1.5)


class SourceRef(BaseModel):
    """A retrieved passage used to ground the answer."""

    index: int
    document_id: str
    filename: str
    score: float | None = None
    page: int | None = None
    text: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceRef] = Field(default_factory=list)
    mode: QueryMode
    model: str
    latency_ms: int
    error: str | None = None
