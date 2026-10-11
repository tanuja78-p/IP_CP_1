import csv
from pathlib import Path
from collections import Counter

ROOT = Path(".")
GEO = ROOT / "outputs" / "p3_geometric_10000" / "geometric_features_10000.csv"
P1 = ROOT / "outputs" / "p1_dataset"

rows = list(csv.DictReader(GEO.open("r", encoding="utf-8")))

# Count how many physical P1 files exist for each filename.
filename_matches = {}

for path in P1.rglob("*"):
    if path.is_file():
        filename_matches.setdefault(path.name, []).append(path)

# Reproduce the 104 images that had zero texture rows.
TEX = ROOT / "outputs" / "p4_texture_10000" / "texture_features_10000.csv"

geo_keys = {(r["index"], r["image"]) for r in rows}

tex_keys = set()
with TEX.open("r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        tex_keys.add((r["index"], r["image"]))

excluded_keys = geo_keys - tex_keys

excluded_rows = [
    r for r in rows
    if (r["index"], r["image"]) in excluded_keys
]

print("=" * 75)
print("AIM002 — P4 IMAGE-IDENTITY COLLISION DIAGNOSTIC")
print("=" * 75)

print(f"\nExcluded images : {len(excluded_keys)}")
print(f"Excluded regions: {len(excluded_rows):,}")

match_counts = Counter()

for r in excluded_keys:
    count = len(filename_matches.get(r[1], []))
    match_counts[count] += 1

print("\nNumber of physical files matching each excluded filename:")

for count in sorted(match_counts):
    print(f"  {count} match(es): {match_counts[count]} images")

ambiguous = [
    r for r in excluded_keys
    if len(filename_matches.get(r[1], [])) > 1
]

print(f"\nExcluded images with duplicate filenames: {len(ambiguous)}")

print("\nFirst 20 ambiguous filenames:")

for index, image in sorted(ambiguous)[:20]:
    matches = filename_matches.get(image, [])
    print(f"\nindex={index} image={image}")
    for path in matches:
        print(f"    {path}")

print("\n" + "-" * 75)
print("SAMPLE CROP VALIDITY CHECK")
print("-" * 75)

for r in excluded_rows[:20]:
    image = r["image"]
    matches = filename_matches.get(image, [])

    print(
        f"index={r['index']} "
        f"image={image} "
        f"matches={len(matches)} "
        f"bbox=({r['x']},{r['y']},{r['width']},{r['height']})"
    )

    for path in matches[:3]:
        import cv2

        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if img is None:
            print(f"    {path} -> READ FAILED")
            continue

        x = int(r["x"])
        y = int(r["y"])
        w = int(r["width"])
        h = int(r["height"])

        crop = img[y:y+h, x:x+w]

        print(
            f"    {path.name}: "
            f"shape={img.shape}, "
            f"crop_shape={crop.shape}, "
            f"crop_empty={crop.size == 0}"
        )

print("\n" + "=" * 75)
print("DIAGNOSTIC COMPLETE")
print("=" * 75)
