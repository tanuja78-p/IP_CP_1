from pathlib import Path
import csv
import cv2
import numpy as np

from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

ROOT = Path(__file__).resolve().parent

GEOMETRIC_CSV = (
    ROOT
    / "outputs"
    / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

P1_ROOT = ROOT / "outputs" / "p1_dataset"

OUTPUT_ROOT = ROOT / "outputs" / "p4_texture_10000"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_ROOT / "texture_features_10000.csv"

rows = list(
    csv.DictReader(
        GEOMETRIC_CSV.open(
            "r",
            encoding="utf-8"
        )
    )
)

image_cache = {}


def load_image(image_name):

    if image_name in image_cache:
        return image_cache[image_name]

    matches = list(P1_ROOT.rglob(image_name))

    if not matches:
        raise FileNotFoundError(
            f"P1 image not found: {image_name}"
        )

    image = cv2.imread(
        str(matches[0]),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {matches[0]}"
        )

    image_cache[image_name] = image

    return image


def extract_texture(region):

    if region is None or region.size == 0:
        raise ValueError("Empty region.")

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

    contrast = float(
        graycoprops(
            glcm,
            "contrast"
        )[0, 0]
    )

    correlation = float(
        graycoprops(
            glcm,
            "correlation"
        )[0, 0]
    )

    energy = float(
        graycoprops(
            glcm,
            "energy"
        )[0, 0]
    )

    homogeneity = float(
        graycoprops(
            glcm,
            "homogeneity"
        )[0, 0]
    )

    lbp = local_binary_pattern(
        region,
        P=8,
        R=1,
        method="uniform"
    )

    lbp_mean = float(
        np.mean(lbp)
    )

    lbp_std = float(
        np.std(lbp)
    )

    return (
        contrast,
        correlation,
        energy,
        homogeneity,
        lbp_mean,
        lbp_std
    )


passed = 0
failed = 0

with OUTPUT_CSV.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

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

    for number, row in enumerate(rows, 1):

        try:

            image = load_image(
                row["image"]
            )

            x = int(row["x"])
            y = int(row["y"])
            width = int(row["width"])
            height = int(row["height"])

            crop = image[
                y:y + height,
                x:x + width
            ]

            features = extract_texture(
                crop
            )

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

        except Exception:

            failed += 1

        if number % 5000 == 0 or number == len(rows):

            print(
                f"[{number:6d}/{len(rows):6d}] "
                f"PASS={passed} "
                f"FAIL={failed}"
            )

print()
print("=" * 70)
print("P4 — TEXTURE FEATURE EXTRACTION COMPLETE")
print("=" * 70)
print(f"Feature regions    : {len(rows)}")
print(f"Passed             : {passed}")
print(f"Failed             : {failed}")
print(f"CSV                : {OUTPUT_CSV}")
print("=" * 70)
