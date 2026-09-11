"""
Vision API Tests
================
Tests for POST /api/vision/analyze

SmolVLM is mocked so tests run fast without downloading any model.
Integration tests that require real images are fixture-guarded.
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ANALYZE_URL = "/api/vision/analyze"
MOCK_ANALYZE = "app.api.vision.analyze_image"

# Minimal valid JPEG header bytes
JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"

VALID_ANALYSIS = {
    "craft": "pottery",
    "material": "terracotta clay",
    "product_type": "earthen pot",
    "visual_description": "Handcrafted terracotta pot with traditional motifs",
    "colors": ["brown", "ochre"],
    "design_features": ["etched geometric lines"],
    "craftsmanship_features": ["wheel-thrown pottery"],
    "possible_region": "Rajasthan",
    "confidence": 0.88,
}


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def test_analyze_rejects_plain_text():
    """Non-image file must be rejected with HTTP 400."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("doc.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]


def test_analyze_rejects_pdf():
    response = client.post(
        ANALYZE_URL,
        files={"file": ("report.pdf", b"%PDF-", "application/pdf")},
    )
    assert response.status_code == 400


def test_analyze_rejects_oversized_file():
    """Files exceeding 10 MB must be rejected with HTTP 400."""
    large_payload = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        ANALYZE_URL,
        files={"file": ("big.jpg", large_payload, "image/jpeg")},
    )
    assert response.status_code == 400
    assert "10 MB" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Happy-path tests (mocked model)
# ---------------------------------------------------------------------------

@patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
def test_analyze_jpeg_success(mock_fn):
    """Valid JPEG should return success with correct analysis wrapper."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "craft.jpg"
    assert "analysis" in data


@patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
def test_analyze_png_accepted(mock_fn):
    """PNG content-type should be accepted."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("craft.png", JPEG_HEADER, "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
def test_analyze_webp_accepted(mock_fn):
    """WEBP content-type should be accepted."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("craft.webp", JPEG_HEADER, "image/webp")},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
def test_analyze_response_schema(mock_fn):
    """Response must match the stable analysis schema."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("craft.jpg", JPEG_HEADER, "image/jpeg")},
    )
    data = response.json()
    analysis = data["analysis"]

    required_keys = {
        "craft", "material", "product_type", "visual_description",
        "colors", "design_features", "craftsmanship_features",
        "possible_region", "confidence",
    }
    assert required_keys.issubset(analysis.keys())
    assert isinstance(analysis["colors"], list)
    assert isinstance(analysis["design_features"], list)
    assert isinstance(analysis["craftsmanship_features"], list)
    assert isinstance(analysis["confidence"], float)
    assert 0.0 <= analysis["confidence"] <= 1.0


@patch(MOCK_ANALYZE, return_value=VALID_ANALYSIS)
def test_analyze_filename_preserved(mock_fn):
    """Uploaded filename must be echoed in the response."""
    response = client.post(
        ANALYZE_URL,
        files={"file": ("my_pottery.jpg", JPEG_HEADER, "image/jpeg")},
    )
    assert response.json()["filename"] == "my_pottery.jpg"


# ---------------------------------------------------------------------------
# Integration tests — require real image fixture
# ---------------------------------------------------------------------------

SAMPLE_IMAGE = os.path.join("tests", "fixtures", "images", "sample_craft.jpg")


@pytest.mark.skipif(
    not os.path.exists(SAMPLE_IMAGE),
    reason=(
        "Real image fixture not found. "
        "Place a craft JPG at tests/fixtures/images/sample_craft.jpg "
        "to enable integration tests."
    ),
)
def test_analyze_real_image():
    """
    Integration test: runs SmolVLM on a real craft image.

    To enable this test:
    1. Place a real craft/artisan product JPEG at:
       tests/fixtures/images/sample_craft.jpg
    2. The file must not be committed to Git.
    3. The test verifies schema only — it does NOT assert specific labels.
    """
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post(
            ANALYZE_URL,
            files={"file": ("sample_craft.jpg", f, "image/jpeg")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "analysis" in data
    analysis = data["analysis"]
    assert "craft" in analysis
    assert "confidence" in analysis
    assert 0.0 <= analysis["confidence"] <= 1.0
