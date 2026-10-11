from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

OUTPUT_ROOT = ROOT / "outputs" / "classification_10000"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_ROOT / "classification_ready_10000.csv"

FEATURES = [
    "area",
    "perimeter",
    "x",
    "y",
    "width",
    "height",
    "aspect_ratio",
    "solidity",
    "circularity",
    "centroid_x",
    "centroid_y",
    "glcm_contrast",
    "glcm_correlation",
    "glcm_energy",
    "glcm_homogeneity",
    "lbp_mean",
    "lbp_std"
]

with INPUT.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

valid = 0
invalid = 0

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "index",
            "image",
            "region_id"
        ] + FEATURES
    )

    writer.writeheader()

    for row in rows:

        try:
            values = []

            for feature in FEATURES:
                value = float(row[feature])

                if not math.isfinite(value):
                    raise ValueError()

                values.append(value)

            output_row = {
                "index": row["index"],
                "image": row["image"],
                "region_id": row["region_id"]
            }

            for feature, value in zip(FEATURES, values):
                output_row[feature] = f"{value:.8f}"

            writer.writerow(output_row)
            valid += 1

        except Exception:
            invalid += 1

print()
print("=" * 70)
print("CLASSIFICATION DATA PREPARATION COMPLETE")
print("=" * 70)
print(f"Input rows        : {len(rows)}")
print(f"Valid rows        : {valid}")
print(f"Invalid rows      : {invalid}")
print(f"Features           : {len(FEATURES)}")
print(f"Output CSV         : {OUTPUT}")
print("=" * 70)
