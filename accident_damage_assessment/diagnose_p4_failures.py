from pathlib import Path
import csv
from collections import Counter

ROOT = Path(__file__).resolve().parent

FAILURE_CSV = (
    ROOT / "outputs" / "p4_texture_10000_fixed"
    / "texture_failures_fixed.csv"
)

counter = Counter()

rows = list(csv.DictReader(
    FAILURE_CSV.open("r", encoding="utf-8")
))

for row in rows:
    reason = row["reason"]

    if reason.startswith("bbox outside source image"):
        counter["bbox_outside_source"] += 1
    elif "No source mapping" in reason:
        counter["missing_mapping"] += 1
    elif "Unable to read image" in reason:
        counter["image_read_error"] += 1
    elif "Empty region" in reason:
        counter["empty_region"] += 1
    else:
        counter["other"] += 1

print("=" * 70)
print("AIM002 — P4 FAILURE DIAGNOSIS")
print("=" * 70)
print(f"Total failures : {len(rows)}")
print()

for reason, count in counter.most_common():
    print(f"{reason:30s}: {count}")

print()
print("First 20 failure records:")
print("-" * 70)

for row in rows[:20]:
    print(
        f"index={row['index']} | "
        f"image={row['image']} | "
        f"region={row['region_id']} | "
        f"{row['reason']}"
    )

print("=" * 70)
