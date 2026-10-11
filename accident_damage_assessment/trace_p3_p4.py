from pathlib import Path
import pandas as pd

ROOT = Path("outputs")

p3_path = ROOT / "p3_10000" / "p3_candidates_10000.csv"
geo_path = ROOT / "p3_geometric_10000" / "geometric_features_10000.csv"
tex_path = ROOT / "p4_texture_10000" / "texture_features_10000.csv"
comb_path = ROOT / "combined_features_10000" / "combined_features_10000.csv"

p3 = pd.read_csv(p3_path)
geo = pd.read_csv(geo_path)
tex = pd.read_csv(tex_path)
comb = pd.read_csv(comb_path)

print("=" * 75)
print("AIM002 — P3 → P4 RECORD TRACE")
print("=" * 75)

keys = ["index", "image"]

def unique_keys(df):
    return df[keys].drop_duplicates()

p3_keys = unique_keys(p3)
geo_keys = unique_keys(geo)
tex_keys = unique_keys(tex)
comb_keys = unique_keys(comb)

print("\nIMAGE-LEVEL COUNTS")
print("-" * 50)
print("P3       :", len(p3_keys))
print("Geometric:", len(geo_keys))
print("Texture  :", len(tex_keys))
print("Combined :", len(comb_keys))

# P3 -> geometric
p3_geo = p3_keys.merge(
    geo_keys,
    on=keys,
    how="left",
    indicator=True
)

p3_missing_geo = p3_geo[p3_geo["_merge"] == "left_only"]

print("\nP3 → GEOMETRIC")
print("-" * 50)
print("P3 images missing from geometric:",
      len(p3_missing_geo))

if len(p3_missing_geo):
    print("\nFirst missing P3 records:")
    print(
        p3_missing_geo[keys]
        .head(20)
        .to_string(index=False)
    )

# Geometric -> texture
geo_tex = geo_keys.merge(
    tex_keys,
    on=keys,
    how="left",
    indicator=True
)

geo_missing_tex = geo_tex[geo_tex["_merge"] == "left_only"]

print("\nGEOMETRIC → TEXTURE")
print("-" * 50)
print("Geometric images missing from texture:",
      len(geo_missing_tex))

if len(geo_missing_tex):
    print("\nFirst missing geometric records:")
    print(
        geo_missing_tex[keys]
        .head(20)
        .to_string(index=False)
    )

# Texture -> combined
tex_comb = tex_keys.merge(
    comb_keys,
    on=keys,
    how="left",
    indicator=True
)

tex_missing_comb = tex_comb[tex_comb["_merge"] == "left_only"]

print("\nTEXTURE → COMBINED")
print("-" * 50)
print("Texture images missing from combined:",
      len(tex_missing_comb))

# Region-level consistency
region_keys = ["index", "image", "region_id"]

geo_regions = geo[region_keys].drop_duplicates()
tex_regions = tex[region_keys].drop_duplicates()
comb_regions = comb[region_keys].drop_duplicates()

print("\n" + "=" * 75)
print("REGION-LEVEL COUNTS")
print("=" * 75)

print("Geometric regions:", f"{len(geo_regions):,}")
print("Texture regions  :", f"{len(tex_regions):,}")
print("Combined regions :", f"{len(comb_regions):,}")

geo_tex_regions = geo_regions.merge(
    tex_regions,
    on=region_keys,
    how="left",
    indicator=True
)

missing_regions = geo_tex_regions[
    geo_tex_regions["_merge"] == "left_only"
]

print("\nGeometric regions missing from texture:",
      f"{len(missing_regions):,}")

tex_comb_regions = tex_regions.merge(
    comb_regions,
    on=region_keys,
    how="left",
    indicator=True
)

missing_comb_regions = tex_comb_regions[
    tex_comb_regions["_merge"] == "left_only"
]

print(
    "Texture regions missing from combined:",
    f"{len(missing_comb_regions):,}"
)

print("\n" + "=" * 75)
print("TRACE COMPLETE")
print("=" * 75)
