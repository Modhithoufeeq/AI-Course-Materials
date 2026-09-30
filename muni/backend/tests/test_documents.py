"""Document CRUD contract tests (against the fake service)."""

from fastapi.testclient import TestClient


def test_list_documents_empty(client: TestClient) -> None:
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "page": 1, "page_size": 20, "total": 0}


def test_get_missing_document_returns_404_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/documents/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"


def test_delete_missing_document_returns_404(client: TestClient) -> None:
    response = client.delete("/api/v1/documents/does-not-exist")
    assert response.status_code == 404
