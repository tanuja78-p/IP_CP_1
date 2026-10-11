from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parent

CSV_PATH = (
    ROOT
    / "outputs"
    / "p4_texture_10000"
    / "texture_features_10000.csv"
)

rows = list(
    csv.DictReader(
        CSV_PATH.open(
            "r",
            encoding="utf-8"
        )
    )
)

features = [
    "glcm_contrast",
    "glcm_correlation",
    "glcm_energy",
    "glcm_homogeneity",
    "lbp_mean",
    "lbp_std"
]

invalid = 0
missing = 0

for row in rows:

    bad = False

    for feature in features:

        value = row.get(feature, "")

        if value == "":
            missing += 1
            bad = True
            break

        try:
            number = float(value)

            if not math.isfinite(number):
                invalid += 1
                bad = True
                break

        except Exception:
            invalid += 1
            bad = True
            break

print()
print("=" * 70)
print("P4 — TEXTURE FEATURE VALIDATION COMPLETE")
print("=" * 70)
print(f"Feature rows       : {len(rows)}")
print(f"Missing rows       : {missing}")
print(f"Invalid rows       : {invalid}")
print("=" * 70)

if missing == 0 and invalid == 0:
    print("STATUS: P4 TEXTURE FEATURES VALID")
else:
    print("STATUS: CHECK REQUIRED")
