"""Pytest suite — runs without Ollama/Postgres (heavy deps mocked or lazy)."""

import os

# Must be set before app modules are imported.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("TRACING_ENABLED", "false")
os.environ.setdefault("AUTO_INGEST_ON_STARTUP", "false")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from datetime import UTC, datetime  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import deps  # noqa: E402
from app.core.errors import NotFoundError  # noqa: E402
from app.main import create_app  # noqa: E402
from app.schemas.document import (  # noqa: E402
    DocumentListResponse,
    DocumentMeta,
    IngestResult,
)
from app.schemas.query import QueryMode, QueryResponse  # noqa: E402


class FakeDocumentService:
    """In-memory stand-in for the real service (no DB / Ollama needed)."""

    def __init__(self) -> None:
        self.stored: list[DocumentMeta] = []
        self._counter = 0

    def _meta(self, filename: str, content: bytes) -> DocumentMeta:
        self._counter += 1
        now = datetime.now(UTC)
        return DocumentMeta(
            id=f"doc-{self._counter}",
            filename=filename,
            content_type="text/plain",
            char_count=len(content),
            chunk_count=1,
            status="indexed",
            created_at=now,
            updated_at=now,
            extra={"source": "upload"},
        )

    def ingest_upload(self, filename: str, content: bytes,
                      content_type: str = "") -> IngestResult:
        meta = self._meta(filename, content)
        self.stored.append(meta)
        return IngestResult(document=meta, ingested_chunks=1, source="upload")

    def ingest_path(self, path: str, *, recursive: bool = False) -> list[IngestResult]:
        return []

    def list_documents(self, page: int = 1, page_size: int = 20) -> DocumentListResponse:
        return DocumentListResponse(
            items=self.stored, page=page, page_size=page_size, total=len(self.stored)
        )

    def get_document(self, doc_id: str) -> DocumentMeta:
        for meta in self.stored:
            if meta.id == doc_id:
                return meta
        raise NotFoundError(detail=f"Document '{doc_id}' not found.")

    def delete_document(self, doc_id: str) -> None:
        self.get_document(doc_id)  # 404 when missing
        self.stored = [m for m in self.stored if m.id != doc_id]


class FakeQueryService:
    def answer(self, request) -> QueryResponse:
        return QueryResponse(
            question=request.question,
            answer=f"Fake answer for: {request.question}",
            sources=[],
            mode=QueryMode.basic,
            model="fake-model",
            latency_ms=1,
        )


@pytest.fixture
def fake_document_service() -> FakeDocumentService:
    return FakeDocumentService()


@pytest.fixture
def client(fake_document_service: FakeDocumentService) -> TestClient:
    app = create_app()
    app.dependency_overrides[deps.get_document_service] = lambda: fake_document_service
    app.dependency_overrides[deps.get_query_service] = lambda: FakeQueryService()
    with TestClient(app) as test_client:
        yield test_client
