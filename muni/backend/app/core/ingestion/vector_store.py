"""pgvector-backed vector store provider (LlamaIndex PGVectorStore)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings
from app.core.errors import DependencyUnavailableError


class VectorStoreProvider:
    """Lazily builds and caches the PGVectorStore connection."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._store: Any = None

    @property
    def store(self) -> Any:
        if self._store is None:
            try:
                from llama_index.vector_stores.postgres import PGVectorStore
            except ImportError as exc:
                raise DependencyUnavailableError(
                    detail="llama-index-vector-stores-postgres is not installed."
                ) from exc
            s = self._settings
            try:
                self._store = PGVectorStore.from_params(
                    database=s.PGVECTOR_DATABASE,
                    host=s.PGVECTOR_HOST,
                    password=s.PGVECTOR_PASSWORD,
                    port=s.PGVECTOR_PORT,
                    user=s.PGVECTOR_USER,
                    table_name=s.PGVECTOR_TABLE,
                    embed_dim=s.EMBEDDING_DIM,
                    cache_ok=True,
                )
            except Exception as exc:
                raise DependencyUnavailableError(
                    detail=f"Could not connect to the pgvector store: {exc}"
                ) from exc
        return self._store
