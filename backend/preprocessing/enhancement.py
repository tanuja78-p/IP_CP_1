from pathlib import Path
import cv2
import numpy as np

class ImageEnhancer:
    def __init__(self, target_width=1280):
        self.target_width = target_width

    def load_image(self, source):
        image = cv2.imread(str(source))
        if image is None:
            raise ValueError("Invalid or corrupted image.")
        return image

    def resize_image(self, image):
        h, w = image.shape[:2]
        if w <= self.target_width:
            return image.copy()
        scale = self.target_width / float(w)
        return cv2.resize(image, (self.target_width, int(h * scale)), interpolation=cv2.INTER_AREA)

    def convert_to_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def convert_to_hsv(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    def gaussian_filter(self, image, kernel_size=5):
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    def median_filter(self, image, kernel_size=5):
        return cv2.medianBlur(image, kernel_size)

    def histogram_equalization(self, gray_image):
        return cv2.equalizeHist(gray_image)

    def clahe_enhancement(self, gray_image, clip_limit=2.0, tile_grid_size=(8, 8)):
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(gray_image)

    def enhance(self, image):
        resized = self.resize_image(image)
        gray = self.convert_to_grayscale(resized)
        denoised = self.gaussian_filter(gray)
        equalized = self.histogram_equalization(denoised)
        clahe = self.clahe_enhancement(denoised)
        return {
            "original": resized,
            "gray": gray,
            "denoised": denoised,
            "equalized": equalized,
            "clahe": clahe,
            "hsv": self.convert_to_hsv(resized),
        }

    def enhance_file(self, source):
        return self.enhance(self.load_image(source))
