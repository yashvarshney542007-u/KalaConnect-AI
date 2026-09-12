"""
data_pipeline/generate_dataset.py
=================================
Generates a realistic, domain-grounded synthetic dataset for Indian handicraft price prediction.
Target: 16,000 rows across 32 authentic Indian crafts and 81 product categories.

Adheres strictly to:
- Real geographical authenticity
- Plausible physical dimensions and weights
- Defensible cost-plus economic pricing with craft/skill/channel adjustments
- Real market anchor ranges
- Provenance tracking with source registry foreign keys
- Complete reproducibility (fixed seed)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd

from data_pipeline.craft_catalog import CRAFT_CATALOG, SKILL_LEVELS, MARKET_CHANNELS


def generate_handicraft_dataset(
    target_rows: int = 16000,
    seed: int = 42,
    output_dir: Path | str = "data/processed",
) -> pd.DataFrame:
    """Generates the full synthetic Indian handicraft dataset."""
    rng = np.random.default_rng(seed)
    records = []

    # Calculate rows per craft to ensure balanced representation
    num_crafts = len(CRAFT_CATALOG)
    base_rows_per_craft = target_rows // num_crafts
    remainder = target_rows % num_crafts

    skill_probs = [0.20, 0.50, 0.22, 0.08]  # Apprentice, Skilled, Master, National Awardee
    channel_probs = [0.22, 0.20, 0.22, 0.22, 0.08, 0.06]  # Channels

    curr_id = 1

    for craft_idx, craft_info in enumerate(CRAFT_CATALOG):
        craft_name = craft_info["craft"]
        state = craft_info["state"]
        region = craft_info["region"]
        district = craft_info["district"]
        source_id = craft_info["source_id"]
        source_ref = craft_info["source_reference"]
        products = craft_info["products"]

        rows_for_this_craft = base_rows_per_craft + (1 if craft_idx < remainder else 0)

        for _ in range(rows_for_this_craft):
            # Select product template
            prod_template = rng.choice(products)
            prod_type = prod_template["product_type"]
            material = prod_template["material"]
            technique = prod_template["technique"]

            # Select skill level
            skill_dict = rng.choice(SKILL_LEVELS, p=skill_probs)
            skill_level = skill_dict["level"]
            daily_wage_base = skill_dict["daily_wage_inr"]
            skill_mult = skill_dict["wage_multiplier"]
            complexity_adj = skill_dict["complexity_adj"]

            # Select market channel
            channel_dict = rng.choice(MARKET_CHANNELS, p=channel_probs)
            market_channel = channel_dict["channel"]
            channel_markup = channel_dict["markup_multiplier"]
            overhead_pct = channel_dict["overhead_percent"]

            # Physical specifications (truncated normal around middle)
            len_min, len_max = prod_template["length_cm"]
            wid_min, wid_max = prod_template["width_cm"]
            hgt_min, hgt_max = prod_template["height_cm"]
            wt_min, wt_max = prod_template["weight_kg"]

            scale_factor = rng.uniform(0.0, 1.0)
            # Correlate dimensions somewhat with scale factor
            size_length_cm = round(len_min + scale_factor * (len_max - len_min) * rng.uniform(0.9, 1.1), 1)
            size_length_cm = float(np.clip(size_length_cm, len_min, len_max))

            size_width_cm = round(wid_min + scale_factor * (wid_max - wid_min) * rng.uniform(0.9, 1.1), 1)
            size_width_cm = float(np.clip(size_width_cm, wid_min, wid_max))

            size_height_cm = round(hgt_min + scale_factor * (hgt_max - hgt_min) * rng.uniform(0.9, 1.1), 1)
            size_height_cm = float(np.clip(size_height_cm, hgt_min, hgt_max))

            # Weight scales roughly with volume
            vol_ratio = (size_length_cm * size_width_cm * size_height_cm) / (len_max * wid_max * hgt_max)
            vol_ratio = float(np.clip(vol_ratio, 0.1, 1.0))
            weight_kg = round(wt_min + vol_ratio * (wt_max - wt_min) * rng.uniform(0.92, 1.08), 3)
            weight_kg = float(np.clip(weight_kg, wt_min, wt_max))

            # Labor specifications
            lab_min, lab_max = prod_template["labor_days"]
            base_days = lab_min + vol_ratio * (lab_max - lab_min)
            # Master craftsmen work with higher precision / intricacy
            labor_days = round(base_days * rng.uniform(0.90, 1.15) * (1.0 + (skill_mult - 1.0) * 0.15), 1)
            labor_days = max(0.2, labor_days)

            hours_per_day = rng.uniform(7.2, 8.5)
            labor_hours = round(labor_days * hours_per_day, 1)

            # Complexity score (1.0 - 10.0)
            base_comp = prod_template["base_complexity"]
            complexity_score = round(
                np.clip(base_comp * complexity_adj * rng.uniform(0.93, 1.07), 1.0, 10.0), 1
            )

            # Material cost (scales with dimensions and quality)
            mat_min, mat_max = prod_template["material_cost_range"]
            material_cost = mat_min + vol_ratio * (mat_max - mat_min) * rng.uniform(0.90, 1.10)
            if skill_level in ("Master Craftsman", "National Awardee"):
                material_cost *= rng.uniform(1.05, 1.20)  # finer grade materials
            material_cost_inr = round(float(material_cost), 2)

            # Labor cost
            daily_wage = daily_wage_base * rng.uniform(0.95, 1.08)
            labor_cost_inr = round(float(labor_days * daily_wage), 2)

            # Overhead cost (utilities, fuel/firing, tools, packing, local freight)
            overhead_cost_inr = round(float((material_cost_inr + labor_cost_inr) * overhead_pct * rng.uniform(0.9, 1.15)), 2)

            # Production quantity (batch size / annual capacity: high for toys/coasters, low for carpets/Tanjore)
            if labor_days > 30:
                production_quantity = int(rng.integers(2, 12))
            elif labor_days > 10:
                production_quantity = int(rng.integers(8, 35))
            elif labor_days > 3:
                production_quantity = int(rng.integers(25, 120))
            else:
                production_quantity = int(rng.integers(80, 500))

            # Market demand and seasonality
            base_demand = prod_template["demand_score"]
            market_demand_score = round(float(np.clip(base_demand + rng.normal(0, 0.7), 1.0, 10.0)), 1)

            base_season = prod_template["seasonality_score"]
            seasonality_score = round(float(np.clip(base_season + rng.normal(0, 0.6), 1.0, 10.0)), 1)

            # -------------------------------------------------------------------
            # PRICING MECHANISM
            # -------------------------------------------------------------------
            production_cost = material_cost_inr + labor_cost_inr + overhead_cost_inr

            # Craft complexity premium
            complexity_factor = 1.0 + (complexity_score - 1.0) * 0.05

            # Skill reputation premium
            if skill_level == "National Awardee":
                skill_premium = rng.uniform(1.35, 1.65)
            elif skill_level == "Master Craftsman":
                skill_premium = rng.uniform(1.18, 1.35)
            elif skill_level == "Skilled":
                skill_premium = rng.uniform(1.05, 1.15)
            else:
                skill_premium = 1.0

            # Demand elasticity adjustment
            demand_adj = 1.0 + (market_demand_score - 5.0) * 0.025 + (seasonality_score - 5.0) * 0.015

            # Base market price formula
            unanchored_price = production_cost * complexity_factor * skill_premium * channel_markup * demand_adj

            # Calibrate against documented real market anchors
            anch_min, anch_max = prod_template["anchor_price_range"]
            # Target anchor point based on position in range
            target_anchor = anch_min + vol_ratio * (anch_max - anch_min) * skill_premium * (channel_markup / 1.48)

            # Blend unanchored cost-plus with market anchor
            blended_price = 0.55 * unanchored_price + 0.45 * target_anchor

            # Introduce controlled log-normal residual variance (8-10%)
            jitter = rng.lognormal(mean=0.0, sigma=0.08)
            final_price = blended_price * jitter

            # Guarantee that price exceeds production cost (healthy artisan margin)
            min_floor = production_cost * 1.08
            final_price = max(min_floor, final_price)
            price_inr = round(float(final_price), 2)

            # Product name generation
            product_id = f"IND-CRF-{curr_id:05d}"
            curr_id += 1

            product_name = f"{district} {craft_name} {prod_type}"

            confidence_score = round(float(rng.uniform(0.91, 0.98)), 2)

            records.append({
                "product_id": product_id,
                "product_name": product_name,
                "craft": craft_name,
                "product_type": prod_type,
                "material": material,
                "technique": technique,
                "state": state,
                "region": region,
                "district": district,
                "size_length_cm": size_length_cm,
                "size_width_cm": size_width_cm,
                "size_height_cm": size_height_cm,
                "weight_kg": weight_kg,
                "labor_days": labor_days,
                "labor_hours": labor_hours,
                "artisan_skill_level": skill_level,
                "complexity_score": complexity_score,
                "material_cost_inr": material_cost_inr,
                "labor_cost_inr": labor_cost_inr,
                "overhead_cost_inr": overhead_cost_inr,
                "market_demand_score": market_demand_score,
                "seasonality_score": seasonality_score,
                "production_quantity": production_quantity,
                "market_channel": market_channel,
                "price_inr": price_inr,
                "currency": "INR",
                "data_type": "synthetic",
                "source_id": source_id,
                "source_reference": source_ref,
                "confidence_score": confidence_score,
            })

    df = pd.DataFrame(records)

    # Shuffle the dataset with fixed seed
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    # Re-assign sequential IDs after shuffle
    df["product_id"] = [f"IND-CRF-{i+1:05d}" for i in range(len(df))]

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "indian_handicraft_price_dataset.csv"
    parquet_path = out_dir / "indian_handicraft_price_dataset.parquet"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_parquet(parquet_path, index=False)

    print(f"Generated {len(df)} records across {df['craft'].nunique()} crafts.")
    print(f"Saved CSV to: {csv_path}")
    print(f"Saved Parquet to: {parquet_path}")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic Indian handicraft pricing dataset")
    parser.add_argument("--rows", type=int, default=16000, help="Number of records to generate (default: 16000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--out", type=str, default="data/processed", help="Output directory")
    args = parser.parse_args()

    generate_handicraft_dataset(target_rows=args.rows, seed=args.seed, output_dir=args.out)
