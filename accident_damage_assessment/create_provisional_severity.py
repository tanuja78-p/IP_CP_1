import pandas as pd
from pathlib import Path

base = Path("outputs/classification_10000")
src = base / "features_with_clusters.csv"
out = base / "provisional_severity_indicators.csv"

df = pd.read_csv(src)

required = [
    "area",
    "width",
    "height",
    "aspect_ratio",
    "solidity",
    "circularity",
    "glcm_contrast",
    "glcm_homogeneity",
    "lbp_std",
    "cluster"
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing required features: {missing}")

indicators = pd.DataFrame(index=df.index)

indicators["damage_area_score"] = df["area"].rank(pct=True)
indicators["texture_contrast_score"] = df["glcm_contrast"].rank(pct=True)
indicators["texture_variation_score"] = df["lbp_std"].rank(pct=True)

indicators["shape_irregularity_score"] = (
    1.0 - df["solidity"].rank(pct=True)
)

indicators["shape_circularity_score"] = (
    1.0 - df["circularity"].rank(pct=True)
)

score_columns = list(indicators.columns)

indicators["provisional_damage_indicator"] = (
    indicators[score_columns].mean(axis=1)
)

result = pd.concat(
    [
        df[["index", "image", "region_id", "cluster"]].reset_index(drop=True),
        indicators.reset_index(drop=True)
    ],
    axis=1
)

result.to_csv(out, index=False)

print("=" * 70)
print("P4 - PROVISIONAL DAMAGE INDICATORS COMPLETE")
print("=" * 70)
print(f"Rows analysed : {len(result)}")
print(f"Clusters      : {result['cluster'].nunique()}")
print(f"Output        : {out.resolve()}")
print()
print("NOTE:")
print("These indicators are feature-based and provisional.")
print("They are NOT validated minor/moderate/severe labels.")
print("=" * 70)
