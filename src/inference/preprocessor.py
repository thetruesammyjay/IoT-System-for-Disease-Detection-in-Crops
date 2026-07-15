"""MobileNetV2-compatible image preprocessing."""

from __future__ import annotations

import numpy as np
from PIL import Image

from src.inference.model_metadata import IMAGENET_MEAN, IMAGENET_STD

IMAGENET_MEAN_ARRAY = np.asarray(IMAGENET_MEAN, dtype=np.float32)
IMAGENET_STD_ARRAY = np.asarray(IMAGENET_STD, dtype=np.float32)


class ImageQualityError(ValueError):
    """Raised when an image cannot be safely classified."""


class MobileNetPreprocessor:
    """Convert a PIL image to a normalized NCHW float32 tensor."""

    def __init__(self, input_size: tuple[int, int] = (224, 224)) -> None:
        self.input_size = input_size

    def preprocess(self, image: Image.Image) -> np.ndarray:
        if image.width < 32 or image.height < 32:
            raise ImageQualityError("Image width and height must each be at least 32 pixels")

        rgb_image = image.convert("RGB")
        resized = rgb_image.resize(self.input_size, Image.Resampling.BILINEAR)
        pixels = np.asarray(resized, dtype=np.float32) / np.float32(255.0)
        normalized = (pixels - IMAGENET_MEAN_ARRAY) / IMAGENET_STD_ARRAY
        tensor = np.transpose(normalized, (2, 0, 1))[np.newaxis, ...]
        return np.ascontiguousarray(tensor, dtype=np.float32)
