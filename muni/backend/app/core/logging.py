"""Structured logging with request/correlation id support."""

from __future__ import annotations

import logging
import sys
from typing import Any

_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | req=%(request_id)s | %(message)s"
)


class RequestContextFilter(logging.Filter):
    """Guarantees ``record.request_id`` exists (defaults to ``-``)."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", "-")
        return True


def configure_logging(level: str = "INFO") -> None:
    """Idempotently configure root logging (uvicorn/pytest may call twice)."""
    root = logging.getLogger()
    if getattr(root, "_muni_configured", False):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S"))
    handler.addFilter(RequestContextFilter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    root._muni_configured = True  # type: ignore[attr-defined]

    # Quiet the noisier third-party loggers.
    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a key=value structured event line."""
    parts = [f"{key}={value!r}" for key, value in fields.items()]
    logger.info("%s %s", event, " ".join(parts))
