from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from src.inference.preprocessor import ImageQualityError, MobileNetPreprocessor


def test_preprocessor_returns_mobilenet_nchw_tensor() -> None:
    image = Image.new("RGB", (640, 480), color=(20, 120, 60))

    tensor = MobileNetPreprocessor((224, 224)).preprocess(image)

    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == np.float32
    assert tensor.flags.c_contiguous
    assert np.isfinite(tensor).all()


def test_preprocessor_rejects_tiny_images() -> None:
    image = Image.new("RGB", (16, 16))

    with pytest.raises(ImageQualityError):
        MobileNetPreprocessor().preprocess(image)
