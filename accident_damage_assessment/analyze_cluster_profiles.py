import pandas as pd
from pathlib import Path

base = Path("outputs/classification_10000")
src = base / "features_with_clusters.csv"
out = base / "cluster_feature_profiles.csv"

df = pd.read_csv(src)

features = [
    c for c in df.columns
    if c not in {
        "index",
        "image",
        "region_id",
        "cluster"
    }
    and pd.api.types.is_numeric_dtype(df[c])
]

profile = df.groupby("cluster")[features].agg(
    ["count", "mean", "median"]
)

profile.to_csv(out)

print("=" * 70)
print("P4 - CLUSTER FEATURE PROFILE ANALYSIS COMPLETE")
print("=" * 70)
print(f"Rows analysed : {len(df)}")
print(f"Features      : {len(features)}")
print()

counts = df["cluster"].value_counts().sort_index()

for cluster, count in counts.items():
    print(f"Cluster {cluster} : {count}")

print()
print(f"CSV           : {out.resolve()}")
print("=" * 70)
