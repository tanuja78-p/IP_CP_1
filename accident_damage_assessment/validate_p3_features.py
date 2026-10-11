from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "outputs" / "p3_geometric_10000" / "geometric_features_10000.csv"

rows = list(csv.DictReader(CSV_PATH.open("r", encoding="utf-8")))

numeric_columns = [
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
    "centroid_y"
]

invalid = 0
negative = 0
zero_area = 0

for row in rows:
    try:
        values = {
            col: float(row[col])
            for col in numeric_columns
        }

        if any(not math.isfinite(v) for v in values.values()):
            invalid += 1
            continue

        if any(v < 0 for v in values.values()):
            negative += 1

        if values["area"] <= 0:
            zero_area += 1

    except Exception:
        invalid += 1

print()
print("=" * 70)
print("P3 — GEOMETRIC FEATURE VALIDATION COMPLETE")
print("=" * 70)
print(f"Feature rows      : {len(rows)}")
print(f"Invalid rows      : {invalid}")
print(f"Negative values   : {negative}")
print(f"Zero-area regions : {zero_area}")
print("=" * 70)

if invalid == 0 and negative == 0 and zero_area == 0:
    print("STATUS: P3 GEOMETRIC FEATURES VALID")
else:
    print("STATUS: CHECK REQUIRED")
