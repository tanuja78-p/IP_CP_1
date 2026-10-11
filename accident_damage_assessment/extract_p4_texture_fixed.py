from pathlib import Path
import csv
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

ROOT = Path(__file__).resolve().parent

GEOMETRIC_CSV = (
    ROOT / "outputs" / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

MAPPING_CSV = (
    ROOT / "outputs" / "p4_texture_10000_fixed"
    / "index_source_mapping.csv"
)

OUTPUT_ROOT = ROOT / "outputs" / "p4_texture_10000_fixed"
OUTPUT_CSV = OUTPUT_ROOT / "texture_features_fixed.csv"
FAILURE_CSV = OUTPUT_ROOT / "texture_failures_fixed.csv"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(
    GEOMETRIC_CSV.open("r", encoding="utf-8")
))

mapping = {
    row["index"]: row["source_path"]
    for row in csv.DictReader(
        MAPPING_CSV.open("r", encoding="utf-8")
    )
}

image_cache = {}

def load_image(index):
    if index in image_cache:
        return image_cache[index]

    source = mapping.get(index)

    if source is None:
        raise FileNotFoundError(
            f"No source mapping for index {index}"
        )

    image = cv2.imread(
        source,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {source}"
        )

    image_cache[index] = image
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
        graycoprops(glcm, "contrast")[0, 0]
    )

    correlation = float(
        graycoprops(glcm, "correlation")[0, 0]
    )

    energy = float(
        graycoprops(glcm, "energy")[0, 0]
    )

    homogeneity = float(
        graycoprops(glcm, "homogeneity")[0, 0]
    )

    lbp = local_binary_pattern(
        region,
        P=8,
        R=1,
        method="uniform"
    )

    return (
        contrast,
        correlation,
        energy,
        homogeneity,
        float(np.mean(lbp)),
        float(np.std(lbp))
    )


passed = 0
failed = 0

with OUTPUT_CSV.open(
    "w",
    newline="",
    encoding="utf-8"
) as f_out, FAILURE_CSV.open(
    "w",
    newline="",
    encoding="utf-8"
) as f_fail:

    writer = csv.writer(f_out)
    fail_writer = csv.writer(f_fail)

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

    total = len(rows)

    for number, row in enumerate(rows, 1):

        try:
            index = row["index"]

            image = load_image(index)

            x = int(row["x"])
            y = int(row["y"])
            width = int(row["width"])
            height = int(row["height"])

            image_h, image_w = image.shape[:2]

            if (
                x < 0 or
                y < 0 or
                width <= 0 or
                height <= 0 or
                x + width > image_w or
                y + height > image_h
            ):
                raise ValueError(
                    f"bbox outside source image "
                    f"{image_w}x{image_h}"
                )

            crop = image[
                y:y + height,
                x:x + width
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

            failed += 1

            fail_writer.writerow([
                row.get("index", ""),
                row.get("image", ""),
                row.get("region_id", ""),
                str(exc)
            ])

        if number % 5000 == 0 or number == total:
            print(
                f"[{number:6d}/{total:6d}] "
                f"PASS={passed} "
                f"FAIL={failed}"
            )

print()
print("=" * 70)
print("AIM002 — CORRECTED P4 TEXTURE EXTRACTION")
print("=" * 70)
print(f"Input geometric rows : {len(rows)}")
print(f"Texture PASS         : {passed}")
print(f"Texture FAIL         : {failed}")
print(f"Output CSV           : {OUTPUT_CSV}")
print(f"Failure CSV          : {FAILURE_CSV}")
print("=" * 70)
