from pathlib import Path
import csv
import numpy as np
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

OUTPUT_ROOT = ROOT / "outputs" / "classification_10000"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_ROOT / "scaled_features_10000.csv"

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

X = np.array(
    [
        [float(row[f]) for f in FEATURES]
        for row in rows
    ],
    dtype=np.float64
)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow(
        ["index", "image", "region_id"] + FEATURES
    )

    for row, values in zip(rows, X_scaled):

        writer.writerow(
            [
                row["index"],
                row["image"],
                row["region_id"]
            ]
            +
            [f"{v:.8f}" for v in values]
        )

print()
print("=" * 70)
print("FEATURE SCALING COMPLETE")
print("=" * 70)
print(f"Input rows        : {len(rows)}")
print(f"Features           : {len(FEATURES)}")
print(f"Output rows        : {len(X_scaled)}")
print(f"Output CSV         : {OUTPUT}")
print("=" * 70)
print("STATUS: FEATURES STANDARDIZED")
