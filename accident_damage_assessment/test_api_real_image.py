from pathlib import Path
from app import app

BASE_DIR = Path(__file__).resolve().parent

image_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

test_image = None

for root in [
    BASE_DIR.parent / "data 1",
    BASE_DIR / "data",
]:
    if not root.exists():
        continue

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in image_extensions:
            test_image = path
            break

    if test_image:
        break

if test_image is None:
    raise FileNotFoundError("No test image found.")

with app.test_client() as client:
    with open(test_image, "rb") as handle:
        response = client.post(
            "/api/upload",
            data={
                "image": (
                    handle,
                    test_image.name
                )
            },
            content_type="multipart/form-data"
        )

print("=" * 70)
print("BACKEND API REAL IMAGE TEST")
print("=" * 70)
print(f"HTTP status : {response.status_code}")

if response.status_code != 200:
    print(response.get_json())
    raise AssertionError("API upload test failed.")

data = response.get_json()

required = [
    "success",
    "input_file",
    "original_filename",
    "pipeline",
    "p1",
    "p2",
    "p3",
    "p4",
    "saved_files"
]

missing = [
    key for key in required
    if key not in data
]

if missing:
    raise AssertionError(
        f"Missing response fields: {missing}"
    )

if data["success"] is not True:
    raise AssertionError("API returned success=False.")

if data["pipeline"] != [
    "P1",
    "P2",
    "P3",
    "P4"
]:
    raise AssertionError("Incorrect pipeline sequence.")

print(f"Pipeline    : {' -> '.join(data['pipeline'])}")
print(f"Severity    : {data['p4']['severity']}")
print(f"Damage %    : {data['p4']['damage_percent']:.4f}")
print(f"Regions     : {data['p4']['region_count']}")
print("=" * 70)
print("STATUS: API REAL IMAGE TEST PASSED")
print("=" * 70)
