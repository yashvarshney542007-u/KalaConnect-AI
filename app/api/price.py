"""
app/api/price.py
================
FastAPI router for the price prediction endpoint.

POST /api/price/predict
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so ml.* imports resolve when running
# via `uvicorn app.main:app` from any working directory.
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Optional
from fastapi import APIRouter, HTTPException, File, Form, UploadFile

from app.schemas.price import PricePredictRequest, PricePredictResponse
from ml.feature_extractor import extract_features
from ml.price_predictor import predict

router = APIRouter(
    prefix="/api/price",
    tags=["Price Prediction"],
)


@router.post("/predict", response_model=PricePredictResponse)
def predict_price(body: PricePredictRequest):
    """Predict the fair market price (INR) for a handicraft item.

    Accepts structured data from the Vision AI, the artisan, and
    derived/computed fields. Returns the CatBoost model's prediction.
    """
    try:
        features = extract_features(
            ai_data=body.ai_data.model_dump(),
            artisan_data=body.artisan_data.model_dump(),
            derived_data=body.derived_data.model_dump(),
        )
        price = predict(features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PricePredictResponse(
        success=True,
        predicted_price_inr=round(price, 2),
        features_used=features,
    )


@router.post("/predict-with-media", response_model=PricePredictResponse)
async def predict_price_with_media(
    image: Optional[UploadFile] = File(None, description="Optional product photograph (JPG/PNG)"),
    audio: Optional[UploadFile] = File(None, description="Optional voice recording (WAV/MP3)"),
    product_name: str = Form("Blue Pottery Vase", description="Product Name"),
    craft: str = Form("Blue Pottery", description="Craft form (e.g. Blue Pottery, Pashmina, Wood Carving)"),
    material: str = Form("Ceramic", description="Material (e.g. Ceramic, Silk, Brass, Teak Wood)"),
    technique: str = Form("Hand-painted", description="Technique used"),
    state: str = Form("Rajasthan", description="Artisan State"),
    district: str = Form("Jaipur", description="District / Region"),
    artisan_skill_level: str = Form("Skilled", description="Skill Level: Skilled, Master, Semi-Skilled"),
    market_channel: str = Form("Artisan Direct", description="Market Channel"),
    size_length_cm: float = Form(20.0, description="Length in cm"),
    size_width_cm: float = Form(20.0, description="Width in cm"),
    size_height_cm: float = Form(30.0, description="Height in cm"),
    weight_kg: float = Form(1.8, description="Weight in kg"),
    labor_days: float = Form(3.0, description="Days of labor"),
    material_cost_inr: float = Form(500.0, description="Cost of raw materials in INR"),
    labor_cost_inr: float = Form(900.0, description="Cost of labor in INR"),
    complexity_score: float = Form(6.5, description="Craft complexity score (1 - 10)"),
):
    """Predict fair market price with direct Image & Voice file upload via Swagger Docs.

    You can attach your actual handicraft photo and voice recording right here in `/docs`!
    """
    ai_data = {
        "productName": product_name,
        "craft": craft,
        "material": material,
        "technique": technique,
        "description": f"Uploaded product with image: {image.filename if image else 'None'}, audio: {audio.filename if audio else 'None'}"
    }
    artisan_data = {
        "state": state,
        "region": district,
        "district": district,
        "size_length_cm": size_length_cm,
        "size_width_cm": size_width_cm,
        "size_height_cm": size_height_cm,
        "weight_kg": weight_kg,
        "labor_days": labor_days,
        "artisan_skill_level": artisan_skill_level,
        "production_quantity": 10,
        "market_channel": market_channel,
    }
    derived_data = {
        "product_type": craft,
        "labor_hours": labor_days * 8.0,
        "complexity_score": complexity_score,
        "material_cost_inr": material_cost_inr,
        "labor_cost_inr": labor_cost_inr,
        "overhead_cost_inr": round(material_cost_inr * 0.25, 2),
        "market_demand_score": 7.2,
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
        features_used=features,
    )
