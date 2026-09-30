from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_document_service
from app.schemas.document import DocumentListResponse, DocumentMeta
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("", response_model=DocumentListResponse, summary="List indexed documents")
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    return service.list_documents(page=page, page_size=page_size)


@router.get("/{doc_id}", response_model=DocumentMeta, summary="Get document metadata")
def get_document(
    doc_id: str,
    service: DocumentService = Depends(get_document_service),
) -> DocumentMeta:
    return service.get_document(doc_id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document and its vectors")
def delete_document(
    doc_id: str,
    service: DocumentService = Depends(get_document_service),
) -> Response:
    service.delete_document(doc_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
