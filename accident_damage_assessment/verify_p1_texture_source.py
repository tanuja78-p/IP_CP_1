from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent

GEOMETRIC_CSV = (
    ROOT / "outputs" / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

P1_ROOT = ROOT / "outputs" / "p1_dataset"

rows = list(csv.DictReader(
    GEOMETRIC_CSV.open("r", encoding="utf-8")
))

# Build P1 image lookup by filename.
# Unlike the raw dataset, we will verify the dimensions
# against the geometric bounding boxes.
files = sorted(
    [
        p for p in P1_ROOT.rglob("*.png")
        if p.is_file()
    ],
    key=lambda p: str(p).lower()
)

print("=" * 70)
print("AIM002 — P1 SOURCE VERIFICATION")
print("=" * 70)
print(f"P1 PNG files found     : {len(files)}")
print(f"Geometric rows         : {len(rows)}")

# Check the first representative rows and their image dimensions.
checked = 0
valid = 0
invalid = 0

seen = set()

for row in rows:

    index = row["index"]

    if index in seen:
        continue

    seen.add(index)

    candidates = [
        p for p in files
        if p.name == row["image"]
    ]

    if len(candidates) != 1:
        invalid += 1
        continue

    image_path = candidates[0]

    import cv2

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        invalid += 1
        continue

    checked += 1

    if (
        int(row["x"]) + int(row["width"]) <= image.shape[1]
        and
        int(row["y"]) + int(row["height"]) <= image.shape[0]
    ):
        valid += 1
    else:
        invalid += 1

    if checked >= 100:
        break

print()
print(f"Unique images checked   : {checked}")
print(f"Valid bbox checks       : {valid}")
print(f"Invalid bbox checks     : {invalid}")

if checked == 100 and invalid == 0:
    print("STATUS: PASS — P1 dimensions support P3 coordinates")
else:
    print("STATUS: REVIEW — P1 mapping needs further checking")

print("=" * 70)
