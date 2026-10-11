from pathlib import Path
from werkzeug.utils import secure_filename
import cv2

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image, output_dir, filename):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / secure_filename(filename)
    if not cv2.imwrite(str(path), image):
        raise IOError("Could not save processed image.")
    return path
