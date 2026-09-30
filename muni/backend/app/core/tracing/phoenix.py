"""OpenTelemetry tracing wired to Arize Phoenix (OTLP/HTTP).

Instrumentors for LlamaIndex and CrewAI capture every LLM/embedding/retrieval
call so full traces are visible in the Phoenix UI. All of this is best-effort:
if Phoenix or the instrumentation packages are missing, the app still runs.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)


def init_tracing(settings: Settings) -> Any | None:
    """Set up OTLP export + instrumentors. Returns the tracer provider or None."""
    if not settings.TRACING_ENABLED or settings.ENVIRONMENT == "test":
        logger.info("Tracing disabled (TRACING_ENABLED=%s, env=%s)",
                    settings.TRACING_ENABLED, settings.ENVIRONMENT)
        return None
    try:
        from opentelemetry import trace as otel_trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        from app import __version__

        resource = Resource.create({
            "service.name": "document-search-backend",
            "service.version": __version__,
            "deployment.environment": settings.ENVIRONMENT,
        })
        provider = TracerProvider(resource=resource)
        endpoint = f"{settings.PHOENIX_COLLECTOR_ENDPOINT.rstrip('/')}/v1/traces"
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        otel_trace.set_tracer_provider(provider)

        _instrument(provider, "llama_index",
                    "openinference.instrumentation.llama_index",
                    "LlamaIndexInstrumentor")
        _instrument(provider, "crewai",
                    "openinference.instrumentation.crewai",
                    "CrewAIInstrumentor")

        logger.info("Tracing enabled → Phoenix at %s (UI: %s)",
                    endpoint, settings.PHOENIX_UI_URL)
        return provider
    except Exception as exc:  # noqa: BLE001 — observability must never break serving
        logger.warning("Tracing disabled: %s", exc)
        return None


def _instrument(provider: Any, label: str, module: str, class_name: str) -> None:
    try:
        module_ref = __import__(module, fromlist=[class_name])
        instrumentor = getattr(module_ref, class_name)()
        instrumentor.instrument(tracer_provider=provider)
        logger.info("Instrumented %s", label)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not instrument %s: %s", label, exc)


def shutdown_tracing(provider: Any | None) -> None:
    if provider is not None:
        try:
            provider.shutdown()
        except Exception:  # noqa: BLE001
            logger.debug("Tracer provider shutdown failed", exc_info=True)
