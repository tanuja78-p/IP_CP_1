import pandas as pd
from pathlib import Path

base = Path("outputs")

combined = base / "combined_features_10000" / "combined_features_10000.csv"
clusters = base / "classification_10000" / "exploratory_clusters_10000.csv"

df_features = pd.read_csv(combined, nrows=5)
df_clusters = pd.read_csv(clusters, nrows=5)

print("=" * 70)
print("P4 DATA STRUCTURE CHECK")
print("=" * 70)

print("\nCOMBINED FEATURES")
print("Columns:", len(df_features.columns))
print(df_features.columns.tolist())

print("\nCLUSTER FILE")
print("Columns:", len(df_clusters.columns))
print(df_clusters.columns.tolist())

print("\nCombined sample:")
print(df_features.head(2).to_string(index=False))

print("\nCluster sample:")
print(df_clusters.head(2).to_string(index=False))

print("=" * 70)
