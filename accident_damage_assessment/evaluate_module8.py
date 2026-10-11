from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(".")
OUTPUTS = ROOT / "outputs"

print("=" * 70)
print("AIM002 MODULE 8 — DATASET & PIPELINE EVALUATION")
print("=" * 70)

files = {
    "working_10000": OUTPUTS / "working_dataset_10000.csv",
    "p1_p2": OUTPUTS / "full_p1_p2" / "full_p1_p2_results.csv",
    "p3": OUTPUTS / "p3_10000" / "p3_candidates_10000.csv",
    "geometric": OUTPUTS / "p3_geometric_10000" / "geometric_features_10000.csv",
    "texture": OUTPUTS / "p4_texture_10000" / "texture_features_10000.csv",
    "combined": OUTPUTS / "combined_features_10000" / "combined_features_10000.csv",
    "clusters": OUTPUTS / "classification_10000" / "exploratory_clusters_10000.csv",
}

for name, path in files.items():
    print(f"\n{name.upper()}")
    print("-" * 50)

    if not path.exists():
        print("MISSING:", path)
        continue

    try:
        df = pd.read_csv(path)
        print("Rows :", len(df))
        print("Cols :", len(df.columns))
        print("Columns:", ", ".join(df.columns.astype(str).tolist()))
    except Exception as exc:
        print("ERROR:", exc)

print("\n" + "=" * 70)
print("BASIC INTEGRITY CHECKS")
print("=" * 70)

# ---------------------------------------------------------
# Working dataset
# ---------------------------------------------------------
working = None

if files["working_10000"].exists():
    working = pd.read_csv(files["working_10000"])

    print("\nWorking dataset:")
    print("Rows:", len(working))

    if len(working) == 10000:
        print("STATUS: EXACTLY 10,000 IMAGES")
    else:
        print("STATUS: WORKING SET IS NOT EXACTLY 10,000")

    possible_image_cols = [
        c for c in working.columns
        if str(c).lower() in {"image", "filename", "file", "path"}
    ]

    if possible_image_cols:
        col = possible_image_cols[0]
        print("Image column:", col)
        print("Unique images:", working[col].nunique())
    else:
        print("Image column could not be automatically identified.")


# ---------------------------------------------------------
# Combined feature dataset
# ---------------------------------------------------------
combined = None

if files["combined"].exists():
    combined = pd.read_csv(files["combined"])

    required = [
        "index",
        "image",
        "region_id",
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
        "lbp_std",
    ]

    missing = [c for c in required if c not in combined.columns]

    print("\nCombined feature validation:")
    print("Rows:", len(combined))

    if missing:
        print("Missing columns:", missing)
    else:
        print("All required feature columns present.")

    print("Duplicate rows:", combined.duplicated().sum())

    numeric = [c for c in required if c not in ["index", "image", "region_id"]]

    bad_values = {}
    for c in numeric:
        bad = int(
            (~np.isfinite(pd.to_numeric(combined[c], errors="coerce"))).sum()
        )
        if bad:
            bad_values[c] = bad

    if bad_values:
        print("Invalid numeric values:", bad_values)
    else:
        print("Numeric feature values: VALID")

    print(
        "Unique images:",
        combined["image"].nunique() if "image" in combined.columns else "N/A"
    )

    print(
        "Unique regions:",
        len(combined[["index", "image", "region_id"]].drop_duplicates())
        if all(c in combined.columns for c in ["index", "image", "region_id"])
        else "N/A"
    )


# ---------------------------------------------------------
# Cluster consistency
# ---------------------------------------------------------
clusters = None

if files["clusters"].exists() and combined is not None:
    clusters = pd.read_csv(files["clusters"])

    print("\nCluster consistency:")

    keys = ["index", "image", "region_id"]

    if all(c in combined.columns for c in keys) and all(c in clusters.columns for c in keys):
        feature_keys = combined[keys].drop_duplicates()
        cluster_keys = clusters[keys].drop_duplicates()

        merged = feature_keys.merge(
            cluster_keys,
            on=keys,
            how="left",
            indicator=True
        )

        missing_clusters = int((merged["_merge"] == "left_only").sum())

        print("Feature rows:", len(feature_keys))
        print("Cluster rows:", len(cluster_keys))
        print("Missing cluster assignments:", missing_clusters)

        if missing_clusters == 0 and len(feature_keys) == len(cluster_keys):
            print("STATUS: ALL FEATURE ROWS HAVE CLUSTER ASSIGNMENTS")
        else:
            print("STATUS: CLUSTER CONSISTENCY NEEDS REVIEW")

        if "cluster" in clusters.columns:
            print("\nCluster distribution:")
            print(clusters["cluster"].value_counts().sort_index().to_string())


print("\n" + "=" * 70)
print("IMPORTANT EVALUATION NOTE")
print("=" * 70)
print(
    "This evaluation checks dataset/output integrity and consistency."
)
print(
    "It does NOT calculate classification accuracy because verified "
    "ground-truth severity labels are not available."
)
print("=" * 70)
