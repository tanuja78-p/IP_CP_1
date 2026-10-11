from pathlib import Path
import cv2

from ip.pipeline import AccidentDamagePipeline


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_ROOT = PROJECT_ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "p1_p2_test"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_ROOT.rglob("*.png"))

if not images:
    raise FileNotFoundError(
        f"No P1 output images found in {INPUT_ROOT}"
    )

pipeline = AccidentDamagePipeline()

passed = 0
failed = 0

print("=" * 70)
print("AIM002 P1 -> P2 INTEGRATION TEST")
print("=" * 70)
print(f"P1 images available : {len(images)}")
print()

for index, image_path in enumerate(images[:20], start=1):

    try:
        result = pipeline.process(image_path)

        mask = result["p2_mask"]
        vehicle = result["p2_vehicle"]

        if not cv2.imwrite(
            str(OUTPUT_ROOT / f"{index:02d}_mask.png"),
            mask
        ):
            raise IOError("Could not save mask.")

        if not cv2.imwrite(
            str(OUTPUT_ROOT / f"{index:02d}_vehicle.png"),
            vehicle
        ):
            raise IOError("Could not save vehicle image.")

        passed += 1
        print(f"[PASS] {index:02d}  {image_path.name}")

    except Exception as exc:
        failed += 1
        print(f"[FAIL] {index:02d}  {image_path.name}")
        print(f"       {exc}")

print()
print("=" * 70)
print("P1 -> P2 RESULT")
print("=" * 70)
print(f"Images tested : {min(20, len(images))}")
print(f"Passed        : {passed}")
print(f"Failed        : {failed}")
print(f"Output        : {OUTPUT_ROOT}")
print("=" * 70)

if failed == 0:
    print("STATUS: P1 -> P2 INTEGRATION TEST PASSED")
else:
    print("STATUS: P1 -> P2 INTEGRATION TEST HAS FAILURES")
