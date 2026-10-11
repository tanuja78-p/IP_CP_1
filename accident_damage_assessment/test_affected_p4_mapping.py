import csv
from pathlib import Path

import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


ROOT = Path(".")
GEO = ROOT / "outputs" / "p4_texture_10000_fixed" / "affected_geometric_rows.csv"
P1_ROOT = ROOT / "outputs" / "p1_dataset"

OUT = ROOT / "outputs" / "p4_texture_10000_fixed"
OUT.mkdir(parents=True, exist_ok=True)

TEXTURE_OUT = OUT / "affected_texture_features.csv"
FAIL_OUT = OUT / "affected_texture_failures.csv"


# ---------------------------------------------------------
# Build filename -> physical-file lookup
# ---------------------------------------------------------
lookup = {}

for path in sorted(P1_ROOT.rglob("*")):
    if path.is_file():
        lookup.setdefault(path.name, []).append(path)


def bbox_fits(image, x, y, w, h):
    height, width = image.shape[:2]

    return (
        x >= 0 and
        y >= 0 and
        w > 0 and
        h > 0 and
        x + w <= width and
        y + h <= height
    )


def extract_texture(region):

    if region is None or region.size == 0:
        raise ValueError("Empty region")

    region = cv2.resize(
        region,
        (64, 64),
        interpolation=cv2.INTER_AREA
    )

    region = cv2.normalize(
        region,
        None,
        0,
        63,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    glcm = graycomatrix(
        region,
        distances=[1],
        angles=[0],
        levels=64,
        symmetric=True,
        normed=True
    )

    lbp = local_binary_pattern(
        region,
        P=8,
        R=1,
        method="uniform"
    )

    return (
        float(graycoprops(glcm, "contrast")[0, 0]),
        float(graycoprops(glcm, "correlation")[0, 0]),
        float(graycoprops(glcm, "energy")[0, 0]),
        float(graycoprops(glcm, "homogeneity")[0, 0]),
        float(np.mean(lbp)),
        float(np.std(lbp))
    )


rows = list(
    csv.DictReader(
        GEO.open("r", encoding="utf-8")
    )
)


passed = 0
failed = 0
ambiguous = 0
missing = 0


with TEXTURE_OUT.open("w", newline="", encoding="utf-8") as tf, \
     FAIL_OUT.open("w", newline="", encoding="utf-8") as ff:

    writer = csv.writer(tf)
    fail_writer = csv.writer(ff)

    writer.writerow([
        "index",
        "image",
        "region_id",
        "glcm_contrast",
        "glcm_correlation",
        "glcm_energy",
        "glcm_homogeneity",
        "lbp_mean",
        "lbp_std"
    ])

    fail_writer.writerow([
        "index",
        "image",
        "region_id",
        "reason"
    ])

    for number, row in enumerate(rows, 1):

        try:

            image_name = row["image"]

            matches = lookup.get(image_name, [])

            if not matches:
                missing += 1
                raise FileNotFoundError(
                    "No physical P1 image found"
                )

            x = int(row["x"])
            y = int(row["y"])
            w = int(row["width"])
            h = int(row["height"])

            valid_matches = []

            for path in matches:

                image = cv2.imread(
                    str(path),
                    cv2.IMREAD_GRAYSCALE
                )

                if image is not None and bbox_fits(
                    image,
                    x,
                    y,
                    w,
                    h
                ):
                    valid_matches.append(
                        (path, image)
                    )

            if len(valid_matches) == 0:
                missing += 1
                raise ValueError(
                    "No matching physical image contains the recorded bounding box"
                )

            if len(valid_matches) > 1:
                ambiguous += 1
                raise ValueError(
                    f"Ambiguous mapping: {len(valid_matches)} physical images contain bbox"
                )

            image_path, image = valid_matches[0]

            crop = image[
                y:y+h,
                x:x+w
            ]

            features = extract_texture(crop)

            writer.writerow([
                row["index"],
                row["image"],
                row["region_id"],
                f"{features[0]:.8f}",
                f"{features[1]:.8f}",
                f"{features[2]:.8f}",
                f"{features[3]:.8f}",
                f"{features[4]:.8f}",
                f"{features[5]:.8f}"
            ])

            passed += 1

        except Exception as exc:

            fail_writer.writerow([
                row["index"],
                row["image"],
                row["region_id"],
                str(exc)
            ])

            failed += 1

        if number % 1000 == 0 or number == len(rows):
            print(
                f"[{number:5d}/{len(rows):5d}] "
                f"PASS={passed:,} "
                f"FAIL={failed:,} "
                f"AMBIGUOUS={ambiguous:,}"
            )


print()
print("=" * 75)
print("AIM002 — AFFECTED P4 REGION VALIDATION")
print("=" * 75)
print(f"Input regions       : {len(rows):,}")
print(f"Texture PASS        : {passed:,}")
print(f"Failures            : {failed:,}")
print(f"Missing mappings    : {missing:,}")
print(f"Ambiguous mappings  : {ambiguous:,}")
print(f"Texture CSV         : {TEXTURE_OUT}")
print(f"Failure CSV         : {FAIL_OUT}")
print("=" * 75)
