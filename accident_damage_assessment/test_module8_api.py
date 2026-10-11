from pathlib import Path
import sys
import requests

BASE_URL = "http://127.0.0.1:5000"

DATASET = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data 1"
)

print("=" * 60)
print("AIM002 MODULE 8 - BACKEND/API TEST")
print("=" * 60)

# ---------------------------------------------------------
# TEST 1: Health endpoint
# ---------------------------------------------------------
print("\n[1/4] Testing Flask health endpoint...")

try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print("HTTP:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 200
    print("PASS")
except Exception as exc:
    print("FAIL:", exc)
    sys.exit(1)


# ---------------------------------------------------------
# TEST 2: Find a real dataset image
# ---------------------------------------------------------
print("\n[2/4] Finding test image...")

extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

images = sorted(
    p for p in DATASET.rglob("*")
    if p.is_file() and p.suffix.lower() in extensions
)

if not images:
    print("FAIL: No images found.")
    sys.exit(1)

test_image = images[0]

print("Test image:", test_image)
print("PASS")


# ---------------------------------------------------------
# TEST 3: Real P1 -> P4 API analysis
# ---------------------------------------------------------
print("\n[3/4] Testing real P1 -> P4 API analysis...")

try:
    with open(test_image, "rb") as f:
        files = {
            "image": (
                test_image.name,
                f,
                "image/jpeg"
            )
        }

        response = requests.post(
            f"{BASE_URL}/api/analyze",
            files=files,
            timeout=180
        )

    print("HTTP:", response.status_code)

    assert response.status_code == 200

    result = response.json()

    print("Result ID:", result.get("result_id"))
    print("Pipeline:", result.get("pipeline"))

    p4 = result.get("p4", {})

    print("Severity:", p4.get("severity"))
    print("Damage %:", p4.get("damage_percent"))
    print("Regions:", p4.get("region_count"))

    assert result.get("success") is True
    assert result.get("pipeline") == ["P1", "P2", "P3", "P4"]

    print("PASS")

except Exception as exc:
    print("FAIL:", exc)
    sys.exit(1)


# ---------------------------------------------------------
# TEST 4: Verify returned artifacts
# ---------------------------------------------------------
print("\n[4/4] Checking generated artifacts...")

artifacts = result.get("artifacts", {})

print("Artifacts returned:", len(artifacts))

if not artifacts:
    print("FAIL: No artifacts returned.")
    sys.exit(1)

for name, url in artifacts.items():
    print(f"  {name}: {url}")

print("PASS")

print("\n" + "=" * 60)
print("MODULE 8 BASIC API TEST: PASSED")
print("=" * 60)
