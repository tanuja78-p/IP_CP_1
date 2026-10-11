from pathlib import Path
import shutil
import cv2


PROJECT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

INPUT_DIR = PROJECT_DIR / "data 1"
RESULTS_DIR = PROJECT_DIR / "data" / "enhancement_results"
OUTPUT_DIR = PROJECT_DIR / "data" / "p2_test_set"

SAMPLES_PER_CLASS = 10


def find_samples():
    damage = []
    whole = []

    for path in INPUT_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp",
        }:
            continue

        path_string = str(path).lower()

        if "00-damage" in path_string:
            damage.append(path)

        elif "01-whole" in path_string:
            whole.append(path)

    damage.sort()
    whole.sort()

    return damage[:SAMPLES_PER_CLASS], whole[:SAMPLES_PER_CLASS]


def get_clahe_path(image_path):
    relative_path = image_path.relative_to(INPUT_DIR)

    return (
        RESULTS_DIR
        / relative_path.parent
        / image_path.stem
        / "clahe.png"
    )


def validate_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return False, "Could not read image"

    if len(image.shape) != 2:
        return False, "Image is not grayscale"

    if image.dtype != "uint8":
        return False, f"Wrong dtype: {image.dtype}"

    height, width = image.shape

    if height <= 0 or width <= 0:
        return False, "Invalid dimensions"

    return True, f"{width}x{height}, uint8, grayscale"


def copy_sample(source_image, output_class, index):
    clahe_path = get_clahe_path(source_image)

    if not clahe_path.exists():
        print(f"[ERROR] CLAHE output missing:")
        print(clahe_path)
        return False

    valid, message = validate_image(clahe_path)

    if not valid:
        print(f"[ERROR] Invalid P1 output:")
        print(clahe_path)
        print(f"Reason: {message}")
        return False

    class_folder = OUTPUT_DIR / output_class
    class_folder.mkdir(parents=True, exist_ok=True)

    output_name = f"{index:02d}_{source_image.stem}_clahe.png"
    output_path = class_folder / output_name

    shutil.copy2(clahe_path, output_path)

    print(f"[OK] {output_name} -> {message}")

    return True


def main():
    print("=" * 70)
    print("AIM002 - P1 -> P2 INTEGRATION TEST")
    print("=" * 70)

    print()
    print("P1 output required by P2:")
    print("CLAHE enhanced grayscale image")
    print("Format: PNG")
    print("Type: uint8")
    print("Channels: 1")
    print()

    damage, whole = find_samples()

    print(f"Damage samples: {len(damage)}")
    print(f"Whole samples : {len(whole)}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    print("PREPARING DAMAGE SAMPLES")
    print("-" * 70)

    for index, image_path in enumerate(damage, start=1):
        if copy_sample(image_path, "damage", index):
            successful += 1
        else:
            failed += 1

    print()
    print("PREPARING WHOLE VEHICLE SAMPLES")
    print("-" * 70)

    for index, image_path in enumerate(whole, start=1):
        if copy_sample(image_path, "whole", index):
            successful += 1
        else:
            failed += 1

    print()
    print("=" * 70)
    print("P1 -> P2 TEST SET COMPLETE")
    print("=" * 70)

    print(f"Successful samples : {successful}")
    print(f"Failed samples     : {failed}")
    print()
    print("P2 test set:")
    print(OUTPUT_DIR)

    if failed == 0:
        print()
        print("STATUS: P1 HANDOFF READY FOR P2")
    else:
        print()
        print("STATUS: CHECK FAILED SAMPLES")


if __name__ == "__main__":
    main()