"""Query orchestration: basic RAG vs. agentic CrewAI mode, with fallback."""

from __future__ import annotations

import logging
import time

from app.core.agents.orchestrator import AgenticQueryOrchestrator
from app.core.config import Settings
from app.core.errors import AppError
from app.core.ingestion.embedder import EmbeddingProvider
from app.core.ingestion.vector_store import VectorStoreProvider
from app.core.rag.engine import QueryEngine
from app.core.rag.retriever import Retriever
from app.schemas.query import QueryMode, QueryRequest, QueryResponse

logger = logging.getLogger(__name__)


class QueryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._retriever: Retriever | None = None
        self._engine: QueryEngine | None = None

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            self._retriever = Retriever(
                self.settings,
                vector_store=VectorStoreProvider(self.settings),
                embedder=EmbeddingProvider(self.settings),
            )
        return self._retriever

    @property
    def engine(self) -> QueryEngine:
        if self._engine is None:
            self._engine = QueryEngine(self.settings, self.retriever)
        return self._engine

    def answer(self, request: QueryRequest) -> QueryResponse:
        started = time.perf_counter()
        mode = (
            QueryMode.agentic
            if (request.mode is QueryMode.auto and self.settings.AGENTIC_MODE)
            else (QueryMode.basic if request.mode is QueryMode.auto else request.mode)
        )
        error: str | None = None

        try:
            sources = self.engine.retrieve_sources(request.question, request.top_k)

            if not sources:
                answer = (
                    "I could not find any relevant documents for your question. "
                    "Please make sure the knowledge base has been populated "
                    "(POST /api/v1/ingest/upload)."
                )
            elif mode is QueryMode.agentic:
                try:
                    orchestrator = AgenticQueryOrchestrator(
                        self.settings,
                        retriever=self.retriever,
                        temperature=request.temperature,
                    )
                    answer = orchestrator.run(request.question)
                except Exception as exc:  # noqa: BLE001 — degrade, don't fail
                    logger.warning("Agentic pipeline failed; falling back to "
                                   "basic RAG: %s", exc)
                    answer = self.engine.generate_from_sources(
                        request.question, sources, request.temperature
                    )
                    error = f"Agentic pipeline failed ({exc}); served basic RAG answer."
            else:
                answer = self.engine.generate_from_sources(
                    request.question, sources, request.temperature
                )
        except AppError:
            raise
        except Exception as exc:  # noqa: BLE001 — report, don't 500 blindly
            logger.exception("Query failed")
            return self._response(request, f"Query failed: {exc}", mode,
                                  started, sources=[], error=str(exc))

        return self._response(request, answer, mode, started,
                              sources=sources, error=error)

    def _response(self, request: QueryRequest, answer: str, mode: QueryMode,
                  started: float, *, sources, error: str | None) -> QueryResponse:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources,
            mode=mode,
            model=self.settings.OLLAMA_LLM_MODEL,
            latency_ms=latency_ms,
            error=error,
        )
