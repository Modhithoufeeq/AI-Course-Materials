"""FastAPI dependency-injection providers.

These callables are what routes declare as dependencies, which makes them
trivial to override in tests via ``app.dependency_overrides``.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.document_service import DocumentService
from app.services.query_service import QueryService


@lru_cache
def get_document_service() -> DocumentService:
    return DocumentService(get_settings())


@lru_cache
def get_query_service() -> QueryService:
    return QueryService(get_settings())


__all__ = ["Settings", "get_document_service", "get_query_service", "get_settings"]
