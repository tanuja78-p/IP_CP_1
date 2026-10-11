from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory, render_template
from werkzeug.utils import secure_filename

from ip.pipeline import AccidentDamagePipeline


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULT_DIR = BASE_DIR / "outputs" / "api_results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE

pipeline = AccidentDamagePipeline()


def allowed_file(filename):
    if not filename:
        return False

    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def build_artifact_urls(result_id, saved_files):
    urls = {}

    for key, value in saved_files.items():
        if not value:
            continue

        filename = Path(value).name

        urls[key] = (
            f"/api/results/{result_id}/{filename}"
        )

    return urls


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "pipeline": ["P1", "P2", "P3", "P4"]
    })


@app.post("/api/upload")
@app.post("/api/analyze")
def analyze():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload an image using the 'image' field."
        }), 400

    uploaded = request.files["image"]

    if not uploaded.filename:
        return jsonify({
            "success": False,
            "error": "No filename was provided."
        }), 400

    if not allowed_file(uploaded.filename):
        return jsonify({
            "success": False,
            "error": "Unsupported image format. Use JPG, JPEG, PNG, BMP, or WEBP."
        }), 400

    original_filename = secure_filename(uploaded.filename)

    if not original_filename:
        return jsonify({
            "success": False,
            "error": "Invalid filename."
        }), 400

    result_id = uuid4().hex
    extension = Path(original_filename).suffix.lower()
    stored_filename = f"{result_id}{extension}"

    input_path = UPLOAD_DIR / stored_filename
    result_dir = RESULT_DIR / result_id
    result_dir.mkdir(parents=True, exist_ok=True)

    try:
        uploaded.save(input_path)

        if not input_path.exists() or input_path.stat().st_size == 0:
            raise ValueError("Uploaded file is empty.")

        result = pipeline.run(
            input_path,
            output_dir=result_dir
        )

        if not result.get("success", False):
            raise RuntimeError("Pipeline processing failed.")

        saved_files = result.get("saved_files", {})

        artifact_urls = build_artifact_urls(
            result_id,
            saved_files
        )

        response = {
            "success": True,
            "result_id": result_id,
            "input_filename": original_filename,
            "pipeline": result.get(
                "pipeline",
                ["P1", "P2", "P3", "P4"]
            ),
            "p1": result.get("p1", {}),
            "p2": result.get("p2", {}),
            "p3": result.get("p3", {}),
            "p4": result.get("p4", {}),
            "artifacts": artifact_urls
        }

        return jsonify(response), 200

    except ValueError as exc:
        if input_path.exists():
            input_path.unlink(missing_ok=True)

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception:
        if input_path.exists():
            input_path.unlink(missing_ok=True)

        return jsonify({
            "success": False,
            "error": "Image processing failed. Please try another image."
        }), 500


@app.get("/api/results/<result_id>/<filename>")
def result_file(result_id, filename):
    safe_result_id = Path(result_id).name
    safe_filename = Path(filename).name

    if safe_result_id != result_id or safe_filename != filename:
        return jsonify({
            "success": False,
            "error": "Invalid result path."
        }), 400

    result_dir = RESULT_DIR / safe_result_id

    if not result_dir.exists():
        return jsonify({
            "success": False,
            "error": "Result not found."
        }), 404

    requested_file = result_dir / safe_filename

    if not requested_file.exists() or not requested_file.is_file():
        return jsonify({
            "success": False,
            "error": "Result file not found."
        }), 404

    return send_from_directory(
        result_dir,
        safe_filename
    )


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "error": "Uploaded file is too large. Maximum size is 25 MB."
    }), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error."
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

