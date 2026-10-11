from pathlib import Path
import csv
import numpy as np

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

OUTPUT_ROOT = ROOT / "outputs" / "classification_10000"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_ROOT / "exploratory_clusters_10000.csv"

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

model = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

clusters = model.fit_predict(X_scaled)

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "index",
        "image",
        "region_id",
        "cluster"
    ])

    for row, cluster in zip(rows, clusters):

        writer.writerow([
            row["index"],
            row["image"],
            row["region_id"],
            int(cluster)
        ])

counts = np.bincount(clusters)

print()
print("=" * 70)
print("EXPLORATORY DAMAGE CANDIDATE CLUSTERING COMPLETE")
print("=" * 70)

for cluster_id, count in enumerate(counts):
    print(
        f"Cluster {cluster_id} : {count}"
    )

print(f"Total regions       : {len(rows)}")
print(f"CSV                 : {OUTPUT}")
print("=" * 70)
print("STATUS: EXPLORATORY ONLY — NO SEVERITY LABELS ASSIGNED")
