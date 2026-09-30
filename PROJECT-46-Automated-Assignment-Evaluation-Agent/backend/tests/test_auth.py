import pytest
from fastapi.testclient import TestClient


def test_register_and_login_flow(client: TestClient):
    # 1. Register a new teacher
    reg_payload = {
        "email": "new_teacher@test.com",
        "password": "strongpassword123",
        "full_name": "Dr. Sarah Connor",
        "role": "teacher",
        "department": "Robotics & AI"
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "new_teacher@test.com"
    assert reg_data["user"]["role"] == "teacher"

    # 2. Login with registered credentials
    login_payload = {
        "email": "new_teacher@test.com",
        "password": "strongpassword123"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token

    # 3. Access protected /me endpoint
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["full_name"] == "Dr. Sarah Connor"


def test_invalid_login_credentials(client: TestClient):
    resp = client.post("/api/v1/auth/login", json={"email": "nonexistent@test.com", "password": "wrongpassword"})
    assert resp.status_code == 401


def test_role_authorization_guard(client: TestClient, student_auth_headers):
    # Student attempting to create an assignment (restricted to teachers)
    assign_payload = {
        "title": "Unauthorized Assignment",
        "instructions": "Should fail with 403 forbidden.",
        "max_score": 100.0
    }
    resp = client.post("/api/v1/assignments", json=assign_payload, headers=student_auth_headers)
    assert resp.status_code == 403
