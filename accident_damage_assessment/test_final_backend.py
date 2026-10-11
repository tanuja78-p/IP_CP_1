import json
from io import BytesIO
from pathlib import Path

from app import app


def check(condition, message):
    status = "PASS" if condition else "FAIL"
    print(f"{message:<35}: {status}")
    return condition


client = app.test_client()

print("=" * 70)
print("AIM002 FINAL BACKEND HARDENING TEST")
print("=" * 70)

all_passed = True

# Health
response = client.get("/api/health")
all_passed &= check(
    response.status_code == 200,
    "Health endpoint"
)

# Missing image
response = client.post("/api/analyze")
all_passed &= check(
    response.status_code == 400,
    "Missing image"
)

# Empty filename
response = client.post(
    "/api/analyze",
    data={
        "image": (
            BytesIO(b""),
            ""
        )
    },
    content_type="multipart/form-data"
)

all_passed &= check(
    response.status_code == 400,
    "Empty filename"
)

# Unsupported extension
response = client.post(
    "/api/analyze",
    data={
        "image": (
            BytesIO(b"not an image"),
            "test.txt"
        )
    },
    content_type="multipart/form-data"
)

all_passed &= check(
    response.status_code == 400,
    "Unsupported extension"
)

# Corrupted image
response = client.post(
    "/api/analyze",
    data={
        "image": (
            BytesIO(b"this is not a real image"),
            "corrupted.jpg"
        )
    },
    content_type="multipart/form-data"
)

all_passed &= check(
    response.status_code == 400,
    "Corrupted image"
)

# Invalid result path
response = client.get(
    "/api/results/does-not-exist/file.png"
)

all_passed &= check(
    response.status_code == 404,
    "Missing result file"
)

print("=" * 70)

if all_passed:
    print("STATUS: FINAL BACKEND HARDENING PASSED")
else:
    print("STATUS: BACKEND HARDENING FAILED")

print("=" * 70)

Path("outputs/backend_integration_test").mkdir(
    parents=True,
    exist_ok=True
)

Path(
    "outputs/backend_integration_test/"
    "final_backend_hardening.json"
).write_text(
    json.dumps(
        {
            "status": "passed" if all_passed else "failed"
        },
        indent=2
    ),
    encoding="utf-8"
)

raise SystemExit(0 if all_passed else 1)
