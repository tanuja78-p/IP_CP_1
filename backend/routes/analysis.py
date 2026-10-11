from pathlib import Path

from flask import Blueprint, jsonify, request

from backend.pipeline.processor import PipelineProcessor
from backend.utils.image_utils import allowed_file


analysis_bp = Blueprint("analysis", __name__)
processor = PipelineProcessor()


@analysis_bp.post("/analyze")
def analyze():
    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image file supplied."
        }), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({
            "success": False,
            "message": "Empty filename."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": "Unsupported image format."
        }), 400

    safe_name = Path(file.filename).name
    temp_path = Path("data/input") / safe_name
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file.save(temp_path)

        result = processor.process(temp_path)

        return jsonify({
    "success": True,
    "message": "Image processed successfully",
    "enhanced_image_path": result["enhanced_image_path"],
    "p2_input_path": result["p2_input_path"],
})

    except (ValueError, IOError) as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400

    finally:
        # Keep the uploaded image in data/input for now.
        pass