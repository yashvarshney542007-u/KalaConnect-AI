import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

from pathlib import Path
from catboost import CatBoostRegressor, Pool


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

REPORT_DIR = (
    BASE_DIR
    / "reports"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

# print("Dataset shape:", df.shape)


# --------------------------------------------------
# Load trained CatBoost model
# --------------------------------------------------

model = CatBoostRegressor()

model.load_model(
    MODEL_PATH
)

print("Model loaded successfully.")


# --------------------------------------------------
# Features
# IMPORTANT:
# These must match the final model's feature order.
# --------------------------------------------------

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
    "direct_cost"
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


# --------------------------------------------------
# IMPORTANT NOTE
# --------------------------------------------------
# The final model also used market-reference features.
# We therefore need the same features used during
# final training.
#
# For SHAP explanation, use model_dataset.csv if it
# contains the exact final feature columns.
# --------------------------------------------------

MODEL_DATA_PATH = (
    BASE_DIR
    / "reports"
    / "final_test_features.csv"
)


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

# --------------------------------------------------
# Load exact final test features
# --------------------------------------------------

MODEL_DATA_PATH = (
    BASE_DIR
    / "reports"
    / "final_test_features.csv"
)

model_df = pd.read_csv(MODEL_DATA_PATH)

print("SHAP dataset shape:", model_df.shape)

X = model_df[features]

y = model_df["actual_selling_price"]


# --------------------------------------------------
# Use a sample for SHAP
# --------------------------------------------------

sample_size = min(
    500,
    len(X)
)

X_sample = X.sample(
    sample_size,
    random_state=42
)

print(
    "SHAP sample size:",
    len(X_sample)
)


# --------------------------------------------------
# CatBoost Pool
# --------------------------------------------------

pool = Pool(
    X_sample,
    cat_features=categorical_features
)


# --------------------------------------------------
# Get SHAP values directly from CatBoost
# --------------------------------------------------

shap_values = model.get_feature_importance(
    pool,
    type="ShapValues"
)

# Last column is expected value / base value
shap_contributions = shap_values[:, :-1]

base_values = shap_values[:, -1]


print(
    "SHAP matrix shape:",
    shap_contributions.shape
)


# --------------------------------------------------
# Global feature importance
# --------------------------------------------------

mean_abs_shap = np.abs(
    shap_contributions
).mean(axis=0)


importance_df = pd.DataFrame({

    "feature": features,

    "mean_absolute_shap":
        mean_abs_shap
})


importance_df = (
    importance_df
    .sort_values(
        "mean_absolute_shap",
        ascending=False
    )
)


print("\nTop SHAP features:")

print(
    importance_df.head(15)
)


importance_df.to_csv(

    REPORT_DIR
    / "shap_feature_importance.csv",

    index=False
)


# --------------------------------------------------
# SHAP bar chart
# --------------------------------------------------

top_n = 15

plot_df = (
    importance_df
    .head(top_n)
    .sort_values(
        "mean_absolute_shap"
    )
)


plt.figure(
    figsize=(9, 7)
)

plt.barh(

    plot_df["feature"],

    plot_df[
        "mean_absolute_shap"
    ]
)

plt.xlabel(
    "Mean absolute SHAP value (₹ impact)"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "Global Feature Importance using SHAP"
)

plt.tight_layout()

plt.savefig(

    REPORT_DIR
    / "shap_summary.png",

    dpi=300
)

plt.close()


# --------------------------------------------------
# Explain one example product
# --------------------------------------------------

example_position = 0

example_row = X_sample.iloc[
    example_position
]

example_shap = shap_contributions[
    example_position
]

example_base = base_values[
    example_position
]


example_prediction = model.predict(
    X_sample.iloc[
        [example_position]
    ]
)[0]


example_actual = y.loc[
    example_row.name
]


example_df = pd.DataFrame({

    "feature": features,

    "feature_value":
        example_row.values,

    "shap_value":
        example_shap
})


example_df[
    "absolute_shap"
] = (
    example_df[
        "shap_value"
    ].abs()
)


example_df = (
    example_df
    .sort_values(
        "absolute_shap",
        ascending=False
    )
)


print("\n==============================")
print("EXAMPLE EXPLANATION")
print("==============================")

print(
    "Actual price:",
    example_actual
)

print(
    "Predicted price:",
    example_prediction
)

print(
    "Base value:",
    example_base
)

print("\nTop factors:")

print(
    example_df[
        [
            "feature",
            "feature_value",
            "shap_value"
        ]
    ]
    .head(10)
)


example_df.to_csv(

    REPORT_DIR
    / "shap_example_explanation.csv",

    index=False
)


# --------------------------------------------------
# Consistency check
# --------------------------------------------------

shap_sum_prediction = (
    example_base
    +
    example_shap.sum()
)


print("\nSHAP reconstructed prediction:")
print(
    shap_sum_prediction
)

print(
    "\nModel prediction:"
)

print(
    example_prediction
)


# --------------------------------------------------
# Final status
# --------------------------------------------------

print("\n==============================")
print("SHAP EXPLANATION COMPLETE")
print("==============================")

print("\nSaved:")

print(
    REPORT_DIR
    / "shap_summary.png"
)

print(
    REPORT_DIR
    / "shap_feature_importance.csv"
)

print(
    REPORT_DIR
    / "shap_example_explanation.csv"
)

model_df = pd.read_csv(
    MODEL_DATA_PATH
)

X = model_df[features]

y = model_df[
    "actual_selling_price"
]

