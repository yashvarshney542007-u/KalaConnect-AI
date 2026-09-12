"""
app/api/price.py
================
FastAPI router for the price prediction endpoint.

Pipeline:
  Step 1: POST /api/vision/analyze   -> VisionOutput JSON
  Step 2: POST /api/voice/transcribe -> VoiceOutput JSON
  Step 3: POST /api/price/predict    -> paste both -> predicted price INR
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException

from app.schemas.price import (
    CRAFT_COMPLEXITY,
    PricePredictRequest,
    PricePredictResponse,
)
from ml.feature_extractor import extract_features
from ml.price_predictor import predict

router = APIRouter(
    prefix="/api/price",
    tags=["Price Prediction  (Step 3 of 3)"],
)


@router.post(
    "/predict",
    response_model=PricePredictResponse,
    summary="Predict Price from Vision + Voice AI Output",
)
def predict_price(body: PricePredictRequest):
    """
    ## Step 3 of 3 — Predict Fair Market Price

    This is the **final step** in the AI pipeline.
    Paste the outputs from Steps 1 and 2 here:

    | Step | Endpoint | What you get |
    |------|----------|-------------|
    | **1** | `POST /api/vision/analyze` | Craft, material, product type from image |
    | **2** | `POST /api/voice/transcribe` | Product name and description from voice |
    | **3** | `POST /api/price/predict` ← **you are here** | Predicted price in INR |

    The system automatically derives:
    - Complexity score from craft type
    - Labor cost, overhead cost
    - Market demand score
    - All 22 model features required by CatBoost

    No manual JSON required — just paste the Vision and Voice responses.
    """
    v = body.vision_output
    a = body.voice_output

    craft = v.craft or "Handicraft"
    material = v.material or "Mixed"
    product_type = v.product_type or craft
    region = v.possible_region or "Unknown"

    # Build description from voice transcript OR visual description
    transcript = (a.text or "").strip()
    description = transcript if transcript else (v.visual_description or f"Handcrafted {craft}")

    # Product name from transcript or craft + product type
    product_name = transcript or f"{craft} {product_type}".strip()

    # Technique from craftsmanship features (first one if available)
    technique = "Traditional"
    if v.craftsmanship_features:
        technique = v.craftsmanship_features[0]

    # Auto-derive all cost and complexity features
    complexity = CRAFT_COMPLEXITY.get(craft.lower().strip(), 6.0)
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
            "_pipeline": {
                "step1_vision_craft": craft,
                "step1_vision_material": material,
                "step1_vision_product_type": product_type,
                "step1_vision_region": region,
                "step1_vision_confidence": v.confidence,
                "step2_voice_transcript": transcript or "(no transcript)",
                "step2_voice_language": a.language,
                "auto_complexity_score": complexity,
                "auto_labor_cost_inr": labor_cost,
                "auto_overhead_cost_inr": overhead,
                "auto_demand_score": demand_score,
            },
        },
    )
