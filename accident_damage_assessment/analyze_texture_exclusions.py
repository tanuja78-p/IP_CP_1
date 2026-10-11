from pathlib import Path
import pandas as pd

ROOT = Path("outputs")

geo_path = ROOT / "p3_geometric_10000" / "geometric_features_10000.csv"
tex_path = ROOT / "p4_texture_10000" / "texture_features_10000.csv"

geo = pd.read_csv(geo_path)
tex = pd.read_csv(tex_path)

keys = ["index", "image"]

geo_counts = (
    geo.groupby(keys)
    .size()
    .reset_index(name="geometric_regions")
)

tex_counts = (
    tex.groupby(keys)
    .size()
    .reset_index(name="texture_regions")
)

comparison = geo_counts.merge(
    tex_counts,
    on=keys,
    how="left"
)

comparison["texture_regions"] = (
    comparison["texture_regions"]
    .fillna(0)
    .astype(int)
)

missing_texture = comparison[
    comparison["texture_regions"] == 0
].copy()

print("=" * 75)
print("AIM002 — GEOMETRIC → TEXTURE EXCLUSION ANALYSIS")
print("=" * 75)

print("\nImages with geometric regions but zero texture regions:")
print(f"Count: {len(missing_texture)}")

print("\nGeometric region count for excluded images:")
print(
    missing_texture["geometric_regions"]
    .describe()
    .to_string()
)

print("\nFirst 30 excluded images:")
print(
    missing_texture
    .sort_values(["index", "image"])
    .head(30)
    .to_string(index=False)
)

print("\n" + "-" * 75)
print("TOTAL GEOMETRIC REGIONS IN EXCLUDED IMAGES")
print("-" * 75)

print(
    "Regions:",
    f"{missing_texture['geometric_regions'].sum():,}"
)

print("\n" + "-" * 75)
print("TEXTURE DATASET COVERAGE")
print("-" * 75)

total_geo_images = len(geo_counts)
texture_images = len(tex_counts)
excluded_images = len(missing_texture)

print("Geometric images :", total_geo_images)
print("Texture images   :", texture_images)
print("Excluded images  :", excluded_images)

coverage = (
    texture_images / total_geo_images * 100
    if total_geo_images else 0
)

print(f"Texture image coverage: {coverage:.2f}%")

print("\n" + "=" * 75)
print("ANALYSIS COMPLETE")
print("=" * 75)
