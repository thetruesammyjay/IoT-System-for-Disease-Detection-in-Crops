from __future__ import annotations

from PIL import Image

from src.camera.picamera import PiCameraSource
from src.camera.simulation import create_generated_leaf_image, load_local_image


def test_generated_leaf_image_uses_requested_size() -> None:
    image = create_generated_leaf_image((320, 240))

    assert image.mode == "RGB"
    assert image.size == (320, 240)


def test_local_image_is_loaded_without_open_file_handle(tmp_path) -> None:
    image_path = tmp_path / "leaf.png"
    Image.new("RGB", (64, 64), color="green").save(image_path)

    loaded = load_local_image(image_path)
    image_path.unlink()

    assert loaded.size == (64, 64)
    assert loaded.getpixel((0, 0)) == (0, 128, 0)


class FakePiCamera:
    def __init__(self) -> None:
        self.configuration = None
        self.started = False
        self.stopped = False
        self.closed = False

    def create_still_configuration(self, **configuration):
        return configuration

    def configure(self, configuration) -> None:
        self.configuration = configuration

    def start(self) -> None:
        self.started = True

    def capture_image(self, stream: str) -> Image.Image:
        assert stream == "main"
        return Image.new("RGB", (80, 40), color="green")

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


def test_pi_camera_adapter_configures_captures_rotates_and_closes() -> None:
    camera = FakePiCamera()
    warmups: list[float] = []
    source = PiCameraSource(
        resolution=(800, 600),
        rotation=90,
        warmup_seconds=0.25,
        camera_factory=lambda: camera,
        sleeper=warmups.append,
    )

    captured = source.capture()
    source.close()
    source.close()

    assert camera.configuration == {"main": {"size": (800, 600), "format": "RGB888"}}
    assert camera.started is True
    assert captured.image.mode == "RGB"
    assert captured.image.size == (40, 80)
    assert captured.image_path.startswith("camera://picamera2/")
    assert warmups == [0.25]
    assert camera.stopped is True
    assert camera.closed is True
