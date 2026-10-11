from pathlib import Path
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"
DATASET = Path(
    r"C:\Users\tanuj\OneDrive\Documents\AIM002_Member1_Starter_Implementation\data 1"
)

print("=" * 65)
print("AIM002 — FRONTEND/API REGRESSION TEST")
print("=" * 65)

# Health
r = requests.get(f"{BASE_URL}/api/health", timeout=10)
assert r.status_code == 200
print("[PASS] Health endpoint")

# Find test image
extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

image = next(
    p for p in sorted(DATASET.rglob("*"))
    if p.is_file() and p.suffix.lower() in extensions
)

print("Test image:", image.name)

# API analysis
with open(image, "rb") as f:
    r = requests.post(
        f"{BASE_URL}/api/analyze",
        files={"image": (image.name, f, "image/jpeg")},
        timeout=180
    )

assert r.status_code == 200
data = r.json()

# Required top-level fields
required_top = [
    "success",
    "result_id",
    "input_filename",
    "pipeline",
    "p1",
    "p2",
    "p3",
    "p4",
    "artifacts",
]

for field in required_top:
    assert field in data, f"Missing field: {field}"

print("[PASS] Required top-level response fields")

# P4 fields used by frontend
p4 = data["p4"]

required_p4 = [
    "severity",
    "severity_score",
    "damage_percent",
    "region_count",
    "regions",
    "severity_method",
    "severity_validated",
]

for field in required_p4:
    assert field in p4, f"Missing P4 field: {field}"

print("[PASS] Required P4/frontend fields")

# Pipeline
assert data["pipeline"] == ["P1", "P2", "P3", "P4"]
print("[PASS] P1 -> P4 pipeline contract")

# Artifacts
assert isinstance(data["artifacts"], dict)
assert len(data["artifacts"]) >= 4
print("[PASS] Processing artifacts returned")

print("\n" + "=" * 65)
print("FRONTEND/API REGRESSION TEST: PASSED")
print("=" * 65)
