"""
app/schemas/price.py
====================
Price prediction schemas for the AI pipeline.

Pipeline order in /docs:
  1. POST /api/vision/analyze   -> copy JSON response
  2. POST /api/voice/transcribe -> copy JSON response
  3. POST /api/price/predict    -> paste both above -> returns INR price
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


CRAFT_COMPLEXITY = {
    "blue pottery": 7.0,
    "pashmina": 9.5,
    "pashmina weaving": 9.5,
    "dhokra": 8.0,
    "dhokra metal craft": 8.0,
    "wood carving": 7.5,
    "zardozi": 9.0,
    "block printing": 5.0,
    "weaving": 6.5,
    "embroidery": 8.5,
    "pottery": 5.5,
    "terracotta": 5.0,
    "metalwork": 7.0,
    "jewelry": 8.0,
    "painting": 7.0,
    "leather": 5.5,
}


class VisionOutput(BaseModel):
    """Exact JSON returned by POST /api/vision/analyze"""
    craft: Optional[str] = Field(None, description="Craft type detected from image")
    material: Optional[str] = Field(None, description="Material identified from image")
    product_type: Optional[str] = Field(None, description="Object type detected")
    visual_description: Optional[str] = Field(None, description="Visual summary of the product")
    colors: Optional[List[str]] = Field(default_factory=list, description="Main visible colors")
    design_features: Optional[List[str]] = Field(default_factory=list, description="Motifs and patterns")
    craftsmanship_features: Optional[List[str]] = Field(default_factory=list, description="Artisan characteristics")
    possible_region: Optional[str] = Field(None, description="Geographic region if visually justified")
    confidence: Optional[float] = Field(None, description="Model confidence 0.0 to 1.0")


class VoiceOutput(BaseModel):
    """Exact JSON returned by POST /api/voice/transcribe"""
    text: Optional[str] = Field(None, description="Transcription of the artisan voice recording")
    language: Optional[str] = Field(None, description="Detected language code")
    language_probability: Optional[float] = Field(None, description="Language detection confidence")



class PricePredictRequest(BaseModel):
    """
    Price Prediction Input.

    This endpoint is the FINAL STEP of the AI pipeline:

      Step 1: POST /api/vision/analyze   -> analyze product image -> copy full JSON response
      Step 2: POST /api/voice/transcribe -> transcribe voice note  -> copy full JSON response
      Step 3: POST /api/price/predict    -> paste both responses below -> get predicted price INR

    The system automatically derives craft complexity, labor cost, overhead,
    and all other required model features from the Vision and Voice outputs.
    No manual JSON construction is needed.
    """
    vision_output: VisionOutput = Field(
        ...,
        description="[Step 1 output] Paste full JSON from POST /api/vision/analyze"
    )
    voice_output: VoiceOutput = Field(
        ...,
        description="[Step 2 output] Paste full JSON from POST /api/voice/transcribe"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vision_output": {
                    "craft": "Blue Pottery",
                    "material": "Ceramic",
                    "product_type": "Vase",
                    "visual_description": "Hand-painted blue and white ceramic vase with floral motifs",
                    "colors": ["blue", "white"],
                    "design_features": ["floral motifs", "geometric borders"],
                    "craftsmanship_features": ["hand-painted", "wheel-thrown"],
                    "possible_region": "Jaipur",
                    "confidence": 0.92
                },
                "voice_output": {
                    "text": "Handcrafted Blue Pottery decorative vase, took 3 days to make",
                    "language": "en",
                    "language_probability": 0.99
                }
            }
        }
    }


class PricePredictResponse(BaseModel):
    """Price prediction response."""
    success: bool
    predicted_price_inr: float
    features_used: Dict[str, Any]
