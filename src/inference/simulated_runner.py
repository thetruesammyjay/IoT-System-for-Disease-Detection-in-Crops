"""Deterministic classifier used before a trained model or AI HAT+ is available."""

from __future__ import annotations

import hashlib

import numpy as np


class SimulatedClassifier:
    """Produce repeatable five-class logits from an input tensor.

    These values are for software integration testing only and must never be
    reported as model evaluation results.
    """

    def __init__(self, class_count: int) -> None:
        if class_count < 2:
            raise ValueError("Simulation requires at least two classes")
        self.class_count = class_count

    def predict(self, tensor: np.ndarray) -> np.ndarray:
        if tensor.ndim != 4 or tensor.shape[0] != 1:
            raise ValueError("Classifier input must be a single NCHW tensor")

        digest = hashlib.sha256(tensor.tobytes()).digest()
        selected_index = digest[0] % self.class_count
        selected_logit = 2.4 + (digest[1] / 255.0)
        logits = np.full(self.class_count, -0.4, dtype=np.float32)
        logits[selected_index] = np.float32(selected_logit)
        return logits[np.newaxis, ...]
