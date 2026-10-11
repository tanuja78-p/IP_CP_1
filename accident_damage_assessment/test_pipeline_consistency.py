from pathlib import Path
import pandas as pd

ROOT = Path("outputs")

print("=" * 75)
print("AIM002 MODULE 8 — P1 → P4 OUTPUT CONSISTENCY")
print("=" * 75)

# ---------------------------------------------------------
# Locate available result files
# ---------------------------------------------------------
files = {
    "P1-P2": ROOT / "full_p1_p2" / "full_p1_p2_results.csv",
    "P3": ROOT / "p3_10000" / "p3_candidates_10000.csv",
    "Geometric": ROOT / "p3_geometric_10000" / "geometric_features_10000.csv",
    "Texture": ROOT / "p4_texture_10000" / "texture_features_10000.csv",
    "Combined": ROOT / "combined_features_10000" / "combined_features_10000.csv",
    "Clusters": ROOT / "classification_10000" / "exploratory_clusters_10000.csv",
}

data = {}

for stage, path in files.items():
    print(f"\n[{stage}]")
    print("-" * 50)

    if not path.exists():
        print("MISSING:", path)
        continue

    df = pd.read_csv(path)
    data[stage] = df

    print("Rows:", f"{len(df):,}")
    print("Columns:", len(df.columns))

    for col in ["index", "image", "region_id"]:
        if col in df.columns:
            print(f"Unique {col}:", df[col].nunique())


# ---------------------------------------------------------
# P1-P2 image-level verification
# ---------------------------------------------------------
print("\n" + "=" * 75)
print("IMAGE-LEVEL CONSISTENCY")
print("=" * 75)

if "P1-P2" in data:
    df = data["P1-P2"]

    image_col = "image" if "image" in df.columns else None

    if image_col:
        print(
            "P1-P2 unique images:",
            f"{df[image_col].nunique():,}"
        )

    # Look for explicit success/failure columns
    for col in df.columns:
        lower = str(col).lower()

        if any(x in lower for x in ["success", "status", "failed", "error"]):
            print(
                f"{col}:",
                df[col].value_counts(dropna=False).to_dict()
            )


# ---------------------------------------------------------
# P3 candidate statistics
# ---------------------------------------------------------
print("\n" + "=" * 75)
print("P3 CANDIDATE STATISTICS")
print("=" * 75)

if "P3" in data:
    df = data["P3"]

    if "image" in df.columns:
        print("Images represented:", f"{df['image'].nunique():,}")

    print("Candidate rows:", f"{len(df):,}")

    if "region_id" in df.columns:
        print("Unique candidate regions:", f"{df['region_id'].nunique():,}")


# ---------------------------------------------------------
# Geometric / texture / combined image counts
# ---------------------------------------------------------
for stage in ["Geometric", "Texture", "Combined", "Clusters"]:

    print("\n" + "-" * 75)
    print(stage.upper())

    if stage not in data:
        print("No data available.")
        continue

    df = data[stage]

    if "image" in df.columns:
        print(
            "Unique images:",
            f"{df['image'].nunique():,}"
        )

    if "region_id" in df.columns:
        print(
            "Unique region IDs:",
            f"{df['region_id'].nunique():,}"
        )

    print("Rows:", f"{len(df):,}")


# ---------------------------------------------------------
# Combined vs cluster consistency
# ---------------------------------------------------------
print("\n" + "=" * 75)
print("COMBINED FEATURES ↔ CLUSTERS")
print("=" * 75)

if "Combined" in data and "Clusters" in data:

    combined = data["Combined"]
    clusters = data["Clusters"]

    keys = ["index", "image", "region_id"]

    if all(k in combined.columns for k in keys) and \
       all(k in clusters.columns for k in keys):

        combined_keys = combined[keys].drop_duplicates()
        cluster_keys = clusters[keys].drop_duplicates()

        missing = combined_keys.merge(
            cluster_keys,
            on=keys,
            how="left",
            indicator=True
        )

        missing_count = int(
            (missing["_merge"] == "left_only").sum()
        )

        print(
            "Combined unique regions:",
            f"{len(combined_keys):,}"
        )

        print(
            "Cluster unique regions:",
            f"{len(cluster_keys):,}"
        )

        print(
            "Missing cluster assignments:",
            f"{missing_count:,}"
        )

        if missing_count == 0:
            print("STATUS: PASS")
        else:
            print("STATUS: REVIEW")


# ---------------------------------------------------------
# Final interpretation
# ---------------------------------------------------------
print("\n" + "=" * 75)
print("INTERPRETATION")
print("=" * 75)

print(
    "This test verifies internal consistency between stored "
    "pipeline outputs."
)

print(
    "It does NOT claim segmentation accuracy, damage-detection "
    "accuracy, or severity-classification accuracy."
)

print("=" * 75)
