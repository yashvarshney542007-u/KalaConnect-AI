"""
train.py
=======
Script to train a CatBoostRegressor on the Indian Handicraft Price dataset.
It loads preprocessed data from the data pipeline, fits the model, evaluates basic metrics,
and saves the trained model to the `models/` directory.
"""

import argparse
import sys
from pathlib import Path
# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from pathlib import Path
import joblib
from catboost import CatBoostRegressor

# Import the data loading utility
from data_pipeline.preprocess import load_and_preprocess_data


def train_model(
    data_path: str | Path = "data/processed/indian_handicraft_price_dataset.csv",
    test_size: float = 0.2,
    random_state: int = 42,
    model_output: str | Path = "models/catboost_handicraft_model.cbm",
    iterations: int = 1000,
    learning_rate: float = 0.05,
    depth: int = 8,
) -> None:
    """Train CatBoostRegressor and persist the model.

    Parameters
    ----------
    data_path: location of the processed CSV.
    test_size: proportion of data for test split.
    random_state: reproducibility seed.
    model_output: where to write the trained model.
    iterations, learning_rate, depth: CatBoost hyper‑parameters.
    """
    # Load and split data
    X_train, X_test, y_train, y_test, cat_features = load_and_preprocess_data(
        data_path=data_path, test_size=test_size, random_state=random_state
    )

    # Initialise CatBoostRegressor with categorical feature handling
    model = CatBoostRegressor(
        iterations=iterations,
        learning_rate=learning_rate,
        depth=depth,
        loss_function="RMSE",
        cat_features=cat_features,
        verbose=False,
        random_seed=random_state,
    )

    model.fit(X_train, y_train)

    # Simple evaluation on the test set
    preds = model.predict(X_test)
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, preds)
    print(f"Test MAE: {mae:.2f} INR")
    print(f"Test RMSE: {rmse:.2f} INR")
    print(f"Test R²: {r2:.4f}")

    # Ensure output directory exists
    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    # Save the CatBoost model (native format)
    model.save_model(str(model_path))
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CatBoost model for Handicraft price prediction")
    parser.add_argument("--data-path", type=str, default="data/processed/indian_handicraft_price_dataset.csv")
    parser.add_argument("--model-output", type=str, default="models/catboost_handicraft_model.cbm")
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--depth", type=int, default=8)
    args = parser.parse_args()

    train_model(
        data_path=args.data_path,
        model_output=args.model_output,
        iterations=args.iterations,
        learning_rate=args.learning_rate,
        depth=args.depth,
    )