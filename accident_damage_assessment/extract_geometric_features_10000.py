from pathlib import Path
import csv
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
P3_ROOT = ROOT / "outputs" / "p3_10000"
MASK_ROOT = P3_ROOT / "candidate_masks"
OUTPUT_ROOT = ROOT / "outputs" / "p3_geometric_10000"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

input_csv = P3_ROOT / "p3_candidates_10000.csv"
output_csv = OUTPUT_ROOT / "geometric_features_10000.csv"

rows = list(csv.DictReader(input_csv.open("r", encoding="utf-8")))

passed = 0
failed = 0
total_regions = 0

with output_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "index",
        "image",
        "region_id",
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
    ])

    for row in rows:
        index = int(row["index"])

        mask_files = list(
            MASK_ROOT.glob(f"{index:05d}_*_candidate.png")
        )

        if not mask_files:
            failed += 1
            continue

        mask = cv2.imread(
            str(mask_files[0]),
            cv2.IMREAD_GRAYSCALE
        )

        if mask is None:
            failed += 1
            continue

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        image_regions = 0

        for region_id, contour in enumerate(contours, 1):

            area = float(cv2.contourArea(contour))

            if area <= 0:
                continue

            perimeter = float(
                cv2.arcLength(contour, True)
            )

            x, y, width, height = cv2.boundingRect(contour)

            aspect_ratio = (
                width / height
                if height > 0 else 0
            )

            hull = cv2.convexHull(contour)
            hull_area = float(
                cv2.contourArea(hull)
            )

            solidity = (
                area / hull_area
                if hull_area > 0 else 0
            )

            circularity = (
                (4.0 * np.pi * area) /
                (perimeter * perimeter)
                if perimeter > 0 else 0
            )

            moments = cv2.moments(contour)

            if moments["m00"] != 0:
                centroid_x = (
                    moments["m10"] / moments["m00"]
                )
                centroid_y = (
                    moments["m01"] / moments["m00"]
                )
            else:
                centroid_x = 0
                centroid_y = 0

            writer.writerow([
                index,
                row["image"],
                region_id,
                f"{area:.4f}",
                f"{perimeter:.4f}",
                x,
                y,
                width,
                height,
                f"{aspect_ratio:.6f}",
                f"{solidity:.6f}",
                f"{circularity:.6f}",
                f"{centroid_x:.4f}",
                f"{centroid_y:.4f}"
            ])

            image_regions += 1
            total_regions += 1

        passed += 1

        if index % 500 == 0 or index == len(rows):
            print(
                f"[{index:5d}/{len(rows):5d}] "
                f"PASS={passed} FAIL={failed} "
                f"regions={total_regions}"
            )

print()
print("=" * 70)
print("P3 — GEOMETRIC FEATURE EXTRACTION COMPLETE")
print("=" * 70)
print(f"Images processed  : {len(rows)}")
print(f"Passed            : {passed}")
print(f"Failed            : {failed}")
print(f"Total regions     : {total_regions}")
print(f"CSV               : {output_csv}")
print("=" * 70)
