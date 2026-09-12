"""
app/api/price.py
================
FastAPI router for the price prediction endpoint.

Pipeline:
  Step 1: POST /api/vision/analyze   -> VisionOutput JSON (auto-saved to server state)
  Step 2: POST /api/voice/transcribe -> VoiceOutput JSON  (auto-saved to server state)
  Step 3: POST /api/price/predict    -> Automatically auto-extracts from Steps 1 & 2!
"""

import sys
from pathlib import Path
from typing import Optional

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Body, HTTPException

from app.core.state import pipeline_state
from app.schemas.price import (
    CRAFT_COMPLEXITY,
    PricePredictRequest,
    PricePredictResponse,
    VisionOutput,
    VoiceOutput,
)
from ml.feature_extractor import extract_features
from ml.price_predictor import predict

router = APIRouter(
    prefix="/api/price",
    tags=["Price Prediction  (Step 3 of 3)"],
)


@router.get(
    "/pipeline-state",
    summary="Get Current Auto-Extracted Vision & Voice State",
)
def get_pipeline_state():
    """
    Returns the latest Vision analysis and Voice transcription stored in server memory.
    As soon as you run Step 1 or Step 2, this state updates automatically!
    """
    return {
        "success": True,
        "state": pipeline_state.get_combined_state(),
        "ready_for_prediction": (
            pipeline_state.get_vision() is not None or pipeline_state.get_voice() is not None
        ),
    }


@router.post(
    "/predict",
    response_model=PricePredictResponse,
    summary="Predict Price (Auto-extracts from Vision & Voice Models or accepts JSON)",
)
def predict_price(body: PricePredictRequest = Body(default_factory=PricePredictRequest)):
    """
    ## Step 3 of 3 — Predict Fair Market Price

    **⚡ Fully Automatic Mode:**
    If you ran:
      - `POST /api/vision/analyze` (Step 1)
      - `POST /api/voice/transcribe` (Step 2)

    You can simply submit `{}` or leave fields empty! The system will **automatically extract**
    the detected craft, materials, product type, and voice transcription from the server session.

    **Manual Override Mode:**
    You can also explicitly supply `vision_output` and `voice_output` JSON in the body.
    """
    if body is None:
        body = PricePredictRequest()

    # ── 1. Resolve Vision Output (Body or Auto-State) ───────────────────────
    vision_source = "provided_in_request"
    v = body.vision_output
    if v is None or (not v.craft and not v.product_type):
        cached_vision = pipeline_state.get_vision()
        if cached_vision:
            v = VisionOutput.model_validate(cached_vision)
            vision_source = "auto_extracted_from_vision_model"
        else:
            v = v or VisionOutput()
            vision_source = "default_fallback"

    # ── 2. Resolve Voice Output (Body or Auto-State) ────────────────────────
    voice_source = "provided_in_request"
    a = body.voice_output
    if a is None or not a.text:
        cached_voice = pipeline_state.get_voice()
        if cached_voice:
            a = VoiceOutput.model_validate(cached_voice)
            voice_source = "auto_extracted_from_voice_model"
        else:
            a = a or VoiceOutput()
            voice_source = "default_fallback"

    # ── 3. Extract core fields from Vision & Voice ───────────────────────────
    craft = (v.craft or "Handicraft").strip()
    material = (v.material or "Mixed").strip()
    product_type = (v.product_type or craft).strip()
    region = (v.possible_region or "Rajasthan").strip()

    # Build description from voice transcript OR visual description
    transcript = (a.text or "").strip()
    description = transcript if transcript else (v.visual_description or f"Handcrafted {craft}")

    # Product name from transcript or craft + product type
    product_name = transcript if transcript else f"{craft} {product_type}".strip()

    # Technique from craftsmanship features (first one if available)
    technique = "Traditional"
    if v.craftsmanship_features:
        technique = v.craftsmanship_features[0]

    # Auto-derive all cost and complexity features
    complexity = CRAFT_COMPLEXITY.get(craft.lower().strip(), 6.5)
    labor_days = 3.0          # default estimate
    material_cost = 500.0     # default estimate
    labor_cost = round(labor_days * 350.0, 2)
    overhead = round(material_cost * 0.25, 2)
    demand_score = round(min(10.0, complexity * 0.9 + 1.0), 2)

    ai_data = {
        "productName": product_name,
        "craft": craft,
        "material": material,
        "technique": technique,
        "description": description,
    }

    artisan_data = {
        "state": region if region.lower() != "unknown" else "Rajasthan",
        "region": region if region.lower() != "unknown" else "Jaipur",
        "district": region if region.lower() != "unknown" else "Jaipur",
        "size_length_cm": 20.0,
        "size_width_cm": 20.0,
        "size_height_cm": 30.0,
        "weight_kg": 1.8,
        "labor_days": labor_days,
        "artisan_skill_level": "Skilled",
        "production_quantity": 10,
        "market_channel": "Artisan Direct",
    }

    derived_data = {
        "product_type": product_type,
        "material_cost_inr": material_cost,
        "labor_hours": labor_days * 8.0,
        "complexity_score": complexity,
        "labor_cost_inr": labor_cost,
        "overhead_cost_inr": overhead,
        "market_demand_score": demand_score,
        "seasonality_score": 5.0,
    }

    try:
        features = extract_features(
            ai_data=ai_data,
            artisan_data=artisan_data,
            derived_data=derived_data,
        )
        price = predict(features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PricePredictResponse(
        success=True,
        predicted_price_inr=round(price, 2),
        features_used={
            **features,
            "_pipeline_summary": {
                "vision_source": vision_source,
                "voice_source": voice_source,
                "step1_craft_detected": craft,
                "step1_material_detected": material,
                "step1_product_type": product_type,
                "step1_region": region,
                "step1_confidence": v.confidence,
                "step2_voice_transcript": transcript or "(no transcript)",
                "step2_voice_language": a.language,
                "auto_complexity_score": complexity,
                "auto_labor_cost_inr": labor_cost,
                "auto_overhead_cost_inr": overhead,
                "auto_demand_score": demand_score,
            },
        },
    )
