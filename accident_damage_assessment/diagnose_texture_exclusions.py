from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path("outputs")

geo_path = ROOT / "p3_geometric_10000" / "geometric_features_10000.csv"
tex_path = ROOT / "p4_texture_10000" / "texture_features_10000.csv"

geo = pd.read_csv(geo_path)
tex = pd.read_csv(tex_path)

# Images that have geometric regions but no texture regions
geo_keys = geo[["index", "image"]].drop_duplicates()
tex_keys = tex[["index", "image"]].drop_duplicates()

missing = geo_keys.merge(
    tex_keys,
    on=["index", "image"],
    how="left",
    indicator=True
)

missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")

# Attach geometric statistics
stats = (
    geo.groupby(["index", "image"])
    .agg(
        region_count=("region_id", "count"),
        min_area=("area", "min"),
        max_area=("area", "max"),
        mean_area=("area", "mean"),
        min_width=("width", "min"),
        min_height=("height", "min"),
        max_width=("width", "max"),
        max_height=("height", "max"),
    )
    .reset_index()
)

missing = missing.merge(
    stats,
    on=["index", "image"],
    how="left"
)

print("=" * 75)
print("AIM002 — TEXTURE EXCLUSION ROOT-CAUSE DIAGNOSTIC")
print("=" * 75)

print(f"\nExcluded images: {len(missing)}")
print(f"Excluded geometric regions: {missing['region_count'].sum():,}")

print("\n--- REGION AREA ---")
print(
    missing[
        ["min_area", "mean_area", "max_area"]
    ].describe().to_string()
)

print("\n--- REGION WIDTH ---")
print(
    missing[
        ["min_width", "max_width"]
    ].describe().to_string()
)

print("\n--- REGION HEIGHT ---")
print(
    missing[
        ["min_height", "max_height"]
    ].describe().to_string()
)

print("\n--- POTENTIALLY SMALL REGIONS ---")
print(
    "Images where minimum area < 16:",
    int((missing["min_area"] < 16).sum())
)

print(
    "Images where minimum width <= 2:",
    int((missing["min_width"] <= 2).sum())
)

print(
    "Images where minimum height <= 2:",
    int((missing["min_height"] <= 2).sum())
)

print("\n--- EXCLUDED IMAGE SAMPLE ---")
print(
    missing
    .sort_values(["index", "image"])
    .head(50)
    .to_string(index=False)
)

# Save diagnostic table
out = ROOT / "module8_texture_exclusion_diagnostic.csv"
missing.to_csv(out, index=False)

print("\nDiagnostic saved to:")
print(out)

print("\n" + "=" * 75)
print("DIAGNOSTIC COMPLETE")
print("=" * 75)
