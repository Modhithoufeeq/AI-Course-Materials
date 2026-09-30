"""Query endpoint contract tests."""

from fastapi.testclient import TestClient


def test_query_returns_answer(client: TestClient) -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "What is the remote work policy?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"].startswith("Fake answer for:")
    assert body["mode"] == "basic"
    assert body["model"] == "fake-model"
    assert body["latency_ms"] >= 0
    assert body["error"] is None


def test_query_question_too_short_is_422(client: TestClient) -> None:
    response = client.post("/api/v1/query", json={"question": "hi"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["fields"][0]["field"] == "body.question"


def test_query_rejects_out_of_range_top_k(client: TestClient) -> None:
    response = client.post(
        "/api/v1/query",
        json={"question": "What is the leave policy?", "top_k": 99},
    )
    assert response.status_code == 422
