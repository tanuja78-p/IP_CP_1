from pathlib import Path
import csv
import cv2

ROOT = Path(__file__).resolve().parent

P3_CSV = (
    ROOT / "outputs" / "p3_10000"
    / "p3_candidates_10000.csv"
)

P2_ROOT = (
    ROOT / "outputs" / "full_p1_p2"
    / "masks"
)

OUTPUT_ROOT = (
    ROOT / "outputs" / "severity_10000"
)

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT = (
    OUTPUT_ROOT / "damage_percentage_10000.csv"
)

rows = list(
    csv.DictReader(
        P3_CSV.open(
            "r",
            encoding="utf-8"
        )
    )
)

passed = 0
failed = 0

with OUTPUT.open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "index",
        "image",
        "candidate_count",
        "candidate_area",
        "vehicle_area",
        "damage_percentage"
    ])

    for row in rows:

        try:

            index = int(row["index"])

            mask_files = list(
                P2_ROOT.glob(
                    f"{index:05d}_*_mask.png"
                )
            )

            if not mask_files:
                raise FileNotFoundError(
                    "P2 mask not found"
                )

            vehicle_mask = cv2.imread(
                str(mask_files[0]),
                cv2.IMREAD_GRAYSCALE
            )

            if vehicle_mask is None:
                raise ValueError(
                    "Unable to read P2 mask"
                )

            vehicle_area = int(
                cv2.countNonZero(
                    vehicle_mask
                )
            )

            candidate_area = int(
                row["candidate_area"]
            )

            candidate_count = int(
                row["candidate_count"]
            )

            if vehicle_area > 0:
                damage_percentage = (
                    candidate_area /
                    vehicle_area
                ) * 100.0
            else:
                damage_percentage = 0.0

            damage_percentage = min(
                damage_percentage,
                100.0
            )

            writer.writerow([
                index,
                row["image"],
                candidate_count,
                candidate_area,
                vehicle_area,
                f"{damage_percentage:.6f}"
            ])

            passed += 1

        except Exception:
            failed += 1

print()
print("=" * 70)
print("DAMAGE PERCENTAGE CALCULATION COMPLETE")
print("=" * 70)
print(f"Images processed  : {len(rows)}")
print(f"Passed            : {passed}")
print(f"Failed            : {failed}")
print(f"CSV               : {OUTPUT}")
print("=" * 70)
