import pandas as pd
import numpy as np

from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from ml.feature_schema import (
    TARGET_COLUMN,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
)


DATASET_PATH = "data/processed/indian_handicraft_price_dataset.csv"
MODEL_PATH = "models/catboost_handicraft_model.cbm"

RANDOM_STATE = 42


def main():

    df = pd.read_csv(DATASET_PATH)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    for column in CATEGORICAL_FEATURES:
        X[column] = X[column].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
    )

    model = CatBoostRegressor()

    model.load_model(MODEL_PATH)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions,
    )

    print("\n========== OVERALL ==========")

    print(f"MAE : ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²  : {r2:.4f}")

    # -------------------------------------------------
    # Prediction table
    # -------------------------------------------------

    results = X_test.copy()

    results["actual_price"] = y_test.values
    results["predicted_price"] = predictions

    results["absolute_error"] = (
        results["actual_price"]
        - results["predicted_price"]
    ).abs()

    results["percentage_error"] = (
        results["absolute_error"]
        / results["actual_price"]
    ) * 100

    print("\n========== SAMPLE PREDICTIONS ==========")

    print(
        results[
            [
                "actual_price",
                "predicted_price",
                "absolute_error",
                "percentage_error",
            ]
        ].head(10).to_string(index=False)
    )

    # -------------------------------------------------
    # Worst predictions
    # -------------------------------------------------

    print("\n========== WORST 10 PREDICTIONS ==========")

    worst = results.sort_values(
        "absolute_error",
        ascending=False,
    ).head(10)

    print(
        worst[
            [
                "craft",
                "product_type",
                "actual_price",
                "predicted_price",
                "absolute_error",
                "percentage_error",
            ]
        ].to_string(index=False)
    )

    # -------------------------------------------------
    # Price-band evaluation
    # -------------------------------------------------

    results["price_band"] = pd.cut(
        results["actual_price"],
        bins=[
            0,
            1000,
            5000,
            10000,
            25000,
            50000,
            float("inf"),
        ],
        labels=[
            "<1K",
            "1K-5K",
            "5K-10K",
            "10K-25K",
            "25K-50K",
            "50K+",
        ],
    )

    print("\n========== ERROR BY PRICE BAND ==========")

    grouped = results.groupby(
        "price_band",
        observed=True,
    )

    for band, group in grouped:

        band_mae = mean_absolute_error(
            group["actual_price"],
            group["predicted_price"],
        )

        print(
            f"{band}: "
            f"n={len(group)}, "
            f"MAE=₹{band_mae:,.2f}"
        )

    # -------------------------------------------------
    # Feature importance
    # -------------------------------------------------

    importance = model.get_feature_importance()

    importance_df = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": importance,
    })

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False,
    )

    print("\n========== FEATURE IMPORTANCE ==========")

    print(
        importance_df.to_string(
            index=False
        )
    )

    # -------------------------------------------------
    # Save predictions
    # -------------------------------------------------

    results.to_csv(
        "evaluation/price_predictions.csv",
        index=False,
    )

    print(
        "\nPredictions saved to "
        "evaluation/price_predictions.csv"
    )


if __name__ == "__main__":
    main()