import io
from backend.app import create_app

def test_missing_image():
    client = create_app().test_client()
    response = client.post("/api/analyze")
    assert response.status_code == 400

def test_unsupported_file():
    client = create_app().test_client()
    response = client.post(
        "/api/analyze",
        data={"image": (io.BytesIO(b"abc"), "test.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
