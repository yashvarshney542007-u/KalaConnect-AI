from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor

from src.feature_engineering import get_market_reference_features


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# ML files
MODEL_PATH = BASE_DIR / "models" / "catboost_price_model_final.cbm"
REFERENCE_PATH = BASE_DIR / "data" / "processed" / "feature_base.csv"


# Exact feature order used during model training
FEATURES = [
    "product",
    "category",
    "subcategory",
    "craft",
    "material",
    "technique",
    "state",
    "region",
    "size",
    "complexity",
    "customization",
    "labor_hours",
    "raw_material_cost",
    "packaging_cost",
    "transport_cost",
    "direct_cost",
    "market_reference_price",
    "market_price_min",
    "market_price_max",
    "market_comparable_count",
]


class PricingService:
    """
    Handles KalaConnect ML price prediction.
    """

    def __init__(self):
        self.model = CatBoostRegressor()
        self.model.load_model(str(MODEL_PATH))

        self.market_df = pd.read_csv(REFERENCE_PATH).rename(
            columns={"actual_selling_price": "price"}
        )

    def predict(self, input_data):
        """
        Generate a price prediction from the 16 user-supplied fields.
        """

        # Generate the 4 market-derived features
        market_features = get_market_reference_features(
            input_data,
            self.market_df,
        )

        # Combine user input + market features
        model_input = pd.DataFrame(
            [{**input_data, **market_features}],
            columns=FEATURES,
        )

        # Generate prediction
        predicted_price = float(
            self.model.predict(model_input)[0]
        )

        return {
            "predicted_price": round(predicted_price, 2),
            "market_features": market_features,
        }


# Create one reusable service instance
pricing_service = PricingService()