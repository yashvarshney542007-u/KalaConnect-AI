import pandas as pd

from ml.feature_schema import (
    TARGET_COLUMN,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    FEATURE_COLUMNS,
)


DATASET_PATH = "data/processed/indian_handicraft_price_dataset.csv"


def validate_schema(df: pd.DataFrame):

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print("✓ All required columns exist")

    # Check categorical columns
    for column in CATEGORICAL_FEATURES:
        if not pd.api.types.is_object_dtype(df[column]):
            print(
                f"WARNING: {column} is not object/string "
                f"type: {df[column].dtype}"
            )

    # Check numerical columns
    for column in NUMERICAL_FEATURES:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"{column} must be numeric, "
                f"got {df[column].dtype}"
            )

    # Check target
    if not pd.api.types.is_numeric_dtype(df[TARGET_COLUMN]):
        raise ValueError(
            f"{TARGET_COLUMN} must be numeric"
        )

    # Missing values
    missing_values = df[
        required_columns
    ].isnull().sum()

    if missing_values.sum() > 0:
        print("\nMissing values:")
        print(
            missing_values[
                missing_values > 0
            ]
        )
        raise ValueError(
            "Dataset contains missing values"
        )

    # Target sanity
    if (df[TARGET_COLUMN] <= 0).any():
        raise ValueError(
            "price_inr contains zero/negative values"
        )

    print("✓ No missing values")
    print("✓ Target values are positive")
    print("✓ Schema validation successful")

    print("\nFeatures:")
    for feature in FEATURE_COLUMNS:
        print(f"  - {feature}")

    print(f"\nTarget: {TARGET_COLUMN}")


if __name__ == "__main__":

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}\n")

    validate_schema(df)