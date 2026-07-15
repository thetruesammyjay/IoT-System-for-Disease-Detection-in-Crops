from __future__ import annotations

import numpy as np
import pytest

from src.inference.postprocessor import (
    ClassificationOutputError,
    ClassificationPostprocessor,
)
from src.utils.config import AppConfig


def test_postprocessor_accepts_confident_class(app_config: AppConfig) -> None:
    processor = ClassificationPostprocessor(app_config.diseases, 0.70, "test-model")

    result = processor.process(np.asarray([[0.0, 0.0, 5.0, 0.0, 0.0]]))

    assert result.label == "Late Blight"
    assert result.status == "accepted"
    assert result.severity == "high"
    assert result.confidence > 0.70
    assert sum(result.probabilities.values()) == pytest.approx(1.0)


def test_postprocessor_marks_low_confidence_as_uncertain(app_config: AppConfig) -> None:
    processor = ClassificationPostprocessor(app_config.diseases, 0.70, "test-model")

    result = processor.process(np.zeros((1, 5)))

    assert result.status == "uncertain"
    assert result.severity == "unassigned"
    assert result.confidence == pytest.approx(0.2)


def test_postprocessor_rejects_wrong_output_size(app_config: AppConfig) -> None:
    processor = ClassificationPostprocessor(app_config.diseases, 0.70, "test-model")

    with pytest.raises(ClassificationOutputError):
        processor.process(np.zeros((1, 4)))
