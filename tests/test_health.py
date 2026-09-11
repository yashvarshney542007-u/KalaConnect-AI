from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "kalaconnect-ai"


def test_root_returns_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "KalaConnect AI service is running"
