"""LLM factory helpers (LlamaIndex + LangChain flavours of local Ollama)."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings


def get_llama_index_llm(settings: Settings, temperature: float | None = None) -> Any:
    from llama_index.llms.ollama import Ollama as LlamaIndexOllama

    return LlamaIndexOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        request_timeout=settings.OLLAMA_REQUEST_TIMEOUT,
        temperature=settings.RAG_TEMPERATURE if temperature is None else temperature,
    )


def get_langchain_llm(settings: Settings, temperature: float | None = None) -> Any:
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.OLLAMA_LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.RAG_TEMPERATURE if temperature is None else temperature,
        timeout=settings.OLLAMA_REQUEST_TIMEOUT,
    )
