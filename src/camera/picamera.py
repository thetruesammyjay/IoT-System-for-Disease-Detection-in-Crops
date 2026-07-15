"""Physical Raspberry Pi Camera Module adapter using Picamera2."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from time import sleep
from typing import Any

from PIL import Image

from src.domain import CapturedImage


class PiCameraUnavailableError(RuntimeError):
    """Raised when Picamera2 is not available on the current system."""


def _picamera_factory() -> Any:
    try:
        from picamera2 import Picamera2
    except ImportError as exc:
        raise PiCameraUnavailableError(
            "Picamera2 is unavailable. Install python3-picamera2 on Raspberry Pi OS "
            "and create the uv environment with --system-site-packages."
        ) from exc
    return Picamera2()


class PiCameraSource:
    """Capture RGB PIL images from a Camera Module through Picamera2."""

    def __init__(
        self,
        resolution: tuple[int, int] = (1920, 1080),
        rotation: int = 0,
        warmup_seconds: float = 2.0,
        save_captures: bool = False,
        capture_dir: str | Path = "data/captures",
        camera_factory: Callable[[], Any] | None = None,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if min(resolution) <= 0:
            raise ValueError("Camera resolution values must be positive")
        if rotation not in {0, 90, 180, 270}:
            raise ValueError("Camera rotation must be 0, 90, 180, or 270")
        if warmup_seconds < 0:
            raise ValueError("Camera warmup time cannot be negative")

        self.resolution = resolution
        self.rotation = rotation
        self.warmup_seconds = warmup_seconds
        self.save_captures = save_captures
        self.capture_dir = Path(capture_dir)
        self._lock = Lock()
        self._closed = False
        self._camera = (camera_factory or _picamera_factory)()

        configuration = self._camera.create_still_configuration(
            main={"size": self.resolution, "format": "RGB888"}
        )
        self._camera.configure(configuration)
        self._camera.start()
        if self.warmup_seconds:
            sleeper(self.warmup_seconds)

    def capture(self) -> CapturedImage:
        """Capture one frame and optionally persist the original RGB image."""

        with self._lock:
            if self._closed:
                raise RuntimeError("Pi Camera source is closed")
            captured = self._camera.capture_image("main")

        if not isinstance(captured, Image.Image):
            captured = Image.fromarray(captured)
        image = captured.convert("RGB")
        if self.rotation:
            image = image.rotate(-self.rotation, expand=True)

        timestamp = datetime.now(UTC)
        identifier = timestamp.strftime("%Y%m%dT%H%M%S_%fZ")
        if self.save_captures:
            self.capture_dir.mkdir(parents=True, exist_ok=True)
            path = self.capture_dir / f"tomato_{identifier}.jpg"
            image.save(path, format="JPEG", quality=90)
            image_path = str(path.resolve())
        else:
            image_path = f"camera://picamera2/{identifier}"
        return CapturedImage(image=image, image_path=image_path)

    def close(self) -> None:
        """Stop and release the physical camera once."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._camera.stop()
            close = getattr(self._camera, "close", None)
            if callable(close):
                close()

    def __enter__(self) -> PiCameraSource:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
