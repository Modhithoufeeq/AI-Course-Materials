"""Ingestion endpoint contract tests."""

from fastapi.testclient import TestClient


def test_upload_text_document(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("policy.txt", b"Remote work policy: 3 days per week.", "text/plain")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["document"]["filename"] == "policy.txt"
    assert body["document"]["status"] == "indexed"
    assert body["ingested_chunks"] == 1
    assert body["source"] == "upload"


def test_upload_empty_file_is_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unprocessable_content"


def test_upload_unsupported_extension_is_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("virus.exe", b"MZ...", "application/octet-stream")},
    )
    assert response.status_code == 422
    assert "Unsupported file type" in response.json()["error"]["detail"]


def test_directory_ingest_rejects_path_traversal(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ingest/directory",
        json={"path": "C:/Windows/System32", "recursive": True},
    )
    assert response.status_code == 422
    assert "ingest directory" in response.json()["error"]["detail"]
