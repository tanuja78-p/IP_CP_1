from pathlib import Path
import csv
from collections import Counter
import cv2

ROOT = Path(__file__).resolve().parent

P1_ROOT = ROOT / "outputs" / "p1_dataset"

GEOMETRIC_CSV = (
    ROOT / "outputs" / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

files = sorted(
    [
        p for p in P1_ROOT.rglob("*.png")
        if p.is_file()
    ],
    key=lambda p: str(p).lower()
)

by_name = {}

for p in files:
    by_name.setdefault(p.name, []).append(p)

rows = list(csv.DictReader(
    GEOMETRIC_CSV.open("r", encoding="utf-8")
))

cache = {}
stats = Counter()

examples = {}

for number, row in enumerate(rows, 1):

    name = row["image"]

    x = int(row["x"])
    y = int(row["y"])
    w = int(row["width"])
    h = int(row["height"])

    candidates = by_name.get(name, [])

    valid_candidates = []

    for path in candidates:

        key = str(path)

        if key not in cache:
            image = cv2.imread(
                key,
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                cache[key] = None
            else:
                cache[key] = image.shape[:2]

        shape = cache[key]

        if shape is None:
            continue

        image_h, image_w = shape

        if (
            x >= 0 and
            y >= 0 and
            w > 0 and
            h > 0 and
            x + w <= image_w and
            y + h <= image_h
        ):
            valid_candidates.append(path)

    count = len(valid_candidates)

    if count == 0:
        stats["NO_VALID_CANDIDATE"] += 1
    elif count == 1:
        stats["ONE_VALID_CANDIDATE"] += 1
    else:
        stats["MULTIPLE_VALID_CANDIDATES"] += 1

    category = (
        "NO_VALID_CANDIDATE"
        if count == 0
        else "ONE_VALID_CANDIDATE"
        if count == 1
        else "MULTIPLE_VALID_CANDIDATES"
    )

    if category not in examples:
        examples[category] = []

    if len(examples[category]) < 10:
        examples[category].append({
            "index": row["index"],
            "image": name,
            "bbox": f"{x},{y},{w},{h}",
            "candidates": [
                str(p) for p in valid_candidates
            ]
        })

print("=" * 70)
print("AIM002 — BBOX-BASED P1 SOURCE MAPPING")
print("=" * 70)
print(f"Geometric rows              : {len(rows)}")
print(f"P1 files                    : {len(files)}")
print()

for key, value in stats.items():
    print(f"{key:30s}: {value}")

print()
print("Coverage:")
resolved = stats["ONE_VALID_CANDIDATE"] + stats["MULTIPLE_VALID_CANDIDATES"]
print(f"Rows with valid P1 candidate : {resolved}")
print(
    f"Rows unresolved              : "
    f"{stats['NO_VALID_CANDIDATE']}"
)

print()
print("Examples")
print("-" * 70)

for category in [
    "NO_VALID_CANDIDATE",
    "ONE_VALID_CANDIDATE",
    "MULTIPLE_VALID_CANDIDATES"
]:
    print()
    print(f"[{category}]")

    for item in examples.get(category, []):
        print(
            f"index={item['index']} | "
            f"{item['image']} | "
            f"bbox={item['bbox']}"
        )

        for candidate in item["candidates"][:5]:
            print(f"  -> {candidate}")

print("=" * 70)
