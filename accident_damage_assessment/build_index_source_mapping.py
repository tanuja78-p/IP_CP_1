from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent

RAW_ROOT = ROOT.parent / "data 1"

GEOMETRIC_CSV = (
    ROOT
    / "outputs"
    / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

OUTPUT_CSV = (
    ROOT
    / "outputs"
    / "p4_texture_10000_fixed"
    / "index_source_mapping.csv"
)

extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

files = sorted(
    [
        p for p in RAW_ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in extensions
    ],
    key=lambda p: str(p).lower()
)

rows = list(
    csv.DictReader(
        GEOMETRIC_CSV.open("r", encoding="utf-8")
    )
)

unique_indices = sorted(
    {row["index"] for row in rows},
    key=lambda x: int(x)
)

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["index", "source_path"])

    for index in unique_indices:
        number = int(index)

        if 1 <= number <= len(files):
            writer.writerow([
                index,
                str(files[number - 1])
            ])

print("=" * 70)
print("AIM002 — EXACT INDEX → SOURCE MAPPING")
print("=" * 70)
print(f"Raw dataset           : {RAW_ROOT}")
print(f"Raw images found      : {len(files)}")
print(f"Geometric indices     : {len(unique_indices)}")
print(f"Mappings created      : {sum(1 for i in unique_indices if 1 <= int(i) <= len(files))}")
print(f"Missing mappings      : {sum(1 for i in unique_indices if not (1 <= int(i) <= len(files)))}")
print(f"CSV                   : {OUTPUT_CSV}")
print("=" * 70)
