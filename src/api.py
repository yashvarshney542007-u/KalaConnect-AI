from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import pandas as pd
from catboost import CatBoostRegressor
from fastapi import Depends, FastAPI, Header, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from feature_engineering import get_market_reference_features
from market_comparison import compare_with_market


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
MODEL_PATH = BASE_DIR / "models" / "catboost_price_model_final.cbm"
REFERENCE_PATH = BASE_DIR / "data" / "processed" / "feature_base.csv"

FEATURES = [
    "product", "category", "subcategory", "craft", "material", "technique",
    "state", "region", "size", "complexity", "customization", "labor_hours",
    "raw_material_cost", "packaging_cost", "transport_cost", "direct_cost",
    "market_reference_price", "market_price_min", "market_price_max",
    "market_comparable_count",
]

CATEGORICAL_FEATURES = [
    "product", "category", "subcategory", "craft", "material", "technique",
    "state", "region", "size", "complexity", "customization",
]


class PredictionRequest(BaseModel):
    product: str = Field(min_length=1)
    category: str = Field(min_length=1)
    subcategory: str = Field(min_length=1)
    craft: str = Field(min_length=1)
    material: str = Field(min_length=1)
    technique: str = Field(min_length=1)
    state: str = Field(min_length=1)
    region: str = Field(min_length=1)
    size: str = Field(min_length=1)
    complexity: str = Field(min_length=1)
    customization: str = Field(min_length=1)
    labor_hours: float = Field(gt=0)
    raw_material_cost: float = Field(ge=0)
    packaging_cost: float = Field(ge=0)
    transport_cost: float = Field(ge=0)
    direct_cost: float = Field(ge=0)


class PredictionResponse(BaseModel):
    predicted_price: float
    currency: Literal["INR"] = "INR"
    market_analysis: dict[str, object]


app = FastAPI(
    title="KalaConnect AI Price Prediction API",
    version="1.0.0",
)

model = CatBoostRegressor()
model.load_model(MODEL_PATH)
market_df = pd.read_csv(REFERENCE_PATH).rename(
    columns={"actual_selling_price": "price"}
)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require a key only when API_KEY is configured for the deployment."""
    configured_key = os.getenv("API_KEY")
    if configured_key and x_api_key != configured_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": MODEL_PATH.name}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    dependencies=[Depends(require_api_key)],
)
def predict(request: PredictionRequest) -> PredictionResponse:
    input_data = request.model_dump()

    try:
        market_features = get_market_reference_features(input_data, market_df)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    model_input = pd.DataFrame([{**input_data, **market_features}], columns=FEATURES)
    predicted_price = float(model.predict(model_input)[0])

    market_analysis = compare_with_market(
        craft=request.craft,
        material=request.material,
        technique=request.technique,
        size=request.size,
        region=request.region,
        predicted_price=predicted_price,
    )

    return PredictionResponse(
        predicted_price=round(predicted_price, 2),
        market_analysis=market_analysis,
    )