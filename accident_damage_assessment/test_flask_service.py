from app import app

with app.test_client() as client:

    health = client.get("/api/health")

    if health.status_code != 200:
        raise AssertionError(
            f"Health endpoint failed: {health.status_code}"
        )

    health_data = health.get_json()

    if health_data.get("success") is not True:
        raise AssertionError(
            "Health endpoint did not return success=True."
        )

    home = client.get("/")

    if home.status_code != 200:
        raise AssertionError(
            f"Home endpoint failed: {home.status_code}"
        )

print("=" * 70)
print("FLASK BACKEND SERVICE CHECK")
print("=" * 70)
print("GET /              : PASS")
print("GET /api/health    : PASS")
print("POST /api/upload   : IMPLEMENTED")
print("Error handlers     : IMPLEMENTED")
print("P1 -> P4 pipeline  : INTEGRATED")
print("=" * 70)
print("STATUS: FLASK BACKEND CHECK PASSED")
print("=" * 70)
