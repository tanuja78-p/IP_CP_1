from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent

MAPPING_CSV = ROOT / "outputs" / "p4_texture_10000_fixed" / "index_source_mapping.csv"
GEOMETRIC_CSV = ROOT / "outputs" / "p3_geometric_10000" / "geometric_features_10000.csv"

mapping = {
    row["index"]: row["source_path"]
    for row in csv.DictReader(
        MAPPING_CSV.open("r", encoding="utf-8")
    )
}

rows = list(
    csv.DictReader(
        GEOMETRIC_CSV.open("r", encoding="utf-8")
    )
)

missing = []
invalid = []
valid = 0

for row in rows:
    index = row["index"]
    source = mapping.get(index)

    if source is None:
        missing.append(index)
        continue

    path = Path(source)

    if not path.exists():
        invalid.append((index, source))
    else:
        valid += 1

print("=" * 70)
print("AIM002 — INDEX SOURCE MAPPING VERIFICATION")
print("=" * 70)
print(f"Geometric rows       : {len(rows)}")
print(f"Valid source paths   : {valid}")
print(f"Missing mappings     : {len(missing)}")
print(f"Invalid paths        : {len(invalid)}")

if missing:
    print("STATUS: FAIL — missing index mappings")
elif invalid:
    print("STATUS: FAIL — invalid source paths")
else:
    print("STATUS: PASS — every geometric row has a valid exact source")
print("=" * 70)
