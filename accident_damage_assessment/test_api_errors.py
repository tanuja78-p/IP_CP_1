from io import BytesIO
from app import app

with app.test_client() as client:

    # --------------------------------------------------
    # Test 1: no image field
    # --------------------------------------------------
    response1 = client.post("/api/upload")

    if response1.status_code != 400:
        raise AssertionError(
            f"No-image test returned {response1.status_code}"
        )

    # --------------------------------------------------
    # Test 2: empty filename
    # --------------------------------------------------
    response2 = client.post(
        "/api/upload",
        data={
            "image": (
                BytesIO(b""),
                ""
            )
        },
        content_type="multipart/form-data"
    )

    if response2.status_code != 400:
        raise AssertionError(
            f"Empty-file test returned {response2.status_code}"
        )

    # --------------------------------------------------
    # Test 3: unsupported extension
    # --------------------------------------------------
    response3 = client.post(
        "/api/upload",
        data={
            "image": (
                BytesIO(b"fake content"),
                "test.txt"
            )
        },
        content_type="multipart/form-data"
    )

    if response3.status_code != 400:
        raise AssertionError(
            f"Invalid-extension test returned {response3.status_code}"
        )

    # --------------------------------------------------
    # Test 4: unknown endpoint
    # --------------------------------------------------
    response4 = client.get(
        "/api/does-not-exist"
    )

    if response4.status_code != 404:
        raise AssertionError(
            f"404 test returned {response4.status_code}"
        )

print("=" * 70)
print("BACKEND ERROR HANDLING TEST")
print("=" * 70)
print("Missing image       : PASS")
print("Empty filename      : PASS")
print("Unsupported format  : PASS")
print("Unknown endpoint    : PASS")
print("=" * 70)
print("STATUS: ERROR HANDLING PASSED")
print("=" * 70)
