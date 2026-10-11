from pathlib import Path
import csv
import cv2

from ip.pipeline import AccidentDamagePipeline
from ip.damage_detection import DamageCandidateDetector

ROOT = Path(__file__).resolve().parent
INPUT_ROOT = ROOT / "outputs" / "p1_dataset"
OUTPUT_ROOT = ROOT / "outputs" / "p3_10000"
MASK_ROOT = OUTPUT_ROOT / "candidate_masks"

OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
MASK_ROOT.mkdir(parents=True, exist_ok=True)

images = sorted(INPUT_ROOT.rglob("*.png"))[:10000]

pipeline = AccidentDamagePipeline()
detector = DamageCandidateDetector()

csv_path = OUTPUT_ROOT / "p3_candidates_10000.csv"

passed = 0
failed = 0
total_candidates = 0

with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "index",
        "image",
        "candidate_count",
        "candidate_area",
        "vehicle_area",
        "candidate_percentage",
        "status",
        "error"
    ])

    for index, image_path in enumerate(images, 1):

        try:
            result = pipeline.process(image_path)

            p3 = detector.detect(
                result["p2_vehicle"],
                result["p2_mask"]
            )

            candidate_mask = p3["candidate_mask"]
            candidates = p3["candidates"]

            vehicle_area = int(
                (result["p2_mask"] > 0).sum()
            )

            candidate_area = int(
                (candidate_mask > 0).sum()
            )

            percentage = (
                candidate_area / vehicle_area * 100
                if vehicle_area > 0 else 0
            )

            output_name = (
                f"{index:05d}_{image_path.stem}_candidate.png"
            )

            cv2.imwrite(
                str(MASK_ROOT / output_name),
                candidate_mask
            )

            writer.writerow([
                index,
                image_path.name,
                len(candidates),
                candidate_area,
                vehicle_area,
                f"{percentage:.6f}",
                "PASS",
                ""
            ])

            passed += 1
            total_candidates += len(candidates)

            if index % 100 == 0 or index == len(images):
                print(
                    f"[{index:5d}/{len(images):5d}] "
                    f"PASS={passed} FAIL={failed} "
                    f"candidates={total_candidates}"
                )

        except Exception as exc:

            failed += 1

            writer.writerow([
                index,
                image_path.name,
                0,
                0,
                0,
                0,
                "FAIL",
                str(exc)
            ])

print()
print("=" * 70)
print("P3 — 10,000 IMAGE PROCESSING COMPLETE")
print("=" * 70)
print(f"Images processed  : {len(images)}")
print(f"Passed            : {passed}")
print(f"Failed            : {failed}")
print(f"Total candidates  : {total_candidates}")
print(f"CSV               : {csv_path}")
print(f"Masks             : {MASK_ROOT}")
print("=" * 70)
