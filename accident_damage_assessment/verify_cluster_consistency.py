from pathlib import Path
import csv
from collections import Counter

ROOT = Path(__file__).resolve().parent

combined = (
    ROOT / "outputs" / "combined_features_10000"
    / "combined_features_10000.csv"
)

clusters = (
    ROOT / "outputs" / "classification_10000"
    / "exploratory_clusters_10000.csv"
)

profiles = (
    ROOT / "outputs" / "classification_10000"
    / "cluster_profiles.csv"
)

def count_rows(path):
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1

combined_count = count_rows(combined)
cluster_count = count_rows(clusters)

cluster_ids = Counter()

with clusters.open("r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        cluster_ids[row["cluster"]] += 1

print()
print("=" * 70)
print("CLUSTER DATA CONSISTENCY CHECK")
print("=" * 70)
print(f"Combined feature rows : {combined_count}")
print(f"Cluster assignment rows: {cluster_count}")
print()

total_clusters = sum(cluster_ids.values())

for cluster, count in sorted(cluster_ids.items()):
    print(f"Cluster {cluster}          : {count}")

print("-" * 70)
print(f"Total clustered       : {total_clusters}")
print(f"Missing from clusters : {combined_count - total_clusters}")
print("=" * 70)

if combined_count == cluster_count:
    print("STATUS: ALL FEATURE ROWS HAVE CLUSTER ASSIGNMENTS")
else:
    print("STATUS: MISMATCH FOUND — DO NOT PROCEED")
