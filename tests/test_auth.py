"""
tests/test_auth.py
==================

Authentication tests for the KalaConnect AI service.

Covers:
- Valid API key         → 200 on protected endpoints
- Missing header        → 401
- Invalid key           → 401
- Malformed header      → 401
- Wrong scheme          → 401
- GET /health           → 200 (no auth required)
- GET /                 → 200 (no auth required)

The test key is injected via environment variable so the actual .env file is
never read during CI and the real secret is never hard-coded.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# ── Test constants ──────────────────────────────────────────────────────────

TEST_API_KEY = "test-key-for-unit-tests-only"

# Minimal valid JPEG bytes accepted by the vision endpoint
JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"
# Minimal WAV bytes accepted by the voice endpoint
WAV_HEADER = b"RIFF\x00\x00\x00\x00WAVEfmt "

MOCK_TRANSCRIBE = "app.api.voice.transcribe_audio"
MOCK_ANALYZE = "app.api.vision.analyze_image"

VALID_TRANSCRIPTION = {
    "text": "नमस्ते",
    "language": "hi",
    "language_probability": 0.99,
}
VALID_ANALYSIS = {
    "craft": "pottery",
    "material": "terracotta clay",
    "product_type": "earthen pot",
    "visual_description": "Handcrafted terracotta pot",
    "colors": ["brown"],
    "design_features": ["etched lines"],
    "craftsmanship_features": ["wheel-thrown"],
    "possible_region": "Rajasthan",
    "confidence": 0.88,
}


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """TestClient with TEST_API_KEY injected into the environment."""
    with patch.dict(os.environ, {"KALACONNECT_AI_API_KEY": TEST_API_KEY}):
        # Import app AFTER patching env so security.py reads the test key
        from app.main import app
        with TestClient(app) as c:
            yield c


# ── Public endpoints (no auth) ───────────────────────────────────────────────

class TestPublicEndpoints:
    def test_health_no_auth_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_no_auth_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200


# ── Voice endpoint auth ──────────────────────────────────────────────────────

class TestVoiceAuth:
    @patch(MOCK_TRANSCRIBE, return_value=VALID_TRANSCRIPTION)
    def test_valid_key_accepted(self, mock_fn, client):
        """A correct Bearer token must be accepted."""
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
            headers={"Authorization": f"Bearer {TEST_API_KEY}"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_missing_auth_header_returns_401(self, client):
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
        )
        assert response.status_code == 401

    def test_invalid_key_returns_401(self, client):
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert response.status_code == 401

    def test_malformed_header_returns_401(self, client):
        """Non-Bearer scheme should be rejected."""
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status_code == 401

    def test_bearer_prefix_only_returns_401(self, client):
        """'Bearer ' with an empty token string should be rejected."""
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
            headers={"Authorization": "Bearer "},
        )
        # FastAPI's HTTPBearer raises 403 for empty credentials; treat both as
        # an authentication failure (not 200)
        assert response.status_code in (401, 403)

    def test_error_does_not_leak_key(self, client):
        """The 401 response body must not contain the real API key."""
        response = client.post(
            "/api/voice/transcribe",
            files={"file": ("sample.wav", WAV_HEADER, "audio/wav")},
            headers={"Authorization": "Bearer bad-key"},
        )
        assert response.status_code == 401
        assert TEST_API_KEY not in response.text


# ── Vision endpoint auth ─────────────────────────────────────────────────────

class TestVisionAuth:
    @patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
    def test_valid_key_accepted(self, mock_fn, client):
        """A correct Bearer token must be accepted."""
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
            headers={"Authorization": f"Bearer {TEST_API_KEY}"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_missing_auth_header_returns_401(self, client):
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
        )
        assert response.status_code == 401

    def test_invalid_key_returns_401(self, client):
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
            headers={"Authorization": "Bearer totally-wrong"},
        )
        assert response.status_code == 401

    def test_malformed_header_returns_401(self, client):
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
            headers={"Authorization": "Token abc123"},
        )
        assert response.status_code == 401

    def test_error_does_not_leak_key(self, client):
        response = client.post(
            "/api/vision/analyze",
            files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
            headers={"Authorization": "Bearer bad-key"},
        )
        assert response.status_code == 401
        assert TEST_API_KEY not in response.text


# ── Security module unit tests ───────────────────────────────────────────────

class TestSecurityModule:
    def test_missing_env_var_raises_runtime_error(self):
        """_get_expected_key() must raise RuntimeError if env var is unset."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the key if it happens to be set
            os.environ.pop("KALACONNECT_AI_API_KEY", None)
            from app.core.security import _get_expected_key
            with pytest.raises(RuntimeError, match="KALACONNECT_AI_API_KEY"):
                _get_expected_key()
