from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

OUTPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "feature_statistics.csv"
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

data = {
    feature: []
    for feature in features
}

with INPUT.open("r", encoding="utf-8") as f:

    for row in csv.DictReader(f):

        for feature in features:
            data[feature].append(
                float(row[feature])
            )

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "feature",
        "minimum",
        "maximum",
        "mean",
        "std"
    ])

    for feature in features:

        values = data[feature]

        writer.writerow([
            feature,
            f"{min(values):.8f}",
            f"{max(values):.8f}",
            f"{statistics.mean(values):.8f}",
            f"{statistics.pstdev(values):.8f}"
        ])

print()
print("=" * 70)
print("FEATURE STATISTICS COMPLETE")
print("=" * 70)

for feature in features:

    values = data[feature]

    print(
        f"{feature:22s} "
        f"min={min(values):.4f} "
        f"max={max(values):.4f} "
        f"mean={statistics.mean(values):.4f}"
    )

print("=" * 70)
print(f"CSV: {OUTPUT}")
