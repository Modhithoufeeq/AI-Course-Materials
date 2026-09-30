from __future__ import annotations

from pydantic import BaseModel


class HealthDeps(BaseModel):
    ollama: bool
    postgres: bool


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    dependencies: HealthDeps
