from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_unsupported_file_type():
    response = client.post(
        "/api/vision/analyze",
        files={"file": ("test.txt", b"sample plain text", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]


def test_analyze_file_size_exceeded():
    large_payload = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/vision/analyze",
        files={"file": ("large.jpg", large_payload, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "exceeds the 10 MB limit" in response.json()["detail"]


@patch("app.api.vision.analyze_image")
def test_analyze_image_endpoint_success(mock_analyze_image):
    mock_analyze_image.return_value = {
        "craft": "pottery",
        "material": "terracotta clay",
        "product_type": "earthen pot",
        "visual_description": "Handcrafted terracotta pot with traditional motifs",
        "colors": ["brown", "ochre"],
        "design_features": ["etched geometric lines"],
        "craftsmanship_features": ["wheel-thrown pottery"],
        "possible_region": "Rajasthan",
        "confidence": 0.95
    }

    dummy_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"

    response = client.post(
        "/api/vision/analyze",
        files={"file": ("test_pot.jpg", dummy_image_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "test_pot.jpg"
    assert "analysis" in data
    analysis = data["analysis"]
    assert analysis["craft"] == "pottery"
    assert analysis["material"] == "terracotta clay"
    assert analysis["product_type"] == "earthen pot"
    assert analysis["confidence"] == 0.95
    assert isinstance(analysis["colors"], list)
    assert isinstance(analysis["design_features"], list)
    assert isinstance(analysis["craftsmanship_features"], list)
