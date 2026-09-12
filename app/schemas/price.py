"""
app/schemas/price.py
====================
Pydantic request / response schemas for the /api/price/predict endpoint.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AiData(BaseModel):
    """Fields populated by the Vision AI."""
    productName: Optional[str] = None
    craft: Optional[str] = None
    material: Optional[str] = None
    technique: Optional[str] = None
    description: Optional[str] = None


class ArtisanData(BaseModel):
    """Fields provided directly by the artisan."""
    state: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    size_length_cm: Optional[float] = None
    size_width_cm: Optional[float] = None
    size_height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    labor_days: Optional[float] = None
    artisan_skill_level: Optional[str] = None
    production_quantity: Optional[int] = None
    market_channel: Optional[str] = None


class DerivedData(BaseModel):
    """Computed / derived fields (costs, scores, etc.)."""
    product_type: Optional[str] = None
    labor_hours: Optional[float] = None
    complexity_score: Optional[float] = None
    material_cost_inr: Optional[float] = None
    labor_cost_inr: Optional[float] = None
    overhead_cost_inr: Optional[float] = None
    market_demand_score: Optional[float] = None
    seasonality_score: Optional[float] = None


class PricePredictRequest(BaseModel):
    """Full price prediction request body."""
    ai_data: AiData = Field(default_factory=AiData)
    artisan_data: ArtisanData = Field(default_factory=ArtisanData)
    derived_data: DerivedData = Field(default_factory=DerivedData)


class PricePredictResponse(BaseModel):
    """Price prediction response."""
    success: bool
    predicted_price_inr: float
    features_used: Dict[str, Any]


class VoiceImagePriceRequest(BaseModel):
    """Request body for voice + image based price prediction.
    The `voice_audio_base64` and `image_base64` fields should contain
    base64‑encoded binary data (e.g., WAV audio and JPEG/PNG image).
    """
    voice_audio_base64: str = Field(..., description="Base64‑encoded audio (WAV/MP3)")
    image_base64: str = Field(..., description="Base64‑encoded image (JPEG/PNG)")
    # Optional inclusion of existing nested data
    ai_data: AiData = Field(default_factory=AiData)
    artisan_data: ArtisanData = Field(default_factory=ArtisanData)
    derived_data: DerivedData = Field(default_factory=DerivedData)

    class Config:
        json_schema_extra = {
            "example": {
                "voice_audio_base64": "<base64-string>",
                "image_base64": "<base64-string>",
                "ai_data": {},
                "artisan_data": {},
                "derived_data": {}
            }
        }
