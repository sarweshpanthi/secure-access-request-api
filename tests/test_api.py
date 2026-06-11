from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_access_request_endpoint_admin_role():
    payload = {
        "user": "alice@example.com",
        "system": "github",
        "role": "admin",
        "justification": "Need access for incident response"
    }

    response = client.post("/access-request", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["user"] == "alice@example.com"
    assert body["system"] == "github"
    assert body["role"] == "admin"
    assert body["evaluation"]["risk"] == "high"
    assert body["evaluation"]["decision"] == "manual_review_required"