import pandas as pd
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "feature_base.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "model_dataset.csv"
)

df = pd.read_csv(INPUT_PATH)

print("Input shape:", df.shape)


# --------------------------------------------------
# Function to calculate market reference features
# --------------------------------------------------

def get_market_stats(row, dataframe):

    # Level 1: most specific
    conditions = (
        (dataframe["craft"] == row["craft"]) &
        (dataframe["material"] == row["material"]) &
        (dataframe["technique"] == row["technique"]) &
        (dataframe["size"] == row["size"]) &
        (dataframe["region"] == row["region"]) &
        (dataframe["record_id"] != row["record_id"])
    )

    comparable = dataframe[conditions]

    # Level 2 fallback
    if len(comparable) < 10:
        conditions = (
            (dataframe["craft"] == row["craft"]) &
            (dataframe["material"] == row["material"]) &
            (dataframe["technique"] == row["technique"]) &
            (dataframe["size"] == row["size"]) &
            (dataframe["record_id"] != row["record_id"])
        )

        comparable = dataframe[conditions]

    # Level 3 fallback
    if len(comparable) < 10:
        conditions = (
            (dataframe["craft"] == row["craft"]) &
            (dataframe["material"] == row["material"]) &
            (dataframe["technique"] == row["technique"]) &
            (dataframe["record_id"] != row["record_id"])
        )

        comparable = dataframe[conditions]

    # Level 4 fallback
    if len(comparable) < 10:
        conditions = (
            (dataframe["craft"] == row["craft"]) &
            (dataframe["record_id"] != row["record_id"])
        )

        comparable = dataframe[conditions]

    prices = comparable["actual_selling_price"]

    return pd.Series({
        "market_reference_price": prices.median(),
        "market_price_min": prices.min(),
        "market_price_max": prices.max(),
        "market_comparable_count": len(prices)
    })


# --------------------------------------------------
# Create market features
# --------------------------------------------------

market_features = df.apply(
    lambda row: get_market_stats(row, df),
    axis=1
)

df = pd.concat(
    [df, market_features],
    axis=1
)


# --------------------------------------------------
# Validation
# --------------------------------------------------

print("\nMissing values in market features:")
print(
    df[
        [
            "market_reference_price",
            "market_price_min",
            "market_price_max",
            "market_comparable_count"
        ]
    ]
    .isnull()
    .sum()
)

print(
    "\nComparable count statistics:"
)

print(
    df["market_comparable_count"]
    .describe()
)


# --------------------------------------------------
# Save final Phase 3 dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved final model dataset:")
print(OUTPUT_PATH)

print("\nFinal shape:")
print(df.shape)