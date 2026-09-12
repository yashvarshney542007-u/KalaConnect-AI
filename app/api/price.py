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

from fastapi import APIRouter, HTTPException

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
    derived/computed fields.  Returns the CatBoost model's prediction.
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
