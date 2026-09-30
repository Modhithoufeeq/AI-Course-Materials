from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_query_service
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter()


@router.post("", response_model=QueryResponse, summary="Ask a question over the knowledge base")
def query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    return service.answer(request)
