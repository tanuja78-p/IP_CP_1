import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern


class P4DamageAssessment:
    """
    P4 feature extraction and provisional severity assessment.

    IMPORTANT:
    The current dataset does not contain verified
    minor/moderate/severe ground-truth labels.
    Therefore severity here is a transparent heuristic,
    not a trained/validated medical-style classifier.
    """

    def __init__(self):
        pass

    def _validate(self, vehicle, vehicle_mask, candidate_mask):
        if vehicle is None:
            raise ValueError("Vehicle image is missing.")

        if vehicle_mask is None:
            raise ValueError("Vehicle mask is missing.")

        if candidate_mask is None:
            raise ValueError("Candidate mask is missing.")

        if vehicle.ndim != 2:
            raise ValueError("Vehicle image must be grayscale.")

        if vehicle_mask.ndim != 2:
            raise ValueError("Vehicle mask must be grayscale.")

        if candidate_mask.ndim != 2:
            raise ValueError("Candidate mask must be grayscale.")

        if vehicle.dtype != np.uint8:
            raise ValueError("Vehicle image must be uint8.")

        if vehicle_mask.dtype != np.uint8:
            raise ValueError("Vehicle mask must be uint8.")

        if candidate_mask.dtype != np.uint8:
            raise ValueError("Candidate mask must be uint8.")

        if vehicle.shape != vehicle_mask.shape:
            raise ValueError("Vehicle and vehicle mask dimensions differ.")

        if vehicle.shape != candidate_mask.shape:
            raise ValueError("Vehicle and candidate mask dimensions differ.")

    def _texture_features(self, crop):
        if crop is None or crop.size == 0:
            return {
                "glcm_contrast": 0.0,
                "glcm_correlation": 0.0,
                "glcm_energy": 0.0,
                "glcm_homogeneity": 0.0,
                "lbp_mean": 0.0,
                "lbp_std": 0.0,
            }

        crop = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)

        normalized = cv2.normalize(
            crop,
            None,
            0,
            63,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        glcm = graycomatrix(
            normalized,
            distances=[1],
            angles=[0],
            levels=64,
            symmetric=True,
            normed=True
        )

        contrast = float(graycoprops(glcm, "contrast")[0, 0])
        correlation = float(graycoprops(glcm, "correlation")[0, 0])
        energy = float(graycoprops(glcm, "energy")[0, 0])
        homogeneity = float(graycoprops(glcm, "homogeneity")[0, 0])

        lbp = local_binary_pattern(
            normalized,
            P=8,
            R=1,
            method="uniform"
        )

        return {
            "glcm_contrast": contrast,
            "glcm_correlation": correlation,
            "glcm_energy": energy,
            "glcm_homogeneity": homogeneity,
            "lbp_mean": float(np.mean(lbp)),
            "lbp_std": float(np.std(lbp)),
        }

    def _geometric_features(self, contour):
        area = float(cv2.contourArea(contour))
        perimeter = float(cv2.arcLength(contour, True))

        x, y, width, height = cv2.boundingRect(contour)

        aspect_ratio = (
            float(width) / float(height)
            if height > 0 else 0.0
        )

        hull = cv2.convexHull(contour)
        hull_area = float(cv2.contourArea(hull))

        solidity = (
            area / hull_area
            if hull_area > 0 else 0.0
        )

        circularity = (
            (4.0 * np.pi * area) / (perimeter * perimeter)
            if perimeter > 0 else 0.0
        )

        moments = cv2.moments(contour)

        if moments["m00"] != 0:
            centroid_x = moments["m10"] / moments["m00"]
            centroid_y = moments["m01"] / moments["m00"]
        else:
            centroid_x = x + width / 2.0
            centroid_y = y + height / 2.0

        return {
            "area": area,
            "perimeter": perimeter,
            "x": int(x),
            "y": int(y),
            "width": int(width),
            "height": int(height),
            "aspect_ratio": aspect_ratio,
            "solidity": solidity,
            "circularity": circularity,
            "centroid_x": float(centroid_x),
            "centroid_y": float(centroid_y),
        }

    def _region_indicator(self, geometry, texture):
        area_score = min(
            geometry["area"] / 5000.0,
            1.0
        )

        irregularity = 1.0 - min(
            max(geometry["solidity"], 0.0),
            1.0
        )

        non_circular = 1.0 - min(
            max(geometry["circularity"], 0.0),
            1.0
        )

        contrast_score = min(
            texture["glcm_contrast"] / 50.0,
            1.0
        )

        texture_variation = min(
            texture["lbp_std"] / 3.5,
            1.0
        )

        score = (
            0.25 * area_score +
            0.20 * irregularity +
            0.15 * non_circular +
            0.25 * contrast_score +
            0.15 * texture_variation
        )

        return float(np.clip(score, 0.0, 1.0))

    def _severity(self, damage_percent, mean_indicator, max_indicator):
        combined = (
            0.50 * min(damage_percent / 25.0, 1.0) +
            0.30 * mean_indicator +
            0.20 * max_indicator
        )

        if combined < 0.20:
            label = "Low"
        elif combined < 0.50:
            label = "Moderate"
        else:
            label = "High"

        return label, float(combined)

    def assess(self, vehicle, vehicle_mask, candidate_mask):
        self._validate(
            vehicle,
            vehicle_mask,
            candidate_mask
        )

        vehicle_area = int(np.count_nonzero(vehicle_mask))
        damage_area = int(
            np.count_nonzero(
                cv2.bitwise_and(
                    candidate_mask,
                    vehicle_mask
                )
            )
        )

        if vehicle_area > 0:
            damage_percent = (
                damage_area / vehicle_area
            ) * 100.0
        else:
            damage_percent = 0.0

        contours, _ = cv2.findContours(
            candidate_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        regions = []

        for region_id, contour in enumerate(
            contours,
            start=1
        ):
            if cv2.contourArea(contour) <= 0:
                continue

            geometry = self._geometric_features(contour)

            x = geometry["x"]
            y = geometry["y"]
            width = geometry["width"]
            height = geometry["height"]

            crop = vehicle[
                y:y + height,
                x:x + width
            ]

            texture = self._texture_features(crop)

            indicator = self._region_indicator(
                geometry,
                texture
            )

            regions.append({
                "region_id": region_id,
                **geometry,
                **texture,
                "damage_indicator": indicator,
            })

        if regions:
            indicators = [
                r["damage_indicator"]
                for r in regions
            ]

            mean_indicator = float(np.mean(indicators))
            max_indicator = float(np.max(indicators))
        else:
            mean_indicator = 0.0
            max_indicator = 0.0

        severity, severity_score = self._severity(
            damage_percent,
            mean_indicator,
            max_indicator
        )

        return {
            "severity": severity,
            "severity_score": severity_score,
            "damage_percent": float(damage_percent),
            "vehicle_area": vehicle_area,
            "damage_area": damage_area,
            "region_count": len(regions),
            "regions": regions,
            "severity_method": "provisional_feature_based_rule",
            "severity_validated": False,
        }
