from pathlib import Path
import csv
import time
import cv2
import numpy as np

from ip.pipeline import AccidentDamagePipeline


PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_ROOT = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data 1"
)

OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "full_p1_p2"
MASK_ROOT = OUTPUT_ROOT / "masks"
VEHICLE_ROOT = OUTPUT_ROOT / "vehicle"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
MASK_ROOT.mkdir(parents=True, exist_ok=True)
VEHICLE_ROOT.mkdir(parents=True, exist_ok=True)

EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp"
}


def collect_images(root):
    images = []

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in EXTENSIONS:
            images.append(path)

    return sorted(images)


def make_unique_output_name(index, source):
    """
    Prevent filename collisions because the dataset contains
    multiple folders with repeated filenames such as image.jpg,
    0001.jpg, etc.
    """
    relative = source.relative_to(DATASET_ROOT)

    parts = list(relative.parts)

    safe_parts = []

    for part in parts[:-1]:
        safe = "".join(
            character if character.isalnum() else "_"
            for character in part
        )
        safe_parts.append(safe)

    stem = source.stem
    safe_stem = "".join(
        character if character.isalnum() else "_"
        for character in stem
    )

    folder_tag = "_".join(safe_parts)

    if folder_tag:
        return f"{index:05d}_{folder_tag}_{safe_stem}"
    else:
        return f"{index:05d}_{safe_stem}"


print("=" * 80)
print("AIM002 — FULL DATASET P1 → P2 PROCESSING")
print("=" * 80)

print()
print(f"Dataset root:")
print(DATASET_ROOT)

if not DATASET_ROOT.exists():
    raise FileNotFoundError(
        f"Dataset folder does not exist: {DATASET_ROOT}"
    )

images = collect_images(DATASET_ROOT)

print()
print(f"Total images found : {len(images):,}")
print()

if not images:
    raise RuntimeError("No supported images were found.")

pipeline = AccidentDamagePipeline(target_width=1280)

csv_path = OUTPUT_ROOT / "full_p1_p2_results.csv"

fieldnames = [
    "index",
    "source_file",
    "source_relative_path",
    "input_width",
    "input_height",
    "output_width",
    "output_height",
    "mask_area",
    "image_area",
    "coverage",
    "mask_values",
    "status",
    "error"
]

success = 0
failed = 0
empty_masks = 0
high_coverage = 0
low_coverage = 0

total_seconds = 0.0

with csv_path.open(
    "w",
    newline="",
    encoding="utf-8"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for index, image_path in enumerate(images, start=1):

        start = time.perf_counter()

        try:

            original = cv2.imread(
                str(image_path),
                cv2.IMREAD_COLOR
            )

            if original is None:
                raise ValueError(
                    "OpenCV could not read the image."
                )

            input_height, input_width = original.shape[:2]

            result = pipeline.process(image_path)

            p1_clahe = result["p1_clahe"]
            mask = result["p2_mask"]
            vehicle = result["p2_vehicle"]

            output_height, output_width = p1_clahe.shape[:2]

            if mask.dtype != np.uint8:
                raise ValueError(
                    f"Mask dtype is {mask.dtype}, expected uint8."
                )

            if mask.ndim != 2:
                raise ValueError(
                    "Mask is not single-channel."
                )

            if vehicle.dtype != np.uint8:
                raise ValueError(
                    f"Vehicle dtype is {vehicle.dtype}, expected uint8."
                )

            if vehicle.ndim != 2:
                raise ValueError(
                    "Vehicle output is not single-channel."
                )

            if mask.shape != p1_clahe.shape:
                raise ValueError(
                    "Mask dimensions do not match P1 output."
                )

            if vehicle.shape != p1_clahe.shape:
                raise ValueError(
                    "Vehicle dimensions do not match P1 output."
                )

            unique_values = sorted(
                np.unique(mask).tolist()
            )

            if not set(unique_values).issubset({0, 255}):
                raise ValueError(
                    f"Invalid mask values: {unique_values}"
                )

            mask_area = int(
                np.count_nonzero(mask)
            )

            image_area = int(mask.size)

            coverage = (
                mask_area / image_area
                if image_area > 0
                else 0.0
            )

            if mask_area == 0:
                empty_masks += 1

            if coverage > 0.95:
                high_coverage += 1

            if coverage < 0.005:
                low_coverage += 1

            output_name = make_unique_output_name(
                index,
                image_path
            )

            mask_path = MASK_ROOT / (
                output_name + "_mask.png"
            )

            vehicle_path = VEHICLE_ROOT / (
                output_name + "_vehicle.png"
            )

            if not cv2.imwrite(
                str(mask_path),
                mask
            ):
                raise IOError(
                    "Failed to write P2 mask."
                )

            if not cv2.imwrite(
                str(vehicle_path),
                vehicle
            ):
                raise IOError(
                    "Failed to write P2 vehicle image."
                )

            elapsed = time.perf_counter() - start
            total_seconds += elapsed

            success += 1

            writer.writerow({
                "index": index,
                "source_file": image_path.name,
                "source_relative_path": str(
                    image_path.relative_to(DATASET_ROOT)
                ),
                "input_width": input_width,
                "input_height": input_height,
                "output_width": output_width,
                "output_height": output_height,
                "mask_area": mask_area,
                "image_area": image_area,
                "coverage": f"{coverage:.8f}",
                "mask_values": str(unique_values),
                "status": "PASS",
                "error": ""
            })

            if index == 1 or index % 100 == 0 or index == len(images):

                average_time = (
                    total_seconds / success
                    if success
                    else 0
                )

                remaining = len(images) - index

                estimated_remaining = (
                    remaining * average_time
                )

                print(
                    f"[{index:5d}/{len(images):5d}] "
                    f"PASS={success:5d} "
                    f"FAIL={failed:4d} "
                    f"coverage={coverage:6.2%} "
                    f"avg={average_time:.3f}s "
                    f"ETA={estimated_remaining/60:.1f} min"
                )

        except Exception as exc:

            failed += 1

            writer.writerow({
                "index": index,
                "source_file": image_path.name,
                "source_relative_path": str(
                    image_path.relative_to(DATASET_ROOT)
                ),
                "input_width": "",
                "input_height": "",
                "output_width": "",
                "output_height": "",
                "mask_area": "",
                "image_area": "",
                "coverage": "",
                "mask_values": "",
                "status": "FAIL",
                "error": str(exc)
            })

            print(
                f"[{index:5d}/{len(images):5d}] "
                f"FAIL  {image_path}"
            )


print()
print("=" * 80)
print("FULL DATASET P1 → P2 COMPLETE")
print("=" * 80)

print(f"Images found       : {len(images):,}")
print(f"Successful         : {success:,}")
print(f"Failed             : {failed:,}")
print(f"Empty masks        : {empty_masks:,}")
print(f">95% coverage      : {high_coverage:,}")
print(f"<0.5% coverage     : {low_coverage:,}")

if success:
    print(
        f"Average processing : "
        f"{total_seconds / success:.3f} sec/image"
    )

print()
print(f"CSV results        : {csv_path}")
print(f"Mask outputs       : {MASK_ROOT}")
print(f"Vehicle outputs    : {VEHICLE_ROOT}")

print("=" * 80)

if failed == 0:
    print("STATUS: ENTIRE DATASET PROCESSED SUCCESSFULLY")
else:
    print("STATUS: DATASET PROCESSING COMPLETED WITH FAILURES")
    print("Review the CSV error column before locking P2.")

