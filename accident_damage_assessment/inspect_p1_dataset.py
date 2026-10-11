from pathlib import Path
from collections import defaultdict
import cv2

ROOT = Path(__file__).resolve().parent
P1_ROOT = ROOT / "outputs" / "p1_dataset"

files = sorted(
    [
        p for p in P1_ROOT.rglob("*.png")
        if p.is_file()
    ],
    key=lambda p: str(p).lower()
)

by_name = defaultdict(list)

for p in files:
    by_name[p.name].append(p)

duplicates = {
    name: paths
    for name, paths in by_name.items()
    if len(paths) > 1
}

print("=" * 70)
print("AIM002 — P1 DATASET STRUCTURE DIAGNOSTIC")
print("=" * 70)
print(f"P1 files              : {len(files)}")
print(f"Unique filenames      : {len(by_name)}")
print(f"Duplicate filenames   : {len(duplicates)}")
print()

print("First 20 P1 files:")
for p in files[:20]:
    image = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)

    if image is not None:
        print(
            f"{p.name:45s} "
            f"{image.shape[1]}x{image.shape[0]} | "
            f"{p.parent}"
        )
    else:
        print(f"{p.name:45s} READ ERROR")

print()
print("First duplicate filenames:")
for name, paths in list(duplicates.items())[:20]:
    print(f"\n{name}")
    for p in paths:
        image = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        size = (
            f"{image.shape[1]}x{image.shape[0]}"
            if image is not None else "READ ERROR"
        )
        print(f"  {size} | {p}")

print("=" * 70)
