from __future__ import annotations

from typing import Any

import pandas as pd


MARKET_FEATURE_COLUMNS = [
	"market_reference_price",
	"market_price_min",
	"market_price_max",
	"market_comparable_count",
]


def get_market_reference_features(
	row: dict[str, Any],
	reference_df: pd.DataFrame,
	min_comparables: int = 10,
) -> dict[str, float | int]:
	"""Calculate the same market features used by the final model."""

	levels = [
		["craft", "material", "technique", "size", "region"],
		["craft", "material", "technique", "size"],
		["craft", "material", "technique"],
		["craft"],
	]

	comparable = reference_df.iloc[0:0]
	for columns in levels:
		mask = pd.Series(True, index=reference_df.index)
		for column in columns:
			mask &= (
				reference_df[column].astype(str).str.strip().str.lower()
				== str(row[column]).strip().lower()
			)

		comparable = reference_df[mask]
		if len(comparable) >= min_comparables:
			break

	if comparable.empty:
		raise ValueError("No comparable market products found for this craft.")

	prices = comparable["price"]
	return {
		"market_reference_price": float(prices.median()),
		"market_price_min": float(prices.min()),
		"market_price_max": float(prices.max()),
		"market_comparable_count": int(len(prices)),
	}
