from __future__ import annotations

from datetime import UTC, datetime
from threading import Event, Thread

import pytest

from src.camera.simulation import GeneratedImageSource
from src.domain import StoredClassification
from src.monitoring import ContinuousMonitoringService, MonitoringBusyError


def _result(record_id: int = 1) -> StoredClassification:
    return StoredClassification(
        id=record_id,
        image_path="simulation://test",
        disease_label="Late Blight",
        confidence=0.9,
        prediction_status="accepted",
        severity="high",
        model_version="test-v1",
        processing_time_ms=10.0,
        captured_at=datetime.now(UTC),
        temperature_c=27.0,
        humidity_pct=70.0,
        probabilities={"Late Blight": 0.9},
    )


class _Pipeline:
    def __init__(self) -> None:
        self.calls = 0
        self.called = Event()

    def run(self, image, image_path: str) -> StoredClassification:
        self.calls += 1
        self.called.set()
        return _result(self.calls)


class _BlockingPipeline:
    def __init__(self) -> None:
        self.entered = Event()
        self.release = Event()

    def run(self, image, image_path: str) -> StoredClassification:
        self.entered.set()
        assert self.release.wait(2.0)
        return _result()


def test_monitoring_run_once_updates_status() -> None:
    service = ContinuousMonitoringService(
        _Pipeline(), GeneratedImageSource((64, 64)), capture_interval_s=1.0
    )

    result = service.run_once()
    status = service.status()

    assert result.id == 1
    assert status.cycles_completed == 1
    assert status.cycles_failed == 0
    assert status.last_result_id == 1
    assert status.cycle_active is False


def test_monitoring_start_and_stop_are_idempotent() -> None:
    pipeline = _Pipeline()
    service = ContinuousMonitoringService(
        pipeline, GeneratedImageSource((64, 64)), capture_interval_s=0.05
    )

    assert service.start() is True
    assert service.start() is False
    assert pipeline.called.wait(2.0)
    assert service.stop() is True
    assert service.stop() is False
    assert service.status().running is False


def test_monitoring_rejects_overlapping_cycles() -> None:
    pipeline = _BlockingPipeline()
    service = ContinuousMonitoringService(
        pipeline, GeneratedImageSource((64, 64)), capture_interval_s=1.0
    )
    worker = Thread(target=service.run_once)
    worker.start()
    assert pipeline.entered.wait(2.0)

    with pytest.raises(MonitoringBusyError):
        service.run_once()

    pipeline.release.set()
    worker.join(2.0)
    assert not worker.is_alive()
    assert service.status().cycles_skipped == 1
