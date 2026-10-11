import numpy as np
from backend.preprocessing.enhancement import ImageEnhancer

def test_enhancement_pipeline():
    image = np.zeros((200, 300, 3), dtype=np.uint8)
    image[50:150, 75:225] = 180
    result = ImageEnhancer(target_width=1280).enhance(image)
    assert result["original"].shape == image.shape
    assert result["gray"].shape == (200, 300)
    assert result["clahe"].shape == (200, 300)

def test_resize_large_image():
    image = np.zeros((1000, 2000, 3), dtype=np.uint8)
    result = ImageEnhancer(target_width=1280).resize_image(image)
    assert result.shape[1] == 1280
