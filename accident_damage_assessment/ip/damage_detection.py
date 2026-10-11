import cv2
import numpy as np


class DamageCandidateDetector:

    def __init__(
        self,
        threshold=25,
        min_area=40,
        max_area_ratio=0.35
    ):
        self.threshold = threshold
        self.min_area = min_area
        self.max_area_ratio = max_area_ratio

    def detect(self, vehicle, vehicle_mask):

        if vehicle is None:
            raise ValueError("Vehicle image is missing.")

        if vehicle_mask is None:
            raise ValueError("Vehicle mask is missing.")

        if vehicle.ndim != 2:
            raise ValueError("Vehicle image must be grayscale.")

        if vehicle_mask.ndim != 2:
            raise ValueError("Vehicle mask must be grayscale.")

        if vehicle.dtype != np.uint8:
            raise ValueError("Vehicle image must be uint8.")

        if vehicle_mask.dtype != np.uint8:
            raise ValueError("Vehicle mask must be uint8.")

        if vehicle.shape != vehicle_mask.shape:
            raise ValueError(
                "Vehicle image and mask dimensions must match."
            )

        # Keep processing strictly inside the vehicle.
        roi = cv2.bitwise_and(
            vehicle,
            vehicle,
            mask=vehicle_mask
        )

        # Estimate local background appearance.
        smooth = cv2.GaussianBlur(
            roi,
            (21, 21),
            0
        )

        # Absolute local intensity difference.
        difference = cv2.absdiff(
            roi,
            smooth
        )

        # Ignore everything outside the vehicle.
        difference[vehicle_mask == 0] = 0

        # Candidate threshold.
        _, candidate_mask = cv2.threshold(
            difference,
            self.threshold,
            255,
            cv2.THRESH_BINARY
        )

        # Restrict again to vehicle region.
        candidate_mask = cv2.bitwise_and(
            candidate_mask,
            vehicle_mask
        )

        # Remove isolated noise and connect nearby damage pixels.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5)
        )

        candidate_mask = cv2.morphologyEx(
            candidate_mask,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1
        )

        candidate_mask = cv2.morphologyEx(
            candidate_mask,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )

        # Remove very small components.
        num_labels, labels, stats, _ = (
            cv2.connectedComponentsWithStats(
                candidate_mask,
                connectivity=8
            )
        )

        filtered = np.zeros_like(candidate_mask)

        vehicle_area = max(
            int(np.count_nonzero(vehicle_mask)),
            1
        )

        max_area = int(
            vehicle_area * self.max_area_ratio
        )

        for label in range(1, num_labels):

            area = int(
                stats[label, cv2.CC_STAT_AREA]
            )

            if self.min_area <= area <= max_area:
                filtered[labels == label] = 255

        candidate_mask = filtered

        # Extract candidate contours.
        contours, _ = cv2.findContours(
            candidate_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []

        for contour in contours:

            area = float(cv2.contourArea(contour))

            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            perimeter = float(
                cv2.arcLength(contour, True)
            )

            candidates.append({
                "contour": contour,
                "area": area,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "perimeter": perimeter
            })

        candidates.sort(
            key=lambda item: item["area"],
            reverse=True
        )

        return {
            "candidate_mask": candidate_mask,
            "difference": difference,
            "candidates": candidates
        }
