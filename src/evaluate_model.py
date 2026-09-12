import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score
)


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PREDICTIONS_PATH = (
    BASE_DIR
    / "reports"
    / "test_predictions.csv"
)

REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# LOAD TEST PREDICTIONS
# ==========================================

df = pd.read_csv(PREDICTIONS_PATH)

print("Test records:", len(df))
print("\nColumns:")
print(df.columns.tolist())


# ==========================================
# ACTUAL AND PREDICTED VALUES
# ==========================================

y_true = df["actual_selling_price"]

y_pred = df["predicted_price"]


# ==========================================
# METRICS
# ==========================================

mae = mean_absolute_error(
    y_true,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_true,
        y_pred
    )
)

medae = median_absolute_error(
    y_true,
    y_pred
)

r2 = r2_score(
    y_true,
    y_pred
)


print("\n==============================")
print("FINAL TEST EVALUATION")
print("==============================")

print(f"MAE: ₹{mae:.2f}")
print(f"RMSE: ₹{rmse:.2f}")
print(
    f"Median Absolute Error: ₹{medae:.2f}"
)
print(f"R²: {r2:.4f}")


# ==========================================
# ERROR COLUMNS
# ==========================================

df["error"] = (
    df["predicted_price"]
    -
    df["actual_selling_price"]
)

df["absolute_error"] = (
    df["error"].abs()
)

df["percentage_error"] = (
    df["absolute_error"]
    /
    df["actual_selling_price"]
    * 100
)


# ==========================================
# CRAFT-WISE PERFORMANCE
# ==========================================

craft_performance = (

    df.groupby("craft")

    .agg(

        products=("record_id", "count"),

        actual_median=(
            "actual_selling_price",
            "median"
        ),

        predicted_median=(
            "predicted_price",
            "median"
        ),

        mae=(
            "absolute_error",
            "mean"
        ),

        median_error=(
            "absolute_error",
            "median"
        ),

        mean_percentage_error=(
            "percentage_error",
            "mean"
        )
    )

    .sort_values("mae")
)


print("\n==============================")
print("CRAFT-WISE PERFORMANCE")
print("==============================")

print(craft_performance)


craft_performance.to_csv(

    REPORT_DIR
    / "craft_performance.csv"
)


# ==========================================
# WORST PREDICTIONS
# ==========================================

worst_predictions = (

    df.sort_values(
        "absolute_error",
        ascending=False
    )

    .head(20)
)


print("\n==============================")
print("20 WORST PREDICTIONS")
print("==============================")

print(
    worst_predictions[
        [
            "craft",
            "material",
            "technique",
            "actual_selling_price",
            "predicted_price",
            "absolute_error"
        ]
    ]
)


worst_predictions.to_csv(

    REPORT_DIR
    / "worst_predictions.csv",

    index=False
)


# ==========================================
# SAVE COMPLETE EVALUATED TEST SET
# ==========================================

df.to_csv(

    REPORT_DIR
    / "evaluated_test_predictions.csv",

    index=False
)


# ==========================================
# GRAPH 1
# ACTUAL VS PREDICTED
# ==========================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_true,
    y_pred,
    alpha=0.5
)

minimum = min(
    y_true.min(),
    y_pred.min()
)

maximum = max(
    y_true.max(),
    y_pred.max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum]
)

plt.xlabel(
    "Actual Selling Price (₹)"
)

plt.ylabel(
    "Predicted Selling Price (₹)"
)

plt.title(
    "Actual vs Predicted Prices"
)

plt.tight_layout()

plt.savefig(
    REPORT_DIR
    / "actual_vs_predicted.png",
    dpi=300
)

plt.close()


# ==========================================
# GRAPH 2
# RESIDUAL PLOT
# ==========================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_pred,
    df["error"],
    alpha=0.5
)

plt.axhline(
    y=0
)

plt.xlabel(
    "Predicted Selling Price (₹)"
)

plt.ylabel(
    "Prediction Error (₹)"
)

plt.title(
    "Residual Plot"
)

plt.tight_layout()

plt.savefig(
    REPORT_DIR
    / "residual_plot.png",
    dpi=300
)

plt.close()


# ==========================================
# GRAPH 3
# ABSOLUTE ERROR DISTRIBUTION
# ==========================================

plt.figure(figsize=(8, 6))

plt.hist(
    df["absolute_error"],
    bins=40
)

plt.xlabel(
    "Absolute Error (₹)"
)

plt.ylabel(
    "Number of Products"
)

plt.title(
    "Distribution of Prediction Errors"
)

plt.tight_layout()

plt.savefig(
    REPORT_DIR
    / "error_distribution.png",
    dpi=300
)

plt.close()


# ==========================================
# TEXT REPORT
# ==========================================

report = f"""
KALACONNECT PRICE PREDICTION
FINAL MODEL EVALUATION

Test records: {len(df)}

PERFORMANCE
------------------------------

MAE:
₹{mae:.2f}

RMSE:
₹{rmse:.2f}

Median Absolute Error:
₹{medae:.2f}

R²:
{r2:.4f}


INTERPRETATION
------------------------------

MAE represents the average absolute
difference between predicted and actual
synthetic selling prices.

RMSE penalizes large prediction errors
more heavily than MAE.

Median Absolute Error represents the
typical absolute prediction error and is
less affected by expensive outliers.

R² measures the proportion of variation
in selling prices explained by the model.


DATASET NOTE
------------------------------

The model was trained and evaluated on a
domain-informed synthetic dataset.

The synthetic price distributions were
calibrated against Indian handicraft
marketplace price ranges.

These metrics therefore measure
performance on synthetic held-out test
data and should not be presented as
validated real-world accuracy.
"""


with open(

    REPORT_DIR
    / "evaluation_report.txt",

    "w",

    encoding="utf-8"

) as file:

    file.write(report)


print("\n==============================")
print("EVALUATION COMPLETE")
print("==============================")

print("\nReports saved in:")
print(REPORT_DIR)