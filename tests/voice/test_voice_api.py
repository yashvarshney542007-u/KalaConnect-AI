"""
Voice API Tests
===============
Tests for POST /api/voice/transcribe

Model inference (Whisper) is mocked so tests run fast without loading
any ML model.  Integration tests that require real audio are kept in a
separate fixture-guarded block.
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TRANSCRIBE_URL = "/api/voice/transcribe"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_TRANSCRIPTION = {
    "text": "नमस्ते",
    "language": "hi",
    "language_probability": 0.99,
}

MOCK_TRANSCRIBE = "app.api.voice.transcribe_audio"


# ---------------------------------------------------------------------------
# Validation tests (no model needed)
# ---------------------------------------------------------------------------

def test_transcribe_unsupported_format():
    """Non-audio files must be rejected with HTTP 400."""
    response = client.post(
        TRANSCRIBE_URL,
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported audio type" in response.json()["detail"]


def test_transcribe_unsupported_image_type():
    """Image files must be rejected (not audio)."""
    response = client.post(
        TRANSCRIBE_URL,
        files={"file": ("photo.jpg", b"\xff\xd8\xff", "image/jpeg")},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Happy-path tests (mocked model)
# ---------------------------------------------------------------------------

@patch(MOCK_TRANSCRIBE, return_value=VALID_TRANSCRIPTION)
def test_transcribe_wav_returns_success(mock_fn):
    """Valid WAV file should return success and the mocked transcription."""
    dummy_wav = b"RIFF\x00\x00\x00\x00WAVEfmt "
    response = client.post(
        TRANSCRIBE_URL,
        files={"file": ("sample.wav", dummy_wav, "audio/wav")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "text" in data
    assert "language" in data


@patch(MOCK_TRANSCRIBE, return_value=VALID_TRANSCRIPTION)
def test_transcribe_mp3_accepted(mock_fn):
    """MP3 content-type must be accepted."""
    response = client.post(
        TRANSCRIBE_URL,
        files={"file": ("sample.mp3", b"\xff\xfb", "audio/mpeg")},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@patch(MOCK_TRANSCRIBE, return_value=VALID_TRANSCRIPTION)
def test_transcribe_response_schema(mock_fn):
    """Response must contain success, text, language, language_probability."""
    dummy_wav = b"RIFF\x00\x00\x00\x00WAVEfmt "
    response = client.post(
        TRANSCRIBE_URL,
        files={"file": ("sample.wav", dummy_wav, "audio/wav")},
    )
    data = response.json()
    assert "success" in data
    assert "text" in data
    assert "language" in data
    assert "language_probability" in data


# ---------------------------------------------------------------------------
# Integration tests — require real audio fixture
# ---------------------------------------------------------------------------

SAMPLE_AUDIO = os.path.join("tests", "fixtures", "audio", "sample_hi.wav")


@pytest.mark.skipif(
    not os.path.exists(SAMPLE_AUDIO),
    reason=(
        "Real audio fixture not found. "
        "Place a Hindi WAV file at tests/fixtures/audio/sample_hi.wav "
        "to enable integration tests."
    ),
)
def test_transcribe_real_audio():
    """
    Integration test: transcribes a real Hindi WAV file.

    To enable this test:
    1. Place a short (< 30 s) Hindi WAV file at:
       tests/fixtures/audio/sample_hi.wav
    2. The file must not be committed to Git (add *.wav to .gitignore).
    3. Expected language is 'hi' with probability > 0.80.
    """
    with open(SAMPLE_AUDIO, "rb") as f:
        response = client.post(
            TRANSCRIBE_URL,
            files={"file": ("sample_hi.wav", f, "audio/wav")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["text"], str)
    assert data["language"] == "hi"
    assert data["language_probability"] > 0.80
