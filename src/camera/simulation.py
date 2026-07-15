"""Local and generated image sources for desktop simulation."""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from PIL import Image, ImageDraw

from src.domain import CapturedImage


def load_local_image(path: str | Path) -> Image.Image:
    """Load an image fully so that no file handle remains open."""

    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Simulation image does not exist: {image_path}")
    with Image.open(image_path) as image:
        image.load()
        return image.copy()


def create_generated_leaf_image(size: tuple[int, int] = (640, 480)) -> Image.Image:
    """Create a simple synthetic input for pipeline wiring tests."""

    width, height = size
    if width < 32 or height < 32:
        raise ValueError("Generated image dimensions must each be at least 32 pixels")

    image = Image.new("RGB", size, color=(224, 218, 190))
    draw = ImageDraw.Draw(image)
    margin_x = width // 6
    margin_y = height // 5
    draw.ellipse(
        (margin_x, margin_y, width - margin_x, height - margin_y),
        fill=(61, 132, 71),
        outline=(32, 91, 48),
        width=max(1, width // 160),
    )
    draw.line(
        (width // 2, height - margin_y, width // 2, margin_y),
        fill=(218, 231, 178),
        width=max(1, width // 100),
    )
    return image


class GeneratedImageSource:
    """Produce uniquely identified synthetic images for continuous integration tests."""

    def __init__(self, size: tuple[int, int] = (640, 480)) -> None:
        self.size = size
        self._sequence = 0
        self._lock = Lock()

    def capture(self) -> CapturedImage:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
        return CapturedImage(
            image=create_generated_leaf_image(self.size),
            image_path=f"simulation://generated-leaf/{sequence}",
        )
