from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parent

CSV_PATH = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

features = [
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

rows = list(
    csv.DictReader(
        CSV_PATH.open(
            "r",
            encoding="utf-8"
        )
    )
)

invalid = 0
missing = 0

for row in rows:

    for feature in features:

        value = row.get(feature, "")

        if value == "":
            missing += 1
            break

        try:
            number = float(value)

            if not math.isfinite(number):
                invalid += 1
                break

        except Exception:
            invalid += 1
            break

print()
print("=" * 70)
print("COMBINED FEATURE DATASET VALIDATION COMPLETE")
print("=" * 70)
print(f"Rows              : {len(rows)}")
print(f"Features           : {len(features)}")
print(f"Missing rows       : {missing}")
print(f"Invalid rows       : {invalid}")
print("=" * 70)

if missing == 0 and invalid == 0:
    print("STATUS: COMBINED FEATURES VALID")
else:
    print("STATUS: CHECK REQUIRED")
