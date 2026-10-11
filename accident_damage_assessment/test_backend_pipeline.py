from pathlib import Path
import json

from ip.pipeline import AccidentDamagePipeline


BASE_DIR = Path(__file__).resolve().parent

dataset_roots = [
    BASE_DIR.parent / "data 1",
    BASE_DIR / "data",
    BASE_DIR.parent / "data"
]

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

test_image = None

for root in dataset_roots:
    if not root.exists():
        continue

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in image_extensions:
            test_image = path
            break

    if test_image is not None:
        break

if test_image is None:
    raise FileNotFoundError(
        "Could not locate a test image."
    )

output_dir = (
    BASE_DIR /
    "outputs" /
    "backend_integration_test"
)

pipeline = AccidentDamagePipeline()

result = pipeline.run(
    test_image,
    output_dir
)

required = [
    "success",
    "input_file",
    "pipeline",
    "p1",
    "p2",
    "p3",
    "p4",
    "saved_files"
]

missing = [
    key for key in required
    if key not in result
]

if missing:
    raise AssertionError(
        f"Missing backend result fields: {missing}"
    )

if result["pipeline"] != [
    "P1",
    "P2",
    "P3",
    "P4"
]:
    raise AssertionError(
        "Pipeline stages are incorrect."
    )

p4 = result["p4"]

for key in [
    "severity",
    "severity_score",
    "damage_percent",
    "region_count",
    "regions"
]:
    if key not in p4:
        raise AssertionError(
            f"Missing P4 field: {key}"
        )

saved = result["saved_files"]

for key in [
    "enhanced",
    "vehicle_mask",
    "vehicle",
    "candidate_mask"
]:
    path = Path(saved[key])

    if not path.exists():
        raise AssertionError(
            f"Expected output does not exist: {path}"
        )

json_path = (
    output_dir /
    "backend_test_result.json"
)

with open(
    json_path,
    "w",
    encoding="utf-8"
) as handle:
    json.dump(
        result,
        handle,
        indent=2
    )

print("=" * 70)
print("BACKEND P1 -> P4 INTEGRATION TEST")
print("=" * 70)
print(f"Test image       : {test_image}")
print(f"Pipeline         : {' -> '.join(result['pipeline'])}")
print(f"Candidate count  : {result['p3']['candidate_count']}")
print(f"Damage percent   : {p4['damage_percent']:.4f}")
print(f"Region count     : {p4['region_count']}")
print(f"Severity         : {p4['severity']}")
print(f"Severity score   : {p4['severity_score']:.4f}")
print(f"Validation flag  : {p4['severity_validated']}")
print(f"Result JSON      : {json_path}")
print("=" * 70)
print("STATUS: BACKEND PIPELINE PASSED")
print("=" * 70)
