from pathlib import Path

from backend.preprocessing.enhancement import ImageEnhancer
from backend.utils.image_utils import save_image


class PipelineProcessor:
    def __init__(self, output_dir="data/output"):
        self.enhancer = ImageEnhancer()
        self.output_dir = output_dir

    def process(self, image_path):
        result = self.enhancer.enhance_file(image_path)

        p2_input = result["clahe"]

        if p2_input is None or len(p2_input.shape) != 2:
            raise ValueError("P1 output for P2 must be a grayscale image.")

        if p2_input.dtype != "uint8":
            raise ValueError("P1 output for P2 must use uint8 pixel values.")

        enhanced_path = save_image(
            p2_input,
            self.output_dir,
            f"{Path(image_path).stem}_enhanced.png",
        )

        return {
            "success": True,
            "enhanced_image_path": str(enhanced_path),
            "p2_input": p2_input,
            "p2_input_path": str(enhanced_path),
        }