from pathlib import Path
import csv

ROOT = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation"
)

DATASET = ROOT / "data 1"
OUTPUT = ROOT / "accident_damage_assessment" / "outputs"

images = sorted(
    p for p in DATASET.rglob("*")
    if p.is_file() and p.suffix.lower() in {
        ".jpg", ".jpeg", ".png", ".bmp",
        ".tif", ".tiff", ".webp"
    }
)

selected = images[:10000]

manifest = OUTPUT / "working_dataset_10000.csv"
manifest.parent.mkdir(parents=True, exist_ok=True)

with manifest.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["index", "source_path"])
    for i, path in enumerate(selected, 1):
        writer.writerow([
            i,
            str(path.relative_to(ROOT))
        ])

print("=" * 60)
print("10,000-IMAGE WORKING DATASET")
print("=" * 60)
print(f"Total available : {len(images):,}")
print(f"Selected        : {len(selected):,}")
print(f"Manifest        : {manifest}")
print("=" * 60)
