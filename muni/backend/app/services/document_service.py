"""Document lifecycle: ingest, list, get, delete."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.errors import NotFoundError, UnprocessableContentError
from app.core.ingestion.pipeline import IngestionPipeline
from app.schemas.document import DocumentListResponse, DocumentMeta, IngestResult

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pipeline: IngestionPipeline | None = None

    @property
    def pipeline(self) -> IngestionPipeline:
        if self._pipeline is None:
            self._pipeline = IngestionPipeline(self.settings)
        return self._pipeline

    # ── Ingestion ────────────────────────────────────────────────────────────

    def ingest_upload(self, filename: str, content: bytes,
                      content_type: str = "") -> IngestResult:
        max_bytes = self.settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise UnprocessableContentError(
                detail=f"File exceeds the {self.settings.MAX_FILE_SIZE_MB} MB limit."
            )
        return self.pipeline.ingest_bytes(filename, content, content_type)

    def ingest_path(self, path: str, *, recursive: bool = False) -> list[IngestResult]:
        return self.pipeline.ingest_path(path, recursive=recursive)

    # ── Queries ──────────────────────────────────────────────────────────────

    def list_documents(self, page: int = 1, page_size: int = 20) -> DocumentListResponse:
        items, total = self.pipeline.metadata.list(page=page, page_size=page_size)
        return DocumentListResponse(
            items=items, page=page, page_size=page_size, total=total
        )

    def get_document(self, doc_id: str) -> DocumentMeta:
        meta = self.pipeline.metadata.get(doc_id)
        if meta is None:
            raise NotFoundError(detail=f"Document '{doc_id}' not found.")
        return meta

    # ── Deletion ─────────────────────────────────────────────────────────────

    def delete_document(self, doc_id: str) -> None:
        if self.pipeline.metadata.get(doc_id) is None:
            raise NotFoundError(detail=f"Document '{doc_id}' not found.")
        try:
            self.pipeline.vector_store.store.delete(ref_doc_id=doc_id)
        except Exception:  # noqa: BLE001 — metadata deletion still proceeds
            logger.warning("Could not delete vectors for %s", doc_id, exc_info=True)
        self.pipeline.metadata.delete(doc_id)
        logger.info("Deleted document %s", doc_id)
