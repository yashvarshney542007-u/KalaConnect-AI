import os
from fastapi.testclient import TestClient
from app.main import app

AUTH_KEY = os.getenv("KALACONNECT_AI_API_KEY", "test-key-for-unit-tests-only")
os.environ.setdefault("KALACONNECT_AI_API_KEY", AUTH_KEY)
client = TestClient(app, headers={"Authorization": f"Bearer {os.environ['KALACONNECT_AI_API_KEY']}"})


def test_transcribe_unsupported_file_type():
    response = client.post(
        "/api/voice/transcribe",
        files={"file": ("test.txt", b"sample plain text", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported audio type" in response.json()["detail"]


def test_transcribe_audio_endpoint():
    sample_file = os.path.join("sample_data", "audio", "sample_hi.wav")
    assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"

    with open(sample_file, "rb") as f:
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample_hi.wav", f, "audio/wav")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "text" in data
    assert data["language"] == "hi"
    assert data["language_probability"] > 0.8
