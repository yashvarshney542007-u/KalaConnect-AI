# Vision Evaluation

This directory contains the evaluation framework for the KalaConnect Vision AI.

## Overview

The evaluation system measures the accuracy of the Vision AI
(`HuggingFaceTB/SmolVLM-256M-Instruct`) against a curated dataset of
authentic Indian artisan/craft images.

## Directory Structure

```
evaluation/
├── images/          ← Place authentic craft images here (NOT committed to Git)
├── results/         ← Auto-generated result files (NOT committed to Git)
├── metadata.csv     ← Ground-truth labels for each evaluation image
├── evaluate_vision.py ← Evaluation script
└── README.md        ← This file
```

## metadata.csv Format

| Field                 | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| `image_id`            | Unique identifier (e.g. `001`)                                           |
| `filename`            | Filename of the image in `evaluation/images/` (e.g. `pottery_01.jpg`)   |
| `expected_craft`      | Expected craft category (see list below)                                 |
| `expected_material`   | Expected material (e.g. `terracotta clay`, `silk`, `brass`)              |
| `expected_product_type` | Expected product type (e.g. `vase`, `saree`, `sculpture`)              |
| `source`              | Image source / license (e.g. `own photo`, `CC0`, `CC-BY`)               |
| `notes`               | Any additional notes                                                     |

### Supported craft categories

- pottery
- textile
- embroidery
- wood craft
- metal craft
- basketry
- jewellery
- painting
- leather craft
- stone craft
- unknown

## How to add evaluation images

1. **Source legitimate images only.**
   Use images that your team owns, has photographed, or that are available
   under a Creative Commons license (CC0, CC-BY, CC-BY-SA). Do NOT use
   copyrighted stock photos.

2. **Place images in `evaluation/images/`.**
   Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

3. **Fill in `evaluation/metadata.csv`** with the corresponding ground-truth
   labels for each image.

4. **Do NOT commit images to Git.** They are excluded by `.gitignore`.

## Running the evaluation

```bash
# From the repository root with the virtual environment active:
python evaluation/evaluate_vision.py
```

With custom paths:

```bash
python evaluation/evaluate_vision.py \
    --images-dir evaluation/images \
    --metadata   evaluation/metadata.csv \
    --output-dir evaluation/results
```

## Output files

- `evaluation/results/vision_results.csv` — Per-image predictions and match results
- `evaluation/results/vision_summary.json` — Aggregated metrics

## Notes

- Accuracy metrics use **exact string matching** (case-insensitive).
- The model's `confidence` field is **self-reported** by the model — it is not
  calibrated scientific accuracy.
- Do NOT fabricate or pre-fill metrics without running real images through the model.
- The evaluation script exits gracefully if no images are available.
