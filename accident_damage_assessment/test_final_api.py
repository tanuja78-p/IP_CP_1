from pathlib import Path

from app import app


DATASET = Path(
    r"C:\Users\tanuj\OneDrive\Documents"
    r"\AIM002_Member1_Starter_Implementation"
    r"\data 1"
)


def find_image():
    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    for path in DATASET.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            return path

    raise FileNotFoundError(
        "No dataset image was found."
    )


image_path = find_image()

print("=" * 70)
print("AIM002 REAL API END-TO-END TEST")
print("=" * 70)
print(f"Test image: {image_path.name}")
print()

client = app.test_client()

with image_path.open("rb") as image_file:

    response = client.post(
        "/api/analyze",
        data={
            "image": (
                image_file,
                image_path.name
            )
        },
        content_type="multipart/form-data"
    )

print(f"HTTP status: {response.status_code}")

if response.status_code != 200:
    print(response.get_json())
    raise SystemExit(1)

data = response.get_json()

required = [
    "success",
    "result_id",
    "input_filename",
    "pipeline",
    "p1",
    "p2",
    "p3",
    "p4",
    "artifacts"
]

missing = [
    key for key in required
    if key not in data
]

if missing:
    print("Missing response keys:", missing)
    raise SystemExit(1)

print()
print("Response contract: PASS")
print("Pipeline:", data["pipeline"])
print("Result ID:", data["result_id"])

p4 = data["p4"]

print("Severity:", p4.get("severity"))
print("Severity score:", p4.get("severity_score"))
print("Damage percent:", p4.get("damage_percent"))
print("Region count:", p4.get("region_count"))

artifacts = data["artifacts"]

print()
print("Artifact URLs:")

for name, url in artifacts.items():
    print(f"  {name}: {url}")

# Verify every returned artifact through Flask
for name, url in artifacts.items():
    artifact_response = client.get(url)

    if artifact_response.status_code != 200:
        print(
            f"Artifact verification FAILED: "
            f"{name} -> HTTP {artifact_response.status_code}"
        )
        raise SystemExit(1)

print()
print("=" * 70)
print("STATUS: REAL API END-TO-END PASSED")
print("=" * 70)
