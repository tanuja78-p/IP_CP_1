import csv
from pathlib import Path

ROOT = Path(".")

geo_path = (
    ROOT
    / "outputs"
    / "p3_geometric_10000"
    / "geometric_features_10000.csv"
)

old_tex = (
    ROOT
    / "outputs"
    / "p4_texture_10000"
    / "texture_features_10000.csv"
)

rows = list(csv.DictReader(geo_path.open("r", encoding="utf-8")))

old_keys = set()

with old_tex.open("r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        old_keys.add((row["index"], row["image"]))

affected = [
    row for row in rows
    if (row["index"], row["image"]) not in old_keys
]

test_path = ROOT / "outputs" / "p4_texture_10000_fixed" / "affected_geometric_rows.csv"
test_path.parent.mkdir(parents=True, exist_ok=True)

with test_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(affected)

print("=" * 70)
print("AFFECTED P4 TEST SET")
print("=" * 70)
print(f"Affected images : {len(set((r['index'], r['image']) for r in affected))}")
print(f"Affected regions: {len(affected):,}")
print(f"Saved           : {test_path}")
print("=" * 70)
