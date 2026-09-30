"""Ollama embedding provider (lazy — heavy imports stay out of the request path)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings


class EmbeddingProvider:
    """Cached wrapper around the configured Ollama embedding model."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: Any = None

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from llama_index.embeddings.ollama import OllamaEmbedding
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "llama-index-embeddings-ollama is not installed"
                ) from exc
            self._model = OllamaEmbedding(
                model_name=self._settings.OLLAMA_EMBED_MODEL,
                base_url=self._settings.OLLAMA_BASE_URL,
                embed_batch_size=32,
            )
        return self._model

    def embed_query(self, text: str) -> list[float]:
        return list(self.model.get_query_embedding(text))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [list(vec) for vec in self.model.get_text_embedding_batch(texts)]
