"""FastAPI application factory: middleware, lifespan, routers, error handling."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.tracing.phoenix import init_tracing, shutdown_tracing

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state.application_start_time = time.time() 
    settings = get_settings()
    tracer_provider = init_tracing(settings)
    app.state.tracer_provider = tracer_provider

    if settings.AUTO_INGEST_ON_STARTUP and settings.INGEST_DIR:
        from app.api.deps import get_document_service

        logger.info("Auto-ingesting documents from %s", settings.INGEST_DIR)
        try:
            results = get_document_service().ingest_path(
                str(settings.INGEST_DIR), recursive=True
            )
            logger.info("Auto-ingest finished: %d document(s)", len(results))
        except Exception as exc:  # noqa: BLE001 — startup must not crash the app
            logger.warning("Auto-ingest failed: %s", exc, exc_info=True)

    logger.info("%s v%s ready (%s environment)",
                settings.APP_NAME, __version__, settings.ENVIRONMENT)
    yield
    shutdown_tracing(tracer_provider)
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)

    app = FastAPI(titl=e=settings.APP_NAME, version=__version__)

    production = settings.is_production
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        description="Agentic RAG document search platform (Ollama + pgvector)",
        lifespan=lifespan,
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        logger.info("%s %s -> %s (%.1f ms)",
                    request.method, request.url.path,
                    response.status_code, elapsed_ms,
                    extra={"request_id": request_id})
        return response

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
