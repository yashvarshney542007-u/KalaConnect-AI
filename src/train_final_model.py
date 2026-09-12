import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score
)

from catboost import CatBoostRegressor


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "feature_base.csv"
)

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "catboost_price_model_final.cbm"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("Dataset shape:", df.shape)


# --------------------------------------------------
# Split FIRST
# --------------------------------------------------

train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=42
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=42
)

print("\nSplit sizes:")
print("Train:", len(train_df))
print("Validation:", len(val_df))
print("Test:", len(test_df))


# --------------------------------------------------
# Leakage-safe market feature function
# --------------------------------------------------

def get_market_reference_features(row, reference_df):

    levels = [

        [
            "craft",
            "material",
            "technique",
            "size",
            "region"
        ],

        [
            "craft",
            "material",
            "technique",
            "size"
        ],

        [
            "craft",
            "material",
            "technique"
        ],

        [
            "craft"
        ]
    ]

    comparable = None

    for cols in levels:

        mask = pd.Series(
            True,
            index=reference_df.index
        )

        for col in cols:

            mask &= (
                reference_df[col]
                ==
                row[col]
            )

        comparable = reference_df[mask]

        if len(comparable) >= 10:
            break


    prices = comparable[
        "actual_selling_price"
    ]

    return pd.Series({

        "market_reference_price":
            prices.median(),

        "market_price_min":
            prices.min(),

        "market_price_max":
            prices.max(),

        "market_comparable_count":
            len(prices)
    })


# --------------------------------------------------
# Training market features
# --------------------------------------------------

# IMPORTANT:
# For training rows, remove self from comparison.

def get_train_market_features(row):

    reference = train_df[
        train_df["record_id"]
        != row["record_id"]
    ]

    return get_market_reference_features(
        row,
        reference
    )


print(
    "\nGenerating training market features..."
)

train_market = train_df.apply(
    get_train_market_features,
    axis=1
)

train_df = pd.concat(
    [
        train_df.reset_index(drop=True),
        train_market.reset_index(drop=True)
    ],
    axis=1
)


# --------------------------------------------------
# Validation market features
# --------------------------------------------------

print(
    "Generating validation market features..."
)

val_market = val_df.apply(
    lambda row:
        get_market_reference_features(
            row,
            train_df
        ),
    axis=1
)

val_df = pd.concat(
    [
        val_df.reset_index(drop=True),
        val_market.reset_index(drop=True)
    ],
    axis=1
)


# --------------------------------------------------
# Test market features
# --------------------------------------------------

print(
    "Generating test market features..."
)

test_market = test_df.apply(
    lambda row:
        get_market_reference_features(
            row,
            train_df
        ),
    axis=1
)

test_df = pd.concat(
    [
        test_df.reset_index(drop=True),
        test_market.reset_index(drop=True)
    ],
    axis=1
)


# --------------------------------------------------
# Validation checks
# --------------------------------------------------

market_cols = [
    "market_reference_price",
    "market_price_min",
    "market_price_max",
    "market_comparable_count"
]

for name, part in [
    ("train", train_df),
    ("validation", val_df),
    ("test", test_df)
]:

    missing = (
        part[market_cols]
        .isnull()
        .sum()
        .sum()
    )

    print(
        f"{name} market-feature missing values:",
        missing
    )

    assert missing == 0


# --------------------------------------------------
# Feature selection
# --------------------------------------------------

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
    "market_comparable_count"
]


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
    "customization"
]


X_train = train_df[features]
y_train = train_df[TARGET]

X_val = val_df[features]
y_val = val_df[TARGET]

X_test = test_df[features]
y_test = test_df[TARGET]


# --------------------------------------------------
# Model
# --------------------------------------------------

model = CatBoostRegressor(

    iterations=1000,

    learning_rate=0.05,

    depth=8,

    loss_function="RMSE",

    eval_metric="RMSE",

    random_seed=42,

    verbose=100
)


# --------------------------------------------------
# Train
# --------------------------------------------------

print("\nTraining final CatBoost model...")

model.fit(

    X_train,
    y_train,

    cat_features=categorical_features,

    eval_set=(X_val, y_val),

    early_stopping_rounds=100
)


# --------------------------------------------------
# Predict
# --------------------------------------------------

predictions = model.predict(
    X_test
)


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

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


print("\nFINAL MODEL PERFORMANCE")

print(
    f"MAE: ₹{mae:.2f}"
)

print(
    f"RMSE: ₹{rmse:.2f}"
)

print(
    f"Median Absolute Error: "
    f"₹{medae:.2f}"
)

print(
    f"R²: {r2:.4f}"
)


# --------------------------------------------------
# Save predictions
# --------------------------------------------------

results = test_df[
    [
        "record_id",
        "craft",
        "material",
        "technique",
        "size",
        "region",
        "actual_selling_price"
    ]
].copy()

results["predicted_price"] = predictions

results["absolute_error"] = abs(
    results["actual_selling_price"]
    - results["predicted_price"]
)

results[
    "predicted_price"
] = predictions

results[
    "absolute_error"
] = abs(
    results[
        "actual_selling_price"
    ]
    -
    results[
        "predicted_price"
    ]
)


results_path = (
    BASE_DIR
    / "reports"
    / "test_predictions.csv"
)

results_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

results.to_csv(
    results_path,
    index=False
)


# --------------------------------------------------
# Save model
# --------------------------------------------------

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

model.save_model(
    MODEL_PATH
)

print("\nFinal model saved to:")
print(MODEL_PATH)

print("\nPredictions saved to:")
print(results_path)

test_feature_path = (
    BASE_DIR
    / "reports"
    / "final_test_features.csv"
)

final_test_features = X_test.copy()

final_test_features[
    "actual_selling_price"
] = y_test.values

final_test_features.to_csv(
    test_feature_path,
    index=False
)

print(
    "\nFinal test features saved to:"
)

print(
    test_feature_path
)