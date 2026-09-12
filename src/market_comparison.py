import pandas as pd
from pathlib import Path


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MARKET_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "market_data.csv"
)


# ==================================================
# LOAD MARKET DATA
# ==================================================

market_df = pd.read_csv(MARKET_PATH)

print("Market records loaded:", len(market_df))


# ==================================================
# MARKET COMPARISON FUNCTION
# ==================================================

def compare_with_market(
    craft,
    material,
    technique,
    size,
    region,
    predicted_price,
    min_comparables=10
):

    """
    Find comparable handicraft products and compare
    the AI predicted price with their market range.
    """

    # ----------------------------------------------
    # Comparison levels
    # ----------------------------------------------

    levels = [

        (
            "craft + material + technique + size + region",
            ["craft", "material", "technique", "size", "region"]
        ),

        (
            "craft + material + technique + size",
            ["craft", "material", "technique", "size"]
        ),

        (
            "craft + material + technique",
            ["craft", "material", "technique"]
        ),

        (
            "craft + material",
            ["craft", "material"]
        ),

        (
            "craft",
            ["craft"]
        )
    ]


    comparable = None
    comparison_level = None


    # ----------------------------------------------
    # Find comparable products
    # ----------------------------------------------

    input_values = {

        "craft": craft,
        "material": material,
        "technique": technique,
        "size": size,
        "region": region
    }


    for level_name, columns in levels:

        mask = pd.Series(
            True,
            index=market_df.index
        )

        for column in columns:

            mask &= (
                market_df[column]
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                str(
                    input_values[column]
                )
                .strip()
                .lower()
            )


        candidate_products = market_df[mask]


        if len(candidate_products) >= min_comparables:

            comparable = candidate_products

            comparison_level = level_name

            break


    # ----------------------------------------------
    # Final fallback
    # ----------------------------------------------

    if comparable is None:

        mask = (

            market_df["craft"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            str(craft)
            .strip()
            .lower()
        )

        comparable = market_df[mask]

        comparison_level = "craft fallback"


    # ----------------------------------------------
    # No comparable products
    # ----------------------------------------------

    if len(comparable) == 0:

        return {

            "success": False,

            "message":
                "No comparable market products found."
        }


    # ----------------------------------------------
    # Market statistics
    # ----------------------------------------------

    prices = comparable["price"]

    market_min = float(
        prices.min()
    )

    market_q1 = float(
        prices.quantile(0.25)
    )

    market_median = float(
        prices.median()
    )

    market_q3 = float(
        prices.quantile(0.75)
    )

    market_max = float(
        prices.max()
    )

    comparable_count = int(
        len(prices)
    )

    # ----------------------------------------------
    # Difference from market median
    # ----------------------------------------------

    difference = (
        predicted_price
        -
        market_median
    )


    difference_percent = (
        difference
        /
        market_median
        *
        100
    )


    # ----------------------------------------------
    # Market position
    # ----------------------------------------------

    if predicted_price < market_q1:

        position = "below_market"

        recommendation = (
            "Suggested price is below the typical "
            "market reference range."
        )

    elif predicted_price > market_q3:

        position = "above_market"

        recommendation = (
        "Suggested price is above the typical "
        "market reference range."
        )

    else:

        position = "within_market"

        recommendation = (
        "Suggested price is within the typical "
        "market reference range."
        )

    # ----------------------------------------------
    # Return result
    # ----------------------------------------------

    return {
    "success": True,

    "predicted_price": round(
        float(predicted_price), 2
    ),

    "market_min": round(
        market_min, 2
    ),

    "market_q1": round(
        market_q1, 2
    ),

    "market_median": round(
        market_median, 2
    ),

    "market_q3": round(
        market_q3, 2
    ),

    "market_max": round(
        market_max, 2
    ),

    "comparable_count": comparable_count,

    "difference_from_median": round(
        difference, 2
    ),

    "difference_percent": round(
        difference_percent, 2
    ),

    "market_position": position,

    "comparison_level": comparison_level,

    "recommendation": recommendation
}


# ==================================================
# TEST EXAMPLE
# ==================================================

if __name__ == "__main__":

    # Pick a real row from our market dataset
    example = market_df.iloc[0]

    # Temporary test:
    # use its market price as an example AI prediction
    predicted_price = float(
        example["price"]
    )


    result = compare_with_market(

        craft=example["craft"],

        material=example["material"],

        technique=example["technique"],

        size=example["size"],

        region=example["region"],

        predicted_price=predicted_price
    )


    print("\n==============================")
    print("MARKET COMPARISON")
    print("==============================")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )