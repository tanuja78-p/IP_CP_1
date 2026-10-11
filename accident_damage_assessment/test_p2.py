from pathlib import Path

import cv2

from ip.segmentation import VehicleSegmenter


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_ROOT = PROJECT_ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "p2_test"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_ROOT.rglob("*.png"))[:5]

if not images:
    raise FileNotFoundError("No P1 PNG images found.")

segmenter = VehicleSegmenter()

print("=" * 60)
print("P2 SEGMENTATION TEST")
print("=" * 60)

for index, image_path in enumerate(images, start=1):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"[FAILED] {image_path}")
        continue

    mask, vehicle = segmenter.segment(image)

    mask_path = OUTPUT_ROOT / f"sample_{index}_mask.png"
    vehicle_path = OUTPUT_ROOT / f"sample_{index}_vehicle.png"

    cv2.imwrite(str(mask_path), mask)
    cv2.imwrite(str(vehicle_path), vehicle)

    print(f"[OK] {image_path.name}")
    print(f"     Input  : {image.shape}, {image.dtype}")
    print(f"     Mask   : {mask_path}")
    print(f"     Vehicle: {vehicle_path}")

print("=" * 60)
print("P2 TEST COMPLETE")
print("=" * 60)
