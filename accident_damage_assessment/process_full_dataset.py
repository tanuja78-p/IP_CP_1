from pathlib import Path
import csv
import time

import cv2

from ip.enhancement import ImageEnhancer


DATASET_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data 1"
)

OUTPUT_DIR = Path("outputs/p1_dataset")
SUMMARY_FILE = Path("outputs/p1_dataset_summary.csv")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

enhancer = ImageEnhancer(target_width=1280)


def main():
    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATASET_DIR}"
        )

    images = [
        p for p in DATASET_DIR.rglob("*")
        if p.is_file() and p.suffix in IMAGE_EXTENSIONS
    ]

    images.sort()

    print(f"Dataset: {DATASET_DIR}")
    print(f"Images found: {len(images)}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    success_count = 0
    failure_count = 0

    total_start = time.perf_counter()

    for index, source_path in enumerate(images, start=1):
        start = time.perf_counter()

        try:
            result = enhancer.process(source_path)

            relative_path = source_path.relative_to(DATASET_DIR)
            output_relative = relative_path.with_suffix(".png")

            output_path = OUTPUT_DIR / output_relative
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if result["clahe"].ndim != 2:
                raise ValueError("CLAHE output is not single-channel.")

            if result["clahe"].dtype != "uint8":
                raise ValueError("CLAHE output is not uint8.")

            if not cv2.imwrite(str(output_path), result["clahe"]):
                raise IOError("Could not save CLAHE output.")

            elapsed_ms = (time.perf_counter() - start) * 1000

            rows.append({
                "source": str(relative_path),
                "output": str(output_relative),
                "status": "success",
                "width": result["clahe"].shape[1],
                "height": result["clahe"].shape[0],
                "channels": 1,
                "dtype": "uint8",
                "method": "CLAHE",
                "processing_time_ms": round(elapsed_ms, 3),
            })

            success_count += 1

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000

            rows.append({
                "source": str(source_path.relative_to(DATASET_DIR)),
                "output": "",
                "status": f"failed: {exc}",
                "width": "",
                "height": "",
                "channels": "",
                "dtype": "",
                "method": "",
                "processing_time_ms": round(elapsed_ms, 3),
            })

            failure_count += 1

        if index % 100 == 0 or index == len(images):
            print(
                f"[{index}/{len(images)}] "
                f"Success: {success_count} | "
                f"Failed: {failure_count}"
            )

    total_time = time.perf_counter() - total_start

    with SUMMARY_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "source",
                "output",
                "status",
                "width",
                "height",
                "channels",
                "dtype",
                "method",
                "processing_time_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 60)
    print("P1 FULL DATASET PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total images : {len(images)}")
    print(f"Successful   : {success_count}")
    print(f"Failed       : {failure_count}")
    print(f"Total time   : {total_time:.2f} seconds")
    print(f"Output       : {OUTPUT_DIR}")
    print(f"Summary CSV  : {SUMMARY_FILE}")

    if failure_count == 0:
        print()
        print("STATUS: P1 COMPLETE - ALL IMAGES PROCESSED")
    else:
        print()
        print("STATUS: P1 COMPLETE WITH FAILURES - CHECK SUMMARY CSV")


if __name__ == "__main__":
    main()
