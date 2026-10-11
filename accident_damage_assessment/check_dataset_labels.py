from pathlib import Path
from collections import Counter

ROOT = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

DATASET = ROOT / "data 1"

images = [
    p for p in DATASET.rglob("*")
    if p.is_file()
    and p.suffix.lower() in {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp"
    }
]

folders = Counter(
    p.parent.name
    for p in images
)

print()
print("=" * 70)
print("DATASET LABEL STRUCTURE CHECK")
print("=" * 70)
print(f"Total images : {len(images)}")
print()

for folder, count in sorted(
    folders.items(),
    key=lambda x: (-x[1], x[0])
):
    print(f"{folder:40s} : {count}")

print("=" * 70)

severity_names = {
    "minor",
    "moderate",
    "severe",
    "no_damage",
    "nodamage",
    "no-damage",
    "undamaged",
    "damaged"
}

found = [
    folder
    for folder in folders
    if folder.lower() in severity_names
]

if found:
    print("Potential label folders found:")
    for folder in found:
        print(f"  {folder}")
else:
    print("STATUS: NO CONFIRMED SEVERITY LABEL FOLDERS FOUND")
