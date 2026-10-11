from pathlib import Path

import cv2


class ImageEnhancer:
    def __init__(self, target_width=1280):
        self.target_width = target_width

    def load_image(self, source):
        image = cv2.imread(str(source))

        if image is None:
            raise ValueError("Invalid or corrupted image.")

        return image

    def resize_image(self, image):
        height, width = image.shape[:2]

        if width <= self.target_width:
            return image.copy()

        scale = self.target_width / float(width)

        new_height = int(height * scale)

        return cv2.resize(
            image,
            (self.target_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

    def grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def gaussian_filter(self, image):
        return cv2.GaussianBlur(image, (5, 5), 0)

    def median_filter(self, image):
        return cv2.medianBlur(image, 5)

    def histogram_equalization(self, image):
        return cv2.equalizeHist(image)

    def clahe(self, image):
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        return clahe.apply(image)

    def process(self, source):
        original = self.load_image(source)

        resized = self.resize_image(original)

        gray = self.grayscale(resized)

        gaussian = self.gaussian_filter(gray)

        clahe = self.clahe(gaussian)

        return {
            "original": resized,
            "gray": gray,
            "gaussian": gaussian,
            "median": self.median_filter(gray),
            "histogram_equalized": self.histogram_equalization(gaussian),
            "clahe": clahe,
        }
