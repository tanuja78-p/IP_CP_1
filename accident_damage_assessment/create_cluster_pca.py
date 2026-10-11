import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

base = Path("outputs/classification_10000")
src = base / "exploratory_clusters_10000.csv"
out = base / "cluster_pca.png"

df = pd.read_csv(src)

exclude = {"image_name", "source_path", "cluster", "label", "severity"}

features = [
    c for c in df.columns
    if c not in exclude and pd.api.types.is_numeric_dtype(df[c])
]

X = df[features].fillna(df[features].median())
X_scaled = StandardScaler().fit_transform(X)

pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))

for cluster in sorted(df["cluster"].unique()):
    mask = df["cluster"].to_numpy() == cluster

    plt.scatter(
        coords[mask, 0],
        coords[mask, 1],
        s=4,
        alpha=0.35,
        label=f"Cluster {cluster}"
    )

plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)")
plt.title("P4 Feature Space - KMeans Cluster Visualization")
plt.legend()
plt.tight_layout()
plt.savefig(out, dpi=200)
plt.close()

print("=" * 70)
print("P4 - PCA CLUSTER VISUALIZATION COMPLETE")
print("=" * 70)
print(f"Rows plotted : {len(df)}")
print(f"Features     : {len(features)}")
print(f"Output       : {out.resolve()}")
print("=" * 70)
