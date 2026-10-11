from pathlib import Path
import time
import cv2
import csv

from backend.preprocessing.enhancement import ImageEnhancer


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

INPUT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data 1"
)

OUTPUT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data\enhancement_results"
)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

enhancer = ImageEnhancer(target_width=1280)


# ---------------------------------------------------------
# ENHANCEMENT
# ---------------------------------------------------------

def process_image(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"[SKIP] Cannot read: {image_path}")
        return None

    start = time.perf_counter()

    # Resize
    resized = enhancer.resize_image(image)

    # Grayscale
    gray = enhancer.convert_to_grayscale(resized)

    # Gaussian filtering
    gaussian = enhancer.gaussian_filter(gray)

    # Median filtering
    median = enhancer.median_filter(gray)

    # Histogram equalization
    histogram_equalized = enhancer.histogram_equalization(gaussian)

    # CLAHE
    clahe = enhancer.clahe_enhancement(gaussian)

    processing_time = (time.perf_counter() - start) * 1000

    return {
        "original": resized,
        "gray": gray,
        "gaussian": gaussian,
        "median": median,
        "histogram_equalized": histogram_equalized,
        "clahe": clahe,
        "processing_time_ms": processing_time,
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    if not INPUT_DIR.exists():
        print(f"ERROR: Dataset folder not found:")
        print(INPUT_DIR)
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_files = [
        path
        for path in INPUT_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in VALID_EXTENSIONS
    ]

    print("=" * 60)
    print("AIM002 - REAL DATASET IMAGE ENHANCEMENT")
    print("=" * 60)
    print(f"Dataset folder : {INPUT_DIR}")
    print(f"Output folder  : {OUTPUT_DIR}")
    print(f"Images found   : {len(image_files)}")
    print("=" * 60)

    if not image_files:
        print("No image files found.")
        return

    csv_path = OUTPUT_DIR / "enhancement_summary.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "dataset",
            "relative_image",
            "width",
            "height",
            "method",
            "mean_intensity",
            "std_intensity",
            "processing_time_ms"
        ])

        for index, image_path in enumerate(image_files, start=1):

            print(
                f"[{index}/{len(image_files)}] "
                f"{image_path.relative_to(INPUT_DIR)}"
            )

            result = process_image(image_path)

            if result is None:
                continue

            # Preserve dataset folder structure
            relative_path = image_path.relative_to(INPUT_DIR)

            dataset_name = relative_path.parts[0]

            output_folder = (
                OUTPUT_DIR
                / relative_path.parent
                / image_path.stem
            )

            output_folder.mkdir(parents=True, exist_ok=True)

            # Save enhancement results
            for method, processed_image in result.items():

                if method == "processing_time_ms":
                    continue

                output_path = output_folder / f"{method}.png"

                cv2.imwrite(
                    str(output_path),
                    processed_image
                )

                mean_value = float(processed_image.mean())
                std_value = float(processed_image.std())

                writer.writerow([
                    dataset_name,
                    str(relative_path),
                    processed_image.shape[1],
                    processed_image.shape[0],
                    method,
                    round(mean_value, 3),
                    round(std_value, 3),
                    round(result["processing_time_ms"], 3)
                ])

    print()
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Results saved to:")
    print(OUTPUT_DIR)
    print()
    print(f"Summary CSV:")
    print(csv_path)


if __name__ == "__main__":
    main()