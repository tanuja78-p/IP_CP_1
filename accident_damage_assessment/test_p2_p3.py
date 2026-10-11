from pathlib import Path
import cv2
import numpy as np

from ip.pipeline import AccidentDamagePipeline
from ip.damage_detection import DamageCandidateDetector


ROOT = Path(__file__).resolve().parent

INPUT_ROOT = ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = ROOT / "outputs" / "p3_test"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

pipeline = AccidentDamagePipeline()
detector = DamageCandidateDetector()

images = sorted(INPUT_ROOT.rglob("*.png"))[:100]

passed = 0
failed = 0
total_candidates = 0

print("=" * 70)
print("P2 → P3 DAMAGE CANDIDATE TEST")
print("=" * 70)

for index, image_path in enumerate(images, start=1):

    try:

        result = pipeline.process(image_path)

        vehicle = result["p2_vehicle"]
        vehicle_mask = result["p2_mask"]

        p3 = detector.detect(
            vehicle,
            vehicle_mask
        )

        candidate_mask = p3["candidate_mask"]

        if candidate_mask.dtype != np.uint8:
            raise ValueError("Candidate mask must be uint8.")

        if candidate_mask.shape != vehicle.shape:
            raise ValueError(
                "Candidate mask dimensions do not match vehicle."
            )

        unique = set(
            np.unique(candidate_mask).tolist()
        )

        if not unique.issubset({0, 255}):
            raise ValueError(
                f"Invalid candidate mask values: {unique}"
            )

        candidates = p3["candidates"]

        total_candidates += len(candidates)

        cv2.imwrite(
            str(
                OUTPUT_ROOT /
                f"{index:03d}_candidate_mask.png"
            ),
            candidate_mask
        )

        passed += 1

        print(
            f"[PASS] {index:03d} "
            f"{image_path.name} "
            f"candidates={len(candidates)}"
        )

    except Exception as exc:

        failed += 1

        print(
            f"[FAIL] {index:03d} "
            f"{image_path.name}: {exc}"
        )


print()
print("=" * 70)
print("P2 → P3 TEST COMPLETE")
print("=" * 70)
print(f"Images tested     : {len(images)}")
print(f"Passed            : {passed}")
print(f"Failed            : {failed}")
print(f"Total candidates  : {total_candidates}")
print("=" * 70)
