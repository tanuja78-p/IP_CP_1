from pathlib import Path
import csv
import cv2
import numpy as np

from ip.pipeline import AccidentDamagePipeline


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_ROOT = PROJECT_ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "p2_evaluation"
MASK_ROOT = OUTPUT_ROOT / "masks"
VEHICLE_ROOT = OUTPUT_ROOT / "vehicle"

MASK_ROOT.mkdir(parents=True, exist_ok=True)
VEHICLE_ROOT.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_ROOT.rglob("*.png"))

if not images:
    raise FileNotFoundError("No P1 images found.")

pipeline = AccidentDamagePipeline()

# Representative P2 evaluation set.
TEST_LIMIT = min(100, len(images))

rows = []
passed = 0
failed = 0

print("=" * 70)
print("AIM002 P2 REPRESENTATIVE EVALUATION")
print("=" * 70)
print(f"P1 images available : {len(images)}")
print(f"P2 images tested    : {TEST_LIMIT}")
print()

for index, image_path in enumerate(images[:TEST_LIMIT], start=1):

    try:
        result = pipeline.process(image_path)

        clahe = result["p1_clahe"]
        mask = result["p2_mask"]
        vehicle = result["p2_vehicle"]

        total_pixels = mask.size
        vehicle_pixels = int(np.count_nonzero(mask))
        coverage = vehicle_pixels / total_pixels if total_pixels else 0.0

        unique_values = np.unique(mask)

        valid_binary = set(unique_values.tolist()).issubset({0, 255})
        valid_dtype = mask.dtype == np.uint8
        valid_shape = mask.shape == clahe.shape
        valid_vehicle = vehicle.shape == clahe.shape
        nonempty = vehicle_pixels > 0

        # Sanity check only.
        # These are not segmentation accuracy scores.
        reasonable_coverage = 0.005 <= coverage <= 0.95

        valid = (
            valid_binary
            and valid_dtype
            and valid_shape
            and valid_vehicle
            and nonempty
            and reasonable_coverage
        )

        relative = image_path.relative_to(INPUT_ROOT)

        mask_path = MASK_ROOT / relative
        vehicle_path = VEHICLE_ROOT / relative

        mask_path.parent.mkdir(parents=True, exist_ok=True)
        vehicle_path.parent.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(mask_path), mask)
        cv2.imwrite(str(vehicle_path), vehicle)

        rows.append({
            "index": index,
            "image": str(relative),
            "height": clahe.shape[0],
            "width": clahe.shape[1],
            "vehicle_pixels": vehicle_pixels,
            "total_pixels": total_pixels,
            "mask_coverage": round(coverage, 6),
            "valid_binary": valid_binary,
            "valid_dtype": valid_dtype,
            "valid_shape": valid_shape,
            "valid_vehicle_shape": valid_vehicle,
            "nonempty": nonempty,
            "reasonable_coverage": reasonable_coverage,
            "status": "PASS" if valid else "CHECK"
        })

        if valid:
            passed += 1
            print(
                f"[PASS] {index:03d} "
                f"{image_path.name} "
                f"coverage={coverage:.2%}"
            )
        else:
            failed += 1
            print(
                f"[CHECK] {index:03d} "
                f"{image_path.name} "
                f"coverage={coverage:.2%}"
            )

    except Exception as exc:

        failed += 1

        rows.append({
            "index": index,
            "image": str(image_path.relative_to(INPUT_ROOT)),
            "height": "",
            "width": "",
            "vehicle_pixels": "",
            "total_pixels": "",
            "mask_coverage": "",
            "valid_binary": False,
            "valid_dtype": False,
            "valid_shape": False,
            "valid_vehicle_shape": False,
            "nonempty": False,
            "reasonable_coverage": False,
            "status": "FAIL"
        })

        print(f"[FAIL] {index:03d} {image_path.name}: {exc}")


csv_path = OUTPUT_ROOT / "p2_evaluation.csv"

fieldnames = [
    "index",
    "image",
    "height",
    "width",
    "vehicle_pixels",
    "total_pixels",
    "mask_coverage",
    "valid_binary",
    "valid_dtype",
    "valid_shape",
    "valid_vehicle_shape",
    "nonempty",
    "reasonable_coverage",
    "status"
]

with csv_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


coverage_values = [
    row["mask_coverage"]
    for row in rows
    if isinstance(row["mask_coverage"], (float, int))
]

print()
print("=" * 70)
print("P2 REPRESENTATIVE EVALUATION RESULT")
print("=" * 70)
print(f"Images tested       : {TEST_LIMIT}")
print(f"Sanity-check passed : {passed}")
print(f"Needs checking      : {failed}")

if coverage_values:
    print(f"Minimum coverage    : {min(coverage_values):.2%}")
    print(f"Maximum coverage    : {max(coverage_values):.2%}")
    print(f"Average coverage    : {sum(coverage_values)/len(coverage_values):.2%}")

print()
print(f"CSV                 : {csv_path}")
print(f"Masks               : {MASK_ROOT}")
print(f"Vehicle images      : {VEHICLE_ROOT}")
print("=" * 70)

print()
print("NOTE:")
print("Mask coverage is a sanity-check metric,")
print("not segmentation accuracy or IoU.")
