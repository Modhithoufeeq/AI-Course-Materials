"""Grounded answer generation with optional LLM-based compression/reranking."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.rag.llm import get_llama_index_llm
from app.core.rag.retriever import Retriever
from app.prompts.rag.templates import build_answer_prompt
from app.schemas.query import SourceRef

logger = logging.getLogger(__name__)


class QueryEngine:
    """Basic RAG flow: retrieve → (optional) rerank → generate."""

    def __init__(self, settings: Settings, retriever: Retriever) -> None:
        self.settings = settings
        self._retriever = retriever

    # ── Steps (kept separate so the agentic flow can reuse them) ────────────

    def retrieve_sources(self, question: str,
                         top_k: int | None = None) -> list[SourceRef]:
        sources = self._retriever.retrieve(question, top_k)
        if self.settings.COMPRESSION_ENABLED:
            return self._compress(question, sources)
        return sources

    def generate_from_sources(self, question: str, sources: list[SourceRef],
                              temperature: float | None = None) -> str:
        if not sources:
            return (
                "I could not find any relevant documents for your question. "
                "Please make sure the knowledge base has been populated (see /ingest)."
            )
        llm = get_llama_index_llm(self.settings, temperature)
        prompt = build_answer_prompt(question, sources)
        response = llm.complete(prompt)
        return str(response.text).strip()

    # ── Full pipeline ────────────────────────────────────────────────────────

    def run(self, question: str, top_k: int | None = None,
            temperature: float | None = None) -> tuple[str, list[SourceRef]]:
        sources = self.retrieve_sources(question, top_k)
        answer = self.generate_from_sources(question, sources, temperature)
        return answer, sources

    # ── Compression / reranking ──────────────────────────────────────────────

    def _compress(self, question: str,
                  sources: list[SourceRef]) -> list[SourceRef]:
        top_n = self.settings.COMPRESSION_CONTEXT_WINDOW
        if len(sources) <= top_n:
            return sources
        try:
            return self._llm_rerank(question, sources, top_n)
        except Exception as exc:  # noqa: BLE001 — reranking is best-effort
            logger.warning("LLM reranking failed (%s); keeping top-%d by score",
                           exc, top_n)
            return sources[:top_n]

    def _llm_rerank(self, question: str, sources: list[SourceRef],
                    top_n: int) -> list[SourceRef]:
        from llama_index.core.postprocessor import LLMRerank
        from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

        by_text = {s.text: s for s in sources}
        nodes = [
            NodeWithScore(
                node=TextNode(
                    text=s.text,
                    metadata={"filename": s.filename, "doc_id": s.document_id},
                ),
                score=s.score or 0.0,
            )
            for s in sources
        ]
        reranker = LLMRerank(
            top_n=top_n, llm=get_llama_index_llm(self.settings)
        )
        reranked = reranker.postprocess_nodes(nodes, QueryBundle(question))
        compressed: list[SourceRef] = []
        for i, node_with_score in enumerate(reranked):
            original = by_text.get(node_with_score.node.get_content(metadata_mode="none"))
            if original is None:  # pragma: no cover — defensive
                continue
            compressed.append(
                original.model_copy(
                    update={
                        "index": i + 1,
                        "score": (
                            round(float(node_with_score.score), 4)
                            if node_with_score.score is not None else original.score
                        ),
                    }
                )
            )
        return compressed or sources[:top_n]
