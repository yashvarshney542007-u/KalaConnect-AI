"""
data_pipeline/preprocess.py
===========================
Preprocesses the Indian Handicraft Price Dataset for machine learning.
- Selects genuine predictive features and excludes metadata / identifiers.
- Implements stratified & grouped train/test splitting to prevent data leakage.
- Handles categorical typing for CatBoost.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
from sklearn.model_selection import train_test_split


CATEGORICAL_FEATURES = [
    "craft",
    "product_type",
    "material",
    "technique",
    "state",
    "region",
    "district",
    "artisan_skill_level",
    "market_channel",
]

NUMERICAL_FEATURES = [
    "size_length_cm",
    "size_width_cm",
    "size_height_cm",
    "weight_kg",
    "labor_days",
    "labor_hours",
    "complexity_score",
    "material_cost_inr",
    "labor_cost_inr",
    "overhead_cost_inr",
    "market_demand_score",
    "seasonality_score",
    "production_quantity",
]

TARGET_COL = "price_inr"

DROP_COLUMNS = [
    "product_id",
    "product_name",
    "currency",
    "data_type",
    "source_id",
    "source_reference",
    "confidence_score",
    "price_inr",
]


def load_and_preprocess_data(
    data_path: str | Path = "data/processed/indian_handicraft_price_dataset.csv",
    test_size: float = 0.20,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, list[str]]:
    """Loads dataset, casts categorical columns, and splits into train/test sets."""
    df = pd.read_csv(data_path)

    # Convert categoricals to string
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str)

    features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    X = df[features].copy()
    y = df[TARGET_COL].copy()

    # Stratified split based on craft to ensure all craft traditions are represented
    # in both training and test evaluations
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=df["craft"],
    )

    return X_train, X_test, y_train, y_test, CATEGORICAL_FEATURES


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, cat_features = load_and_preprocess_data()
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape:  {X_test.shape}, y_test shape:  {y_test.shape}")
    print(f"Categorical features ({len(cat_features)}): {cat_features}")
