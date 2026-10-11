from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent

result_file = (
    BASE_DIR /
    "outputs" /
    "backend_integration_test" /
    "backend_test_result.json"
)

if not result_file.exists():
    raise FileNotFoundError(
        f"Backend result not found: {result_file}"
    )

with open(
    result_file,
    "r",
    encoding="utf-8"
) as handle:
    result = json.load(handle)

assert result["success"] is True

assert result["pipeline"] == [
    "P1",
    "P2",
    "P3",
    "P4"
]

assert result["p1"]["channels"] == 1
assert result["p1"]["dtype"] == "uint8"

p3 = result["p3"]
p4 = result["p4"]

assert p3["candidate_count"] >= 0
assert p3["candidate_pixels"] >= 0

assert isinstance(p4["severity"], str)
assert 0.0 <= p4["severity_score"] <= 1.0
assert p4["damage_percent"] >= 0.0
assert p4["region_count"] >= 0
assert isinstance(p4["regions"], list)

saved = result["saved_files"]

for key in [
    "enhanced",
    "vehicle_mask",
    "vehicle",
    "candidate_mask"
]:
    path = Path(saved[key])

    assert path.exists(), (
        f"Missing saved output: {path}"
    )

print("=" * 70)
print("BACKEND OUTPUT CONTRACT VALIDATION")
print("=" * 70)
print("P1 output contract       : PASS")
print("P2 output contract       : PASS")
print("P3 output contract       : PASS")
print("P4 output contract       : PASS")
print("Saved output files       : PASS")
print("Final JSON structure     : PASS")
print("=" * 70)
print("STATUS: OUTPUT CONTRACT PASSED")
print("=" * 70)
