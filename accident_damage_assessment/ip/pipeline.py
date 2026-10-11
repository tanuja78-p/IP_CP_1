from pathlib import Path
import cv2

from ip.enhancement import ImageEnhancer
from ip.segmentation import VehicleSegmenter
from ip.damage_detection import DamageCandidateDetector
from ip.p4_assessment import P4DamageAssessment


class AccidentDamagePipeline:

    def __init__(self):
        self.p1 = ImageEnhancer()
        self.p2 = VehicleSegmenter()
        self.p3 = DamageCandidateDetector()
        self.p4 = P4DamageAssessment()

    def run(self, source, output_dir=None):
        source = Path(source)

        if not source.exists():
            raise FileNotFoundError(
                f"Input image not found: {source}"
            )

        # -------------------------
        # P1
        # -------------------------
        p1_result = self.p1.process(source)

        enhanced = p1_result["clahe"]

        # -------------------------
        # P2
        # -------------------------
        vehicle_mask, vehicle = self.p2.segment(
            enhanced
        )

        # -------------------------
        # P3
        # -------------------------
        p3_result = self.p3.detect(
            vehicle,
            vehicle_mask
        )

        candidate_mask = p3_result[
            "candidate_mask"
        ]

        # -------------------------
        # P4
        # -------------------------
        p4_result = self.p4.assess(
            vehicle,
            vehicle_mask,
            candidate_mask
        )

        saved_files = {}

        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            stem = source.stem

            enhanced_path = (
                output_dir / f"{stem}_enhanced.png"
            )

            vehicle_mask_path = (
                output_dir / f"{stem}_vehicle_mask.png"
            )

            vehicle_path = (
                output_dir / f"{stem}_vehicle.png"
            )

            candidate_path = (
                output_dir / f"{stem}_candidate_mask.png"
            )

            cv2.imwrite(
                str(enhanced_path),
                enhanced
            )

            cv2.imwrite(
                str(vehicle_mask_path),
                vehicle_mask
            )

            cv2.imwrite(
                str(vehicle_path),
                vehicle
            )

            cv2.imwrite(
                str(candidate_path),
                candidate_mask
            )

            saved_files = {
                "enhanced": str(enhanced_path),
                "vehicle_mask": str(vehicle_mask_path),
                "vehicle": str(vehicle_path),
                "candidate_mask": str(candidate_path),
            }

        return {
            "success": True,
            "input_file": str(source),
            "pipeline": [
                "P1",
                "P2",
                "P3",
                "P4"
            ],
            "p1": {
                "method": "resize_grayscale_gaussian_clahe",
                "format": "PNG",
                "channels": 1,
                "dtype": "uint8",
            },
            "p2": {
                "vehicle_mask_pixels": int(
                    (vehicle_mask > 0).sum()
                ),
            },
            "p3": {
                "candidate_count": len(
                    p3_result["candidates"]
                ),
                "candidate_pixels": int(
                    (candidate_mask > 0).sum()
                ),
            },
            "p4": p4_result,
            "saved_files": saved_files,
        }
