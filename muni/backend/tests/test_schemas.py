"""Schema validation unit tests."""

import pytest
from pydantic import ValidationError

from app.schemas.document import DocumentMeta
from app.schemas.query import QueryMode, QueryRequest, QueryResponse


def test_query_request_defaults() -> None:
    request = QueryRequest(question="What is the procurement process?")
    assert request.mode is QueryMode.auto
    assert request.top_k is None
    assert request.temperature is None


def test_query_request_rejects_short_question() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(question="ab")


def test_query_request_rejects_bad_temperature() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(question="What is the policy?", temperature=9.5)


def test_query_response_roundtrip() -> None:
    response = QueryResponse(
        question="q?",
        answer="a",
        mode=QueryMode.agentic,
        model="llama3.1",
        latency_ms=12,
    )
    dumped = response.model_dump()
    assert dumped["mode"] == "agentic"
    assert QueryResponse.model_validate(dumped) == response


def test_document_meta_requires_timestamps() -> None:
    with pytest.raises(ValidationError):
        DocumentMeta(id="x", filename="f.txt")
