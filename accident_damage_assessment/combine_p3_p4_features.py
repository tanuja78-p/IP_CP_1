from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent

GEOMETRIC = (
    ROOT / "outputs" / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

TEXTURE = (
    ROOT / "outputs" / "p4_texture_10000"
    / "texture_features_10000.csv"
)

OUTPUT_ROOT = ROOT / "outputs" / "combined_features_10000"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

OUTPUT = OUTPUT_ROOT / "combined_features_10000.csv"

with GEOMETRIC.open("r", encoding="utf-8") as f:
    geometric = list(csv.DictReader(f))

with TEXTURE.open("r", encoding="utf-8") as f:
    texture = list(csv.DictReader(f))

texture_map = {
    (
        row["index"],
        row["image"],
        row["region_id"]
    ): row
    for row in texture
}

geometric_features = [
    "area",
    "perimeter",
    "x",
    "y",
    "width",
    "height",
    "aspect_ratio",
    "solidity",
    "circularity",
    "centroid_x",
    "centroid_y"
]

texture_features = [
    "glcm_contrast",
    "glcm_correlation",
    "glcm_energy",
    "glcm_homogeneity",
    "lbp_mean",
    "lbp_std"
]

fields = [
    "index",
    "image",
    "region_id"
] + geometric_features + texture_features

matched = 0
missing = 0

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()

    for row in geometric:

        key = (
            row["index"],
            row["image"],
            row["region_id"]
        )

        texture_row = texture_map.get(key)

        if texture_row is None:
            missing += 1
            continue

        combined = {
            "index": row["index"],
            "image": row["image"],
            "region_id": row["region_id"]
        }

        for feature in geometric_features:
            combined[feature] = row[feature]

        for feature in texture_features:
            combined[feature] = texture_row[feature]

        writer.writerow(combined)
        matched += 1

print()
print("=" * 70)
print("P3 + P4 — FEATURE FUSION COMPLETE")
print("=" * 70)
print(f"Geometric rows    : {len(geometric)}")
print(f"Texture rows      : {len(texture)}")
print(f"Matched rows      : {matched}")
print(f"Missing matches   : {missing}")
print(f"Total features    : {len(geometric_features) + len(texture_features)}")
print(f"CSV               : {OUTPUT}")
print("=" * 70)
