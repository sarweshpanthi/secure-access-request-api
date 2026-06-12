from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def login_and_get_token(email: str, password: str) -> str:
    response = client.post(
        "/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_login_returns_token_for_valid_user():
    response = client.post(
        "/login",
        json={
            "email": "high@project.com",
            "password": "highpass"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_rejects_invalid_password():
    response = client.post(
        "/login",
        json={
            "email": "high@project.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_access_request_endpoint_high_risk_role():
    token = login_and_get_token("high@project.com", "highpass")

    payload = {
        "system": "github",
        "role": "admin",
        "justification": "Need access for incident response"
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post("/access-request", json=payload, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["requested_by"] == "high@project.com"
    assert body["system"] == "github"
    assert body["role"] == "admin"
    assert body["evaluation"]["risk"] == "high"
    assert body["evaluation"]["decision"] == "manual_review_required"


def test_access_request_endpoint_medium_risk_role():
    token = login_and_get_token("medium@project.com", "mediumpass")

    payload = {
        "system": "github",
        "role": "write",
        "justification": "Need access to update project configuration"
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post("/access-request", json=payload, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["requested_by"] == "medium@project.com"
    assert body["evaluation"]["risk"] == "medium"
    assert body["evaluation"]["decision"] == "manager_approval_required"


def test_access_request_endpoint_low_risk_role():
    token = login_and_get_token("low@project.com", "lowpass")

    payload = {
        "system": "github",
        "role": "read-only",
        "justification": "Need access to review logs"
    }

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post("/access-request", json=payload, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["requested_by"] == "low@project.com"
    assert body["evaluation"]["risk"] == "low"
    assert body["evaluation"]["decision"] == "approved_for_review"


def test_access_request_rejects_missing_token():
    payload = {
        "system": "github",
        "role": "admin",
        "justification": "Need access for incident response"
    }

    response = client.post("/access-request", json=payload)

    assert response.status_code in [401, 403]


def test_access_request_rejects_invalid_token():
    payload = {
        "system": "github",
        "role": "admin",
        "justification": "Need access for incident response"
    }

    headers = {
        "Authorization": "Bearer fake-token"
    }

    response = client.post("/access-request", json=payload, headers=headers)

    assert response.status_code == 401