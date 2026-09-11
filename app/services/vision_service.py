from app.models.vision_model import get_vision_model


def analyze_image(image_path: str) -> dict:
    return get_vision_model().analyze_image(image_path)
