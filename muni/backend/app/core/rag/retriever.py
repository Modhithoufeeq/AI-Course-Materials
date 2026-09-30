"""Vector retriever — embeds the query and pulls the top-k passages."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.errors import DependencyUnavailableError
from app.core.ingestion.embedder import EmbeddingProvider
from app.core.ingestion.vector_store import VectorStoreProvider
from app.schemas.query import SourceRef

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, settings: Settings, vector_store: VectorStoreProvider,
                 embedder: EmbeddingProvider) -> None:
        self.settings = settings
        self._vector_store = vector_store
        self._embedder = embedder

    def retrieve(self, question: str, top_k: int | None = None) -> list[SourceRef]:
        from llama_index.core.vector_stores import VectorStoreQuery
        from llama_index.core.vector_stores.types import VectorStoreQueryMode

        k = top_k or self.settings.RETRIEVAL_TOP_K
        try:
            query_embedding = self._embedder.embed_query(question)
        except Exception as exc:
            raise DependencyUnavailableError(
                detail=f"Query embedding failed (is Ollama running?): {exc}"
            ) from exc

        store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=k,
            mode=VectorStoreQueryMode.DEFAULT,
        )
        try:
            result = self._vector_store.store.query(store_query)
        except DependencyUnavailableError:
            raise
        except Exception as exc:
            raise DependencyUnavailableError(
                detail=f"Vector retrieval failed: {exc}"
            ) from exc

        sources: list[SourceRef] = []
        for i, node in enumerate(result.nodes or []):
            similarities = result.similarities or []
            score = similarities[i] if i < len(similarities) else None
            sources.append(
                SourceRef(
                    index=i + 1,
                    document_id=node.metadata.get("doc_id", ""),
                    filename=node.metadata.get("filename", "unknown"),
                    page=node.metadata.get("page"),
                    score=round(float(score), 4) if score is not None else None,
                    text=node.get_content(metadata_mode="none").strip(),
                )
            )
        logger.info("Retrieved %d passages (top_k=%d)", len(sources), k)
        return sources
