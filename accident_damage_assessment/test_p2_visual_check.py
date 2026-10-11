from pathlib import Path
import cv2
import numpy as np

from ip.pipeline import AccidentDamagePipeline


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_ROOT = PROJECT_ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "p2_visual_check"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

pipeline = AccidentDamagePipeline()

images = sorted(INPUT_ROOT.rglob("*.png"))[:100]

print("=" * 70)
print("P2 AUTOMATIC VISUAL-CHECK GENERATION")
print("=" * 70)

created = 0

for index, image_path in enumerate(images, start=1):

    result = pipeline.process(image_path)

    clahe = result["p1_clahe"]
    mask = result["p2_mask"]
    vehicle = result["p2_vehicle"]

    coverage = np.count_nonzero(mask) / mask.size

    # Create a color visualization of the mask.
    original_color = cv2.cvtColor(clahe, cv2.COLOR_GRAY2BGR)

    overlay = original_color.copy()

    # Highlight the segmented region.
    overlay[mask > 0] = (
        0.55 * overlay[mask > 0] +
        0.45 * np.array([0, 255, 0])
    ).astype(np.uint8)

    # Put the three views side by side.
    original_view = cv2.cvtColor(clahe, cv2.COLOR_GRAY2BGR)
    mask_view = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    vehicle_view = cv2.cvtColor(vehicle, cv2.COLOR_GRAY2BGR)

    # Add labels.
    cv2.putText(
        original_view,
        "P1 CLAHE",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        mask_view,
        "P2 MASK",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        vehicle_view,
        f"P2 VEHICLE {coverage:.1%}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    comparison = np.hstack([
        original_view,
        mask_view,
        vehicle_view
    ])

    output_path = OUTPUT_ROOT / f"{index:03d}_{image_path.stem}_p2.jpg"

    cv2.imwrite(str(output_path), comparison)

    created += 1

print()
print(f"Comparisons created : {created}")
print(f"Output folder       : {OUTPUT_ROOT}")
print("=" * 70)

# Identify the suspicious high-coverage cases.
print()
print("High-coverage cases (>95%):")

high_count = 0

for index, image_path in enumerate(images, start=1):

    result = pipeline.process(image_path)
    mask = result["p2_mask"]

    coverage = np.count_nonzero(mask) / mask.size

    if coverage > 0.95:
        high_count += 1
        print(
            f"  {index:03d} {image_path.name} "
            f"coverage={coverage:.2%}"
        )

print()
print(f"High-coverage cases : {high_count}")
print("=" * 70)
