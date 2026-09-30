from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

DocumentStatus = Literal["indexed", "processing", "failed", "deleted"]


class DocumentMeta(BaseModel):
    """Metadata row for an indexed document."""

    id: str
    filename: str
    content_type: str = "application/octet-stream"
    char_count: int = 0
    chunk_count: int = 0
    status: DocumentStatus = "indexed"
    created_at: datetime
    updated_at: datetime
    extra: dict[str, Any] = Field(default_factory=dict)


class DocumentListResponse(BaseModel):
    items: list[DocumentMeta]
    page: int
    page_size: int
    total: int


class IngestResult(BaseModel):
    """Outcome of a single document ingestion."""

    document: DocumentMeta
    ingested_chunks: int
    source: str = ""
