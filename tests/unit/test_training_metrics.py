from __future__ import annotations

import pytest

pytest.importorskip("sklearn")

from models.training.metrics import calculate_metrics


@pytest.mark.training
def test_classification_metrics_and_confusion_matrix() -> None:
    class_names = ["A", "B", "C"]
    actual = [0, 0, 1, 1, 2, 2]
    predicted = [0, 1, 1, 1, 2, 0]

    metrics, matrix = calculate_metrics(actual, predicted, class_names)

    assert metrics["accuracy"] == pytest.approx(4 / 6)
    assert metrics["test_samples"] == 6
    assert metrics["per_class"]["A"]["support"] == 2
    assert matrix.tolist() == [[1, 1, 0], [0, 2, 0], [1, 0, 1]]
