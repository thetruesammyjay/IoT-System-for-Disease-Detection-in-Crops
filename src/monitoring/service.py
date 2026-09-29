"""Thread-safe scheduling for repeated image classification cycles."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Event, Lock, Thread
from time import monotonic
from typing import Protocol

from PIL import Image

from src.domain import CapturedImage, StoredClassification

LOGGER = logging.getLogger("tomato_iot.monitoring")


class ImageSource(Protocol):
    def capture(self) -> CapturedImage: ...


class Pipeline(Protocol):
    def run(self, image, image_path: str) -> StoredClassification: ...


class MonitoringBusyError(RuntimeError):
    """Raised when another classification cycle is already active."""


@dataclass(frozen=True, slots=True)
class MonitoringStatus:
    running: bool
    cycle_active: bool
    capture_interval_s: float
    cycles_completed: int
    cycles_failed: int
    cycles_skipped: int
    last_started_at: datetime | None
    last_completed_at: datetime | None
    last_result_id: int | None
    last_error: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "cycle_active": self.cycle_active,
            "capture_interval_s": self.capture_interval_s,
            "cycles_completed": self.cycles_completed,
            "cycles_failed": self.cycles_failed,
            "cycles_skipped": self.cycles_skipped,
            "last_started_at": (self.last_started_at.isoformat() if self.last_started_at else None),
            "last_completed_at": (
                self.last_completed_at.isoformat() if self.last_completed_at else None
            ),
            "last_result_id": self.last_result_id,
            "last_error": self.last_error,
        }


class ContinuousMonitoringService:
    """Run one pipeline at a fixed interval without overlapping cycles."""

    def __init__(
        self,
        pipeline: Pipeline,
        image_source: ImageSource,
        capture_interval_s: float,
        stop_timeout_s: float = 5.0,
    ) -> None:
        if capture_interval_s <= 0:
            raise ValueError("capture_interval_s must be greater than zero")
        if stop_timeout_s <= 0:
            raise ValueError("stop_timeout_s must be greater than zero")
        self.pipeline = pipeline
        self.image_source = image_source
        self.capture_interval_s = float(capture_interval_s)
        self.stop_timeout_s = float(stop_timeout_s)
        self._stop_event = Event()
        self._cycle_lock = Lock()
        self._state_lock = Lock()
        self._thread: Thread | None = None
        self._running = False
        self._cycle_active = False
        self._cycles_completed = 0
        self._cycles_failed = 0
        self._cycles_skipped = 0
        self._last_started_at: datetime | None = None
        self._last_completed_at: datetime | None = None
        self._last_result_id: int | None = None
        self._last_error: str | None = None

    def start(self) -> bool:
        """Start the background loop; return False if it is already running."""

        with self._state_lock:
            if self._running:
                return False
            self._stop_event.clear()
            self._running = True
            self._thread = Thread(
                target=self._run_loop,
                name="tomato-monitoring",
                daemon=True,
            )
            self._thread.start()
            return True

    def stop(self) -> bool:
        """Stop the loop and wait for the active cycle to finish."""

        with self._state_lock:
            if not self._running:
                return False
            thread = self._thread
            self._stop_event.set()
        if thread is not None:
            thread.join(self.stop_timeout_s)
            if thread.is_alive():
                raise TimeoutError("Monitoring service did not stop within the configured timeout")
        return True

    def run_once(self) -> StoredClassification:
        """Capture and classify one image, rejecting concurrent execution."""

        return self._run_cycle(self.image_source.capture)

    def classify_image(self, image: Image.Image, image_path: str) -> StoredClassification:
        """Classify a supplied image through the shared, non-overlapping pipeline."""

        captured = CapturedImage(image=image, image_path=image_path)
        return self._run_cycle(lambda: captured)

    def _run_cycle(self, capture: Callable[[], CapturedImage]) -> StoredClassification:
        """Execute one captured or supplied image as a monitored classification cycle."""

        if not self._cycle_lock.acquire(blocking=False):
            with self._state_lock:
                self._cycles_skipped += 1
            raise MonitoringBusyError("A classification cycle is already running")

        with self._state_lock:
            self._cycle_active = True
            self._last_started_at = datetime.now(UTC)
            self._last_error = None
        try:
            captured = capture()
            result = self.pipeline.run(captured.image, captured.image_path)
        except Exception as exc:
            with self._state_lock:
                self._cycles_failed += 1
                self._last_error = f"{type(exc).__name__}: {exc}"
            raise
        else:
            with self._state_lock:
                self._cycles_completed += 1
                self._last_result_id = result.id
                self._last_completed_at = datetime.now(UTC)
            return result
        finally:
            with self._state_lock:
                self._cycle_active = False
            self._cycle_lock.release()

    def status(self) -> MonitoringStatus:
        with self._state_lock:
            return MonitoringStatus(
                running=self._running,
                cycle_active=self._cycle_active,
                capture_interval_s=self.capture_interval_s,
                cycles_completed=self._cycles_completed,
                cycles_failed=self._cycles_failed,
                cycles_skipped=self._cycles_skipped,
                last_started_at=self._last_started_at,
                last_completed_at=self._last_completed_at,
                last_result_id=self._last_result_id,
                last_error=self._last_error,
            )

    def close(self) -> None:
        """Stop monitoring and release the camera and pipeline resources."""

        if self.status().running:
            self.stop()
        for resource in (self.image_source, self.pipeline):
            close = getattr(resource, "close", None)
            if callable(close):
                close()

    def _run_loop(self) -> None:
        try:
            while not self._stop_event.is_set():
                cycle_started = monotonic()
                try:
                    self.run_once()
                except MonitoringBusyError:
                    LOGGER.warning("Skipped a monitoring cycle because inference is busy")
                except Exception:
                    LOGGER.exception("Continuous monitoring cycle failed")
                elapsed = monotonic() - cycle_started
                wait_time = max(0.0, self.capture_interval_s - elapsed)
                self._stop_event.wait(wait_time)
        finally:
            with self._state_lock:
                self._running = False
                self._thread = None
