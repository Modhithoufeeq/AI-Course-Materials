"""Application error types and FastAPI exception handlers.

Every error surfaced by the API has the same JSON envelope::

    {"error": {"code": "<machine_readable>", "detail": "<human readable>"}}
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for all expected application errors."""

    status_code: int = 500
    code: str = "internal_error"
    detail: str = "An unexpected error occurred."

    def __init__(self, *, detail: str | None = None, code: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    detail = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    detail = "Resource already exists."


class UnprocessableContentError(AppError):
    status_code = 422
    code = "unprocessable_content"
    detail = "The provided content could not be processed."


class DependencyUnavailableError(AppError):
    status_code = 503
    code = "dependency_unavailable"
    detail = "A required external dependency is unavailable."


def _error_body(
    code: str,
    detail: str,
    fields: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    error: dict[str, object] = {"code": code, "detail": detail}
    if fields:
        error["fields"] = fields
    return {"error": error}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach consistent JSON error handling to the app."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields = [
            {
                "field": ".".join(str(part) for part in err.get("loc", ())) or "body",
                "message": err.get("msg", "invalid value"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error", "Request validation failed.", fields),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_error", "An unexpected error occurred."),
        )
