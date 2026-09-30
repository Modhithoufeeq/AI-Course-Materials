from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    detail: str
    fields: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    """Envelope returned by every error path in the API."""

    error: ErrorBody


class MessageResponse(BaseModel):
    message: str
