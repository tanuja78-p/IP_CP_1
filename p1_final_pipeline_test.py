from pathlib import Path
import cv2

from backend.preprocessing.enhancement import ImageEnhancer


PROJECT_DIR = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

TEST_DIR = PROJECT_DIR / "data" / "p2_test_set"


def test_p1_output(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        return False, "Cannot read image"

    if len(image.shape) != 2:
        return False, "Output is not grayscale"

    if image.dtype != "uint8":
        return False, f"Wrong dtype: {image.dtype}"

    height, width = image.shape

    if height <= 0 or width <= 0:
        return False, "Invalid dimensions"

    return True, f"{width}x{height}, grayscale, uint8"


def main():
    print("=" * 70)
    print("AIM002 - FINAL P1 PIPELINE VALIDATION")
    print("=" * 70)

    if not TEST_DIR.exists():
        print("ERROR: P2 test set does not exist:")
        print(TEST_DIR)
        return

    enhancer = ImageEnhancer(target_width=1280)

    image_files = list(TEST_DIR.rglob("*.png"))

    print()
    print(f"Test images found: {len(image_files)}")
    print()

    passed = 0
    failed = 0

    for image_path in sorted(image_files):

        image = cv2.imread(str(image_path))

        if image is None:
            print(f"[FAIL] {image_path.name} - cannot read")
            failed += 1
            continue

        try:
            result = enhancer.enhance(image)

            p2_input = result["clahe"]

            if p2_input is None:
                raise ValueError("CLAHE output is None")

            if len(p2_input.shape) != 2:
                raise ValueError("CLAHE output is not grayscale")

            if p2_input.dtype != "uint8":
                raise ValueError(
                    f"CLAHE output dtype is {p2_input.dtype}"
                )

            height, width = p2_input.shape

            if height <= 0 or width <= 0:
                raise ValueError("Invalid output dimensions")

            print(
                f"[PASS] {image_path.name} -> "
                f"{width}x{height}, grayscale, uint8"
            )

            passed += 1

        except Exception as exc:
            print(f"[FAIL] {image_path.name} -> {exc}")
            failed += 1

    print()
    print("=" * 70)
    print("FINAL P1 VALIDATION RESULT")
    print("=" * 70)

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    print()

    if failed == 0:
        print("STATUS: P1 PIPELINE LOCKED")
        print()
        print("Final P1 output:")
        print("CLAHE-enhanced grayscale image")
        print("Format: uint8")
        print("Channels: 1")
        print("Ready for P2 segmentation.")

    else:
        print("STATUS: P1 REQUIRES REVIEW")


if __name__ == "__main__":
    main()