import cv2
import numpy as np


class VehicleSegmenter:
    def __init__(self):
        pass

    def segment(self, image):
        """
        Segment the main vehicle region from a grayscale image.

        Input:
            image: grayscale uint8 image

        Returns:
            mask: binary vehicle mask, uint8 values {0, 255}
            vehicle: grayscale image restricted to the mask
        """

        if image is None:
            raise ValueError("Input image is None.")

        if not isinstance(image, np.ndarray):
            raise TypeError("Input image must be a NumPy array.")

        if image.ndim != 2:
            raise ValueError("P2 expects a grayscale image.")

        if image.dtype != np.uint8:
            raise ValueError("P2 expects uint8 input.")

        # Mild smoothing to reduce small background noise.
        blurred = cv2.GaussianBlur(image, (5, 5), 0)

        # Edge detection.
        edges = cv2.Canny(blurred, 50, 150)

        # Close gaps in vehicle boundaries.
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (7, 7)
        )

        closed = cv2.morphologyEx(
            edges,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )

        # Dilate slightly so fragmented vehicle boundaries connect.
        dilated = cv2.dilate(
            closed,
            kernel,
            iterations=1
        )

        # Find connected components.
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            dilated,
            connectivity=8
        )

        mask = np.zeros_like(image, dtype=np.uint8)

        if num_labels > 1:
            # Ignore background label 0.
            areas = stats[1:, cv2.CC_STAT_AREA]
            largest_label = 1 + int(np.argmax(areas))

            mask[labels == largest_label] = 255

        # Fill holes inside the selected region.
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)

            filled = np.zeros_like(mask)
            cv2.drawContours(
                filled,
                [largest_contour],
                -1,
                255,
                thickness=cv2.FILLED
            )
            mask = filled

        # Apply mask to obtain vehicle-only image.
        vehicle = cv2.bitwise_and(
            image,
            image,
            mask=mask
        )

        return mask, vehicle
