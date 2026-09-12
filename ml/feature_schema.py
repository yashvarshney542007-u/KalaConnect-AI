# ml/feature_schema.py

TARGET_COLUMN = "price_inr"

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

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
