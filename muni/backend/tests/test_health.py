"""Health endpoint contract tests."""

from fastapi.testclient import TestClient


def test_liveness(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "test"
    assert "version" in body


def test_health_reports_dependency_flags(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    deps = response.json()["dependencies"]
    assert set(deps) == {"ollama", "postgres"}
    # No Ollama/Postgres in the test environment → both reported down.
    assert deps["ollama"] is False
    assert deps["postgres"] is False


def test_readiness_is_503_without_dependencies(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
