from pathlib import Path
import csv
import statistics

ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

CLUSTER_FILE = (
    ROOT / "outputs" / "classification_10000"
    / "exploratory_clusters_10000.csv"
)

OUTPUT = (
    ROOT / "outputs" / "classification_10000"
    / "cluster_profiles.csv"
)

FEATURES = [
    "area",
    "perimeter",
    "width",
    "height",
    "aspect_ratio",
    "solidity",
    "circularity",
    "glcm_contrast",
    "glcm_correlation",
    "glcm_energy",
    "glcm_homogeneity",
    "lbp_mean",
    "lbp_std"
]

with INPUT.open("r", encoding="utf-8") as f:
    feature_rows = list(csv.DictReader(f))

with CLUSTER_FILE.open("r", encoding="utf-8") as f:
    cluster_rows = list(csv.DictReader(f))

clusters = {}

for feature_row, cluster_row in zip(
    feature_rows,
    cluster_rows
):

    cluster = int(cluster_row["cluster"])

    if cluster not in clusters:
        clusters[cluster] = {
            feature: []
            for feature in FEATURES
        }

    for feature in FEATURES:
        clusters[cluster][feature].append(
            float(feature_row[feature])
        )

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "cluster",
        "count",
        "feature",
        "mean",
        "std",
        "minimum",
        "maximum"
    ])

    for cluster in sorted(clusters):

        count = len(
            clusters[cluster][FEATURES[0]]
        )

        for feature in FEATURES:

            values = clusters[cluster][feature]

            writer.writerow([
                cluster,
                count,
                feature,
                f"{statistics.mean(values):.6f}",
                f"{statistics.pstdev(values):.6f}",
                f"{min(values):.6f}",
                f"{max(values):.6f}"
            ])

print()
print("=" * 70)
print("CLUSTER PROFILE ANALYSIS COMPLETE")
print("=" * 70)

for cluster in sorted(clusters):

    print(
        f"Cluster {cluster}: "
        f"{len(clusters[cluster][FEATURES[0]])} regions"
    )

print(f"CSV: {OUTPUT}")
print("=" * 70)
