"""Document parsing: plain-text files natively, rich formats via Docling."""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.errors import UnprocessableContentError

logger = logging.getLogger(__name__)

#: Extensions parsed natively (no Docling dependency needed).
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".html", ".htm", ".csv", ".json"}

#: Extensions parsed with Docling (pdf, docx, pptx, xlsx, images, …).
DOCLING_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls",
    ".odt", ".epub", ".rtf", ".rst", ".org", ".asciidoc",
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
}

SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | DOCLING_EXTENSIONS

CONTENT_TYPE_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
    ".csv": "text/csv",
    ".json": "application/json",
}


def content_type_for(path: Path) -> str:
    return CONTENT_TYPE_MAP.get(path.suffix.lower(), "application/octet-stream")


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnprocessableContentError(detail=f"Could not decode text file: {path.name}")


def _parse_with_docling(path: Path) -> str:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise UnprocessableContentError(
            detail="Docling is not installed; cannot parse this file type."
        ) from exc
    try:
        converter = DocumentConverter()
        result = converter.convert(source=str(path))
        return result.document.export_to_markdown()
    except Exception as exc:
        raise UnprocessableContentError(
            detail=f"Failed to parse '{path.name}' with Docling: {exc}"
        ) from exc


def extract_text(path: Path) -> str:
    """Return the plain-text extraction of ``path`` (raises 422 on failure)."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnprocessableContentError(
            detail=f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    if suffix in TEXT_EXTENSIONS:
        return _read_text(path).strip()
    return _parse_with_docling(path).strip()
