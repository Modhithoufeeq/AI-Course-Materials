from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, status

from app import __version__
from app.api.deps import get_settings
from app.core.config import Settings
from app.core.ingestion.metadata_store import MetadataStore
from app.schemas.health import HealthDeps, HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _ollama_reachable(settings: Settings, timeout: float = 3.0) -> bool:
    try:
        response = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=timeout)
        return response.status_code == status.HTTP_200_OK
    except httpx.HTTPError:
        return False


def _postgres_reachable(settings: Settings) -> bool:
    return MetadataStore(settings).health()


@router.get("/health/live", summary="Liveness probe (always cheap & 200 if running)")
def liveness() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=__version__,
        environment=settings.ENVIRONMENT,
        dependencies=HealthDeps(ollama=False, postgres=False),
    )


@router.get("/health/ready", summary="Readiness probe (503 until deps are up)")
def readiness() -> HealthResponse:
    settings = get_settings()
    ollama_ok = _ollama_reachable(settings)
    postgres_ok = _postgres_reachable(settings)
    if not (ollama_ok and postgres_ok):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ollama": ollama_ok, "postgres": postgres_ok},
        )
    return HealthResponse(
        status="ready",
        version=__version__,
        environment=settings.ENVIRONMENT,
        dependencies=HealthDeps(ollama=ollama_ok, postgres=postgres_ok),
    )


@router.get("/health", summary="Dependency status overview (always 200)")
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=__version__,
        environment=settings.ENVIRONMENT,
        dependencies=HealthDeps(
            ollama=_ollama_reachable(settings),
            postgres=_postgres_reachable(settings),
        ),
    )
