from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel, Field

from app.api.deps import get_document_service, get_settings
from app.core.config import Settings
from app.core.errors import UnprocessableContentError
from app.schemas.document import IngestResult
from app.services.document_service import DocumentService

router = APIRouter()


class DirectoryIngestRequest(BaseModel):
    path: str = Field(min_length=1, description="Directory (or file) to ingest")
    recursive: bool = True


def _resolve_ingest_base(settings: Settings) -> Path:
    return Path(settings.INGEST_DIR).resolve()


def _validate_upload(file: UploadFile, settings: Settings) -> tuple[str, bytes]:
    filename = Path(file.filename or "upload.bin").name
    if not filename or filename in {".", ".."}:
        raise UnprocessableContentError(detail="A valid file name is required.")

    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".txt", ".md",
                      ".markdown", ".html", ".htm", ".csv", ".json"}:
        raise UnprocessableContentError(detail=f"Unsupported file type '{suffix}'.")

    content = file.file.read()
    if not content:
        raise UnprocessableContentError(detail="Uploaded file is empty.")

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise UnprocessableContentError(
            detail=f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit."
        )
    return filename, content


@router.post("/upload", response_model=IngestResult, status_code=status.HTTP_201_CREATED,
             summary="Ingest (parse → chunk → embed → index) an uploaded document")
async def ingest_upload(
    file: UploadFile = File(..., description="Document to index (.pdf, .docx, .md, .txt, …)"),
    service: DocumentService = Depends(get_document_service),
    settings: Settings = Depends(get_settings),
) -> IngestResult:
    filename, content = _validate_upload(file, settings)
    return service.ingest_upload(filename, content, file.content_type or "")


@router.post("/directory", response_model=list[IngestResult], status_code=status.HTTP_201_CREATED,
             summary="Bulk-ingest every supported file inside the configured ingest directory")
def ingest_directory(
    request: DirectoryIngestRequest,
    service: DocumentService = Depends(get_document_service),
    settings: Settings = Depends(get_settings),
) -> list[IngestResult]:
    base = _resolve_ingest_base(settings)
    target = Path(request.path).resolve()
    if base not in target.parents and target != base:
        raise UnprocessableContentError(
            detail=f"Path must be inside the configured ingest directory ({base})."
        )
    return service.ingest_path(target, recursive=request.recursive)
