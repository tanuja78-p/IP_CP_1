import pandas as pd
from pathlib import Path

base = Path("outputs")

features_file = base / "combined_features_10000" / "combined_features_10000.csv"
clusters_file = base / "classification_10000" / "exploratory_clusters_10000.csv"
output_file = base / "classification_10000" / "features_with_clusters.csv"

features = pd.read_csv(features_file)
clusters = pd.read_csv(clusters_file)

keys = ["index", "image", "region_id"]

for key in keys:
    if key not in features.columns:
        raise ValueError(f"Missing key in feature file: {key}")
    if key not in clusters.columns:
        raise ValueError(f"Missing key in cluster file: {key}")

merged = features.merge(
    clusters[keys + ["cluster"]],
    on=keys,
    how="left",
    validate="one_to_one"
)

missing_clusters = int(merged["cluster"].isna().sum())

if missing_clusters != 0:
    raise ValueError(
        f"{missing_clusters} feature rows do not have cluster assignments."
    )

merged.to_csv(output_file, index=False)

print("=" * 70)
print("P4 - FEATURE AND CLUSTER DATASET CREATED")
print("=" * 70)
print(f"Feature rows       : {len(features)}")
print(f"Cluster rows       : {len(clusters)}")
print(f"Merged rows        : {len(merged)}")
print(f"Missing clusters   : {missing_clusters}")
print(f"Columns            : {len(merged.columns)}")
print(f"Output             : {output_file.resolve()}")
print("=" * 70)
