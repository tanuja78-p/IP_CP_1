import cv2
import numpy as np
import pytest

from backend.preprocessing.enhancement import ImageEnhancer


@pytest.fixture
def enhancer():
    return ImageEnhancer(target_width=1280)


def check_output(result):
    output = result["clahe"]

    assert output is not None
    assert len(output.shape) == 2
    assert output.dtype == np.uint8
    assert output.shape[0] > 0
    assert output.shape[1] > 0


def test_bright_image(enhancer):
    image = np.full((400, 600, 3), 245, dtype=np.uint8)

    result = enhancer.enhance(image)

    check_output(result)


def test_dark_image(enhancer):
    image = np.full((400, 600, 3), 20, dtype=np.uint8)

    result = enhancer.enhance(image)

    check_output(result)


def test_low_contrast_image(enhancer):
    image = np.full((400, 600, 3), 120, dtype=np.uint8)

    image[150:250, 200:400] = 125

    result = enhancer.enhance(image)

    check_output(result)


def test_noisy_image(enhancer):
    rng = np.random.default_rng(42)

    image = rng.integers(
        0,
        256,
        size=(400, 600, 3),
        dtype=np.uint8,
    )

    result = enhancer.enhance(image)

    check_output(result)


def test_small_image(enhancer):
    image = np.zeros((50, 80, 3), dtype=np.uint8)

    result = enhancer.enhance(image)

    check_output(result)


def test_large_image(enhancer):
    image = np.zeros((2000, 3000, 3), dtype=np.uint8)

    result = enhancer.enhance(image)

    check_output(result)

    assert result["original"].shape[1] == 1280


def test_invalid_file(enhancer, tmp_path):
    invalid_file = tmp_path / "invalid.jpg"

    invalid_file.write_text("This is not an image.")

    with pytest.raises(ValueError):
        enhancer.enhance_file(invalid_file)


def test_color_image(enhancer):
    image = np.zeros((300, 500, 3), dtype=np.uint8)

    image[:, :, 0] = 255
    image[:, :, 1] = 100
    image[:, :, 2] = 50

    result = enhancer.enhance(image)

    check_output(result)