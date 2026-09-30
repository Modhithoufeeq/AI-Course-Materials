"""End-to-end ingestion pipeline: parse → chunk → embed → index → metadata."""

from __future__ import annotations

import logging
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import Settings
from app.core.errors import (
    DependencyUnavailableError,
    UnprocessableContentError,
)
from app.core.ingestion.chunker import split_text
from app.core.ingestion.document_loader import (
    SUPPORTED_EXTENSIONS,
    content_type_for,
    extract_text,
)
from app.core.ingestion.embedder import EmbeddingProvider
from app.core.ingestion.metadata_store import MetadataStore
from app.core.ingestion.vector_store import VectorStoreProvider
from app.schemas.document import DocumentMeta, IngestResult

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates everything needed to make a document searchable."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.metadata = MetadataStore(settings)
        self._vector_store: VectorStoreProvider | None = None
        self._embedder: EmbeddingProvider | None = None

    @property
    def vector_store(self) -> VectorStoreProvider:
        if self._vector_store is None:
            self._vector_store = VectorStoreProvider(self.settings)
        return self._vector_store

    @property
    def embedder(self) -> EmbeddingProvider:
        if self._embedder is None:
            self._embedder = EmbeddingProvider(self.settings)
        return self._embedder

    # ── Public API ───────────────────────────────────────────────────────────

    def ingest_bytes(self, filename: str, content: bytes,
                     content_type: str) -> IngestResult:
        """Ingest an in-memory upload by spooling it to a temp file."""
        suffix = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        try:
            return self._ingest_one(
                tmp_path,
                display_name=filename,
                content_type=content_type or content_type_for(tmp_path),
                source="upload",
            )
        finally:
            tmp_path.unlink(missing_ok=True)

    def ingest_path(self, path: str | Path,
                    *, recursive: bool = False) -> list[IngestResult]:
        """Ingest a file or every supported file under a directory."""
        target = Path(path)
        if target.is_dir():
            iterator = target.rglob("*") if recursive else target.glob("*")
            files = sorted(
                f for f in iterator
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
            )
            if not files:
                logger.warning("No supported documents found under %s", target)
                return []
            return [
                self._ingest_one(f, display_name=f.name,
                                 content_type=content_type_for(f), source=str(f))
                for f in files
            ]
        if target.is_file():
            return [
                self._ingest_one(target, display_name=target.name,
                                 content_type=content_type_for(target),
                                 source=str(target))
            ]
        raise UnprocessableContentError(detail=f"Path does not exist: {target}")

    # ── Internals ────────────────────────────────────────────────────────────

    def _ingest_one(self, path: Path, *, display_name: str,
                    content_type: str, source: str) -> IngestResult:
        self.metadata.init_schema()
        doc_id = f"{datetime.now(UTC):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8]}"

        text = extract_text(path)
        if not text.strip():
            raise UnprocessableContentError(
                detail=f"Document produced no extractable text: {display_name}"
            )

        chunks = split_text(
            text,
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
        )
        if not chunks:  # pragma: no cover — defensive
            raise UnprocessableContentError(
                detail=f"Chunking produced no chunks: {display_name}"
            )

        nodes = self._build_nodes(doc_id, display_name, content_type, source, chunks)

        try:
            self.vector_store.store.add(nodes)
        except DependencyUnavailableError:
            raise
        except Exception as exc:
            raise DependencyUnavailableError(
                detail=f"Failed to write vectors for '{display_name}': {exc}"
            ) from exc

        now = datetime.now(UTC)
        meta = DocumentMeta(
            id=doc_id,
            filename=display_name,
            content_type=content_type,
            char_count=len(text),
            chunk_count=len(chunks),
            status="indexed",
            created_at=now,
            updated_at=now,
            extra={"source": source, "path": str(path)},
        )
        try:
            self.metadata.upsert(meta)
        except Exception:  # noqa: BLE001 — vectors already stored; keep going
            logger.warning("Could not persist metadata for %s", doc_id, exc_info=True)

        logger.info("Ingested %s (%d chunks, %d chars)",
                    display_name, len(chunks), len(text))
        return IngestResult(document=meta, ingested_chunks=len(chunks), source=source)

    def _build_nodes(self, doc_id: str, filename: str, content_type: str,
                     source: str, chunks: list[str]) -> list:
        try:
            from llama_index.core.schema import TextNode
        except ImportError as exc:
            raise DependencyUnavailableError(
                detail="llama-index-core is not installed."
            ) from exc

        nodes = [
            TextNode(
                id_=f"{doc_id}:{idx}",
                ref_doc_id=doc_id,
                text=chunk,
                metadata={
                    "doc_id": doc_id,
                    "filename": filename,
                    "content_type": content_type,
                    "source": source,
                    "chunk_index": idx,
                },
            )
            for idx, chunk in enumerate(chunks)
        ]
        try:
            vectors = self.embedder.embed_batch([n.text for n in nodes])
        except Exception as exc:
            raise DependencyUnavailableError(
                detail=f"Embedding failed (is Ollama running at "
                       f"{self.settings.OLLAMA_BASE_URL}?): {exc}"
            ) from exc
        for node, vector in zip(nodes, vectors, strict=True):
            node.embedding = vector
        return nodes

