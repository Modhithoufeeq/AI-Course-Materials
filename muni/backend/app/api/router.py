"""Aggregated v1 API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import documents, health, ingest, query

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
