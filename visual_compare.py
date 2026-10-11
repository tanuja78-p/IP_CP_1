from pathlib import Path
import cv2
import numpy as np


PROJECT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

INPUT_DIR = PROJECT_DIR / "data 1"
RESULTS_DIR = PROJECT_DIR / "data" / "enhancement_results"
OUTPUT_DIR = RESULTS_DIR / "visual_comparisons"

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

SAMPLES_PER_CLASS = 5


def find_images():
    damage_images = []
    whole_images = []

    for path in INPUT_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in VALID_EXTENSIONS:
            continue

        path_string = str(path).lower()

        if "00-damage" in path_string:
            damage_images.append(path)

        elif "01-whole" in path_string:
            whole_images.append(path)

    damage_images.sort()
    whole_images.sort()

    return damage_images[:SAMPLES_PER_CLASS], whole_images[:SAMPLES_PER_CLASS]


def create_comparison(image_path, index):
    relative_path = image_path.relative_to(INPUT_DIR)

    result_folder = (
        RESULTS_DIR
        / relative_path.parent
        / image_path.stem
    )

    methods = [
        ("original", "Original"),
        ("gray", "Grayscale"),
        ("gaussian", "Gaussian"),
        ("median", "Median"),
        ("histogram_equalized", "Histogram Equalized"),
        ("clahe", "CLAHE"),
    ]

    panels = []

    for method, label in methods:
        image_file = result_folder / f"{method}.png"

        if not image_file.exists():
            print(f"[SKIP] Missing: {image_file}")
            return

        image = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)

        if image is None:
            print(f"[SKIP] Could not read: {image_file}")
            return

        image = cv2.resize(image, (320, 240))

        # Convert grayscale to BGR so text can be added consistently.
        panel = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        cv2.rectangle(
            panel,
            (0, 0),
            (319, 35),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            panel,
            label,
            (10, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        panels.append(panel)

    top_row = cv2.hconcat(panels[:3])
    bottom_row = cv2.hconcat(panels[3:])
    comparison = cv2.vconcat([top_row, bottom_row])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_name = f"comparison_{index}_{image_path.stem}.jpg"
    output_path = OUTPUT_DIR / output_name

    cv2.imwrite(str(output_path), comparison)

    print(f"[SAVED] {output_path}")


def main():
    print("=" * 70)
    print("AIM002 - VISUAL ENHANCEMENT COMPARISON")
    print("=" * 70)

    if not INPUT_DIR.exists():
        print("ERROR: Dataset folder not found:")
        print(INPUT_DIR)
        return

    damage_images, whole_images = find_images()

    print()
    print(f"Damage samples found : {len(damage_images)}")
    print(f"Whole samples found  : {len(whole_images)}")
    print()

    index = 1

    print("PROCESSING DAMAGE SAMPLES")
    print("-" * 70)

    for image_path in damage_images:
        print(f"Image: {image_path.name}")
        create_comparison(image_path, index)
        index += 1

    print()
    print("PROCESSING WHOLE VEHICLE SAMPLES")
    print("-" * 70)

    for image_path in whole_images:
        print(f"Image: {image_path.name}")
        create_comparison(image_path, index)
        index += 1

    print()
    print("=" * 70)
    print("VISUAL COMPARISON COMPLETE")
    print("=" * 70)
    print()
    print("Results saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
    