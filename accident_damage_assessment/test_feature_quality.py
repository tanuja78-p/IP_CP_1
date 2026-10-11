from pathlib import Path
import pandas as pd
import numpy as np

path = Path("outputs/combined_features_10000/combined_features_10000.csv")

df = pd.read_csv(path)

print("=" * 70)
print("AIM002 MODULE 8 — FEATURE QUALITY VALIDATION")
print("=" * 70)

print(f"\nTotal feature rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

features = [
    "area",
    "perimeter",
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
    "lbp_std",
]

print("\n" + "-" * 70)
print("MISSING / INVALID VALUES")
print("-" * 70)

total_bad = 0

for col in features:
    values = pd.to_numeric(df[col], errors="coerce")

    missing = int(values.isna().sum())
    infinite = int(np.isinf(values.fillna(0)).sum())

    bad = missing + infinite
    total_bad += bad

    print(
        f"{col:20s} "
        f"missing={missing:5d} "
        f"infinite={infinite:5d}"
    )

print("\nTotal invalid values:", total_bad)

if total_bad == 0:
    print("STATUS: ALL NUMERIC FEATURES ARE VALID")
else:
    print("STATUS: INVALID VALUES REQUIRE REVIEW")


print("\n" + "-" * 70)
print("RANGE VALIDATION")
print("-" * 70)

range_checks = {
    "area": (0, None),
    "perimeter": (0, None),
    "width": (1, None),
    "height": (1, None),
    "aspect_ratio": (0, None),
    "solidity": (0, 1),
    "circularity": (0, 1),
    "glcm_contrast": (0, None),
    "glcm_correlation": (-1, 1),
    "glcm_energy": (0, 1),
    "glcm_homogeneity": (0, 1),
    "lbp_mean": (0, None),
    "lbp_std": (0, None),
}

range_failures = 0

for col, (minimum, maximum) in range_checks.items():
    values = pd.to_numeric(df[col], errors="coerce").dropna()

    low = int((values < minimum).sum()) if minimum is not None else 0
    high = int((values > maximum).sum()) if maximum is not None else 0

    status = "PASS" if low == 0 and high == 0 else "REVIEW"

    print(
        f"{col:20s} "
        f"min={values.min():10.4f} "
        f"max={values.max():10.4f} "
        f"below={low:5d} "
        f"above={high:5d} "
        f"{status}"
    )

    range_failures += low + high

print("\nTotal range violations:", range_failures)

if range_failures == 0:
    print("STATUS: ALL FEATURE RANGES ARE VALID")
else:
    print("STATUS: RANGE VIOLATIONS FOUND")


print("\n" + "-" * 70)
print("FEATURE SUMMARY")
print("-" * 70)

summary = df[features].describe().T[
    ["min", "mean", "max"]
]

print(summary.to_string())

print("\n" + "=" * 70)
print("FEATURE QUALITY TEST COMPLETE")
print("=" * 70)
