import pandas as pd

from pathlib import Path

from sklearn.model_selection import train_test_split

from catboost import CatBoostRegressor

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model_dataset.csv"
)

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)

TARGET = "actual_selling_price"

features = [
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

X = df[features]

y = df[TARGET]

categorical_features = [
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
]

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42
)

print("Training rows:", len(X_train))
print("Validation rows:", len(X_val))
print("Test rows:", len(X_test))

model = CatBoostRegressor(

    iterations=800,

    learning_rate=0.05,

    depth=8,

    loss_function="RMSE",

    eval_metric="RMSE",

    random_seed=42,

    verbose=100
)

model.fit(

    X_train,
    y_train,

    cat_features=categorical_features,

    eval_set=(X_val, y_val),

    early_stopping_rounds=100
)

predictions = model.predict(X_test)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score
)

import numpy as np

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

medae = median_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)

print("\nMODEL PERFORMANCE")
print("MAE:", mae)
print("RMSE:", rmse)
print("Median Absolute Error:", medae)
print("R²:", r2)

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "catboost_price_model.cbm"
)

model.save_model(MODEL_PATH)

print("Model saved to:")
print(MODEL_PATH)
