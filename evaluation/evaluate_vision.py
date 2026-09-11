"""
Vision Evaluation Script
========================

Evaluates the KalaConnect Vision AI (SmolVLM-256M-Instruct) against a
curated set of authentic artisan/craft images.

Usage
-----
From the repository root with the virtual environment active:

    python evaluation/evaluate_vision.py

or with a custom image directory / metadata file:

    python evaluation/evaluate_vision.py \\
        --images-dir evaluation/images \\
        --metadata   evaluation/metadata.csv \\
        --output-dir evaluation/results

Prerequisites
-------------
1. Add 30–50 legitimate craft images to ``evaluation/images/``.
2. Fill in ``evaluation/metadata.csv`` with the correct labels.
3. Start the FastAPI service (or call the service function directly).

The script calls the Vision service function directly (no HTTP required)
so the FastAPI server does NOT need to be running.

Metrics produced (when evaluation images are available)
-------------------------------------------------------
- total_images
- successful_analyses
- failures
- craft_accuracy         (exact string match, case-insensitive)
- material_accuracy      (exact string match, case-insensitive)
- product_type_accuracy  (exact string match, case-insensitive)
- average_confidence

Output files
------------
- evaluation/results/vision_results.csv
- evaluation/results/vision_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGES_DIR = EVAL_DIR / "images"
DEFAULT_METADATA = EVAL_DIR / "metadata.csv"
DEFAULT_RESULTS_DIR = EVAL_DIR / "results"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

CRAFT_CATEGORIES = {
    "pottery", "textile", "embroidery", "wood craft", "metal craft",
    "basketry", "jewellery", "painting", "leather craft", "stone craft",
    "unknown",
}


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def _load_metadata(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[WARN] metadata file not found: {path}")
        return []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row.get("image_id", "").strip()]
    return rows


def _call_vision(image_path: Path) -> dict:
    """
    Calls the Vision service directly (no HTTP).

    The service is lazy-loaded so the Transformers model is only
    downloaded / initialised on the first call.
    """
    # Ensure project root is importable
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from app.services.vision_service import analyze_image

    return analyze_image(str(image_path))


# ---------------------------------------------------------------------------
# Main evaluation logic
# ---------------------------------------------------------------------------

def evaluate(
    images_dir: Path,
    metadata_path: Path,
    results_dir: Path,
) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_metadata(metadata_path)

    # Find all image files in images_dir
    available_images = {
        f.name: f
        for f in images_dir.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    }

    if not rows:
        print(
            "\n[INFO] No evaluation records found in metadata.csv.\n"
            "\nTo run an evaluation:\n"
            "  1. Add authentic craft images to:  evaluation/images/\n"
            "  2. Fill in evaluation/metadata.csv with correct labels.\n"
            "  3. Re-run this script.\n"
            "\nNo metrics have been fabricated.\n"
        )
        _write_empty_summary(results_dir)
        return

    total = len(rows)
    successes = 0
    failures = 0
    craft_correct = 0
    material_correct = 0
    product_type_correct = 0
    confidence_total = 0.0

    result_rows: list[dict] = []

    print(f"\nEvaluating {total} image(s)…\n")

    for row in rows:
        filename = row.get("filename", "").strip()
        expected_craft = _norm(row.get("expected_craft", ""))
        expected_material = _norm(row.get("expected_material", ""))
        expected_product_type = _norm(row.get("expected_product_type", ""))

        image_path = available_images.get(filename)
        if image_path is None:
            print(f"  [SKIP] Image not found: {filename}")
            failures += 1
            result_rows.append({
                "image_id": row.get("image_id", ""),
                "filename": filename,
                "status": "image_not_found",
                "predicted_craft": "",
                "predicted_material": "",
                "predicted_product_type": "",
                "confidence": "",
                "craft_match": "",
                "material_match": "",
                "product_type_match": "",
            })
            continue

        try:
            analysis = _call_vision(image_path)
            successes += 1

            predicted_craft = _norm(analysis.get("craft", ""))
            predicted_material = _norm(analysis.get("material", ""))
            predicted_product_type = _norm(analysis.get("product_type", ""))
            confidence = float(analysis.get("confidence", 0.0))
            confidence_total += confidence

            craft_ok = predicted_craft == expected_craft
            material_ok = predicted_material == expected_material
            product_type_ok = predicted_product_type == expected_product_type

            if craft_ok:
                craft_correct += 1
            if material_ok:
                material_correct += 1
            if product_type_ok:
                product_type_correct += 1

            status = "ok"
            print(
                f"  [OK] {filename} — craft: {predicted_craft!r} "
                f"(expected: {expected_craft!r}), "
                f"confidence: {confidence:.2f}"
            )

            result_rows.append({
                "image_id": row.get("image_id", ""),
                "filename": filename,
                "status": status,
                "predicted_craft": predicted_craft,
                "predicted_material": predicted_material,
                "predicted_product_type": predicted_product_type,
                "confidence": f"{confidence:.4f}",
                "craft_match": str(craft_ok),
                "material_match": str(material_ok),
                "product_type_match": str(product_type_ok),
            })

        except Exception as exc:
            failures += 1
            print(f"  [FAIL] {filename} — {exc}")
            traceback.print_exc()
            result_rows.append({
                "image_id": row.get("image_id", ""),
                "filename": filename,
                "status": "error",
                "predicted_craft": "",
                "predicted_material": "",
                "predicted_product_type": "",
                "confidence": "",
                "craft_match": "",
                "material_match": "",
                "product_type_match": "",
            })

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    avg_confidence = confidence_total / successes if successes else 0.0
    craft_accuracy = craft_correct / successes if successes else None
    material_accuracy = material_correct / successes if successes else None
    product_type_accuracy = product_type_correct / successes if successes else None

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "HuggingFaceTB/SmolVLM-256M-Instruct",
        "total_images": total,
        "successful_analyses": successes,
        "failures": failures,
        "craft_accuracy": craft_accuracy,
        "material_accuracy": material_accuracy,
        "product_type_accuracy": product_type_accuracy,
        "average_confidence": avg_confidence,
        "note": (
            "Accuracy metrics are exact string matches (case-insensitive). "
            "Partial matches are not counted. "
            "Confidence is model-estimated, not calibrated."
        ),
    }

    # ------------------------------------------------------------------
    # Write outputs
    # ------------------------------------------------------------------
    results_csv = results_dir / "vision_results.csv"
    if result_rows:
        with results_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(result_rows[0].keys()))
            writer.writeheader()
            writer.writerows(result_rows)
        print(f"\n[SAVED] {results_csv}")

    summary_json = results_dir / "vision_summary.json"
    with summary_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[SAVED] {summary_json}")

    # ------------------------------------------------------------------
    # Print summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"  Total images        : {total}")
    print(f"  Successful analyses : {successes}")
    print(f"  Failures            : {failures}")
    if craft_accuracy is not None:
        print(f"  Craft accuracy      : {craft_accuracy:.1%}")
        print(f"  Material accuracy   : {material_accuracy:.1%}")
        print(f"  Product type acc.   : {product_type_accuracy:.1%}")
        print(f"  Avg confidence      : {avg_confidence:.3f}")
    print("=" * 50 + "\n")


def _write_empty_summary(results_dir: Path) -> None:
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "HuggingFaceTB/SmolVLM-256M-Instruct",
        "total_images": 0,
        "successful_analyses": 0,
        "failures": 0,
        "craft_accuracy": None,
        "material_accuracy": None,
        "product_type_accuracy": None,
        "average_confidence": None,
        "note": (
            "No evaluation images supplied. "
            "Add images to evaluation/images/ and labels to evaluation/metadata.csv "
            "then re-run this script."
        ),
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / "vision_summary.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[SAVED] {out}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate KalaConnect Vision AI")
    p.add_argument(
        "--images-dir",
        type=Path,
        default=DEFAULT_IMAGES_DIR,
        help="Directory containing craft images (default: evaluation/images/)",
    )
    p.add_argument(
        "--metadata",
        type=Path,
        default=DEFAULT_METADATA,
        help="CSV file with expected labels (default: evaluation/metadata.csv)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory for result files (default: evaluation/results/)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    evaluate(
        images_dir=args.images_dir,
        metadata_path=args.metadata,
        results_dir=args.output_dir,
    )
