from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.database.repository import ClassificationRepository
from src.domain import ClassificationOutcome, SensorMeasurement


@pytest.mark.integration
def test_classification_and_sensor_reading_are_persisted_together(
    repository: ClassificationRepository,
) -> None:
    now = datetime.now(UTC)
    stored = repository.save_classification(
        outcome=ClassificationOutcome(
            label="Bacterial Spot",
            confidence=0.88,
            status="accepted",
            severity="high",
            probabilities={"Bacterial Spot": 0.88, "Early Blight": 0.12},
            model_version="simulation-test",
        ),
        sensor=SensorMeasurement(temperature_c=29.5, humidity_pct=81.2, recorded_at=now),
        image_path="simulation://test-leaf",
        processing_time_ms=18.2,
        captured_at=now,
    )

    latest = repository.latest()

    assert stored.id == 1
    assert repository.count() == 1
    assert latest is not None
    assert latest.disease_label == "Bacterial Spot"
    assert latest.temperature_c == 29.5
    assert latest.humidity_pct == 81.2
