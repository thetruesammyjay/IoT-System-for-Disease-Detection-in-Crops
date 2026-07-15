"""Physical DHT22 temperature and humidity sensor adapter."""

from __future__ import annotations

import math
from collections.abc import Callable
from datetime import UTC, datetime
from threading import Lock
from time import sleep
from typing import Any

from src.domain import SensorMeasurement


class DHT22UnavailableError(RuntimeError):
    """Raised when the Raspberry Pi GPIO dependencies are unavailable."""


def _resolve_board_pin(gpio_pin: int) -> Any:
    try:
        import board
    except ImportError as exc:
        raise DHT22UnavailableError(
            "The board module is unavailable. Install the hardware extra on Raspberry Pi OS."
        ) from exc
    pin_name = f"D{gpio_pin}"
    try:
        return getattr(board, pin_name)
    except AttributeError as exc:
        raise DHT22UnavailableError(
            f"GPIO pin {gpio_pin} is not exposed as board.{pin_name}"
        ) from exc


def _create_device(pin: Any, use_pulseio: bool) -> Any:
    try:
        import adafruit_dht
    except ImportError as exc:
        raise DHT22UnavailableError(
            "adafruit-circuitpython-dht is unavailable. Run uv sync --extra hardware."
        ) from exc
    return adafruit_dht.DHT22(pin, use_pulseio=use_pulseio)


class DHT22Sensor:
    """Read a DHT22 with bounded retries for its common transient errors."""

    def __init__(
        self,
        gpio_pin: int = 4,
        use_pulseio: bool = False,
        retries: int = 3,
        retry_delay_s: float = 2.0,
        pin_resolver: Callable[[int], Any] = _resolve_board_pin,
        device_factory: Callable[[Any, bool], Any] = _create_device,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if gpio_pin < 0:
            raise ValueError("GPIO pin cannot be negative")
        if retries < 1:
            raise ValueError("DHT22 retries must be at least 1")
        if retry_delay_s < 0:
            raise ValueError("DHT22 retry delay cannot be negative")

        self.gpio_pin = gpio_pin
        self.retries = retries
        self.retry_delay_s = retry_delay_s
        self._sleeper = sleeper
        self._lock = Lock()
        self._closed = False
        pin = pin_resolver(gpio_pin)
        self._device = device_factory(pin, use_pulseio)

    def read(self) -> SensorMeasurement:
        """Return one validated reading, retrying transient DHT timing errors."""

        with self._lock:
            if self._closed:
                raise RuntimeError("DHT22 sensor is closed")
            last_error: RuntimeError | None = None
            for attempt in range(self.retries):
                try:
                    temperature = self._device.temperature
                    humidity = self._device.humidity
                    return self._measurement(temperature, humidity)
                except RuntimeError as exc:
                    last_error = exc
                    if attempt + 1 < self.retries:
                        self._sleeper(self.retry_delay_s)
            raise RuntimeError(
                f"DHT22 read failed after {self.retries} attempts: {last_error}"
            ) from last_error

    @staticmethod
    def _measurement(temperature: object, humidity: object) -> SensorMeasurement:
        if temperature is None or humidity is None:
            raise RuntimeError("DHT22 returned an incomplete reading")
        temperature_c = float(temperature)
        humidity_pct = float(humidity)
        if not math.isfinite(temperature_c) or not math.isfinite(humidity_pct):
            raise RuntimeError("DHT22 returned a non-finite reading")
        if not -40.0 <= temperature_c <= 80.0:
            raise RuntimeError("DHT22 temperature is outside its supported range")
        if not 0.0 <= humidity_pct <= 100.0:
            raise RuntimeError("DHT22 humidity is outside its supported range")
        return SensorMeasurement(
            temperature_c=round(temperature_c, 2),
            humidity_pct=round(humidity_pct, 2),
            recorded_at=datetime.now(UTC),
        )

    def close(self) -> None:
        """Release the GPIO device once."""

        with self._lock:
            if self._closed:
                return
            self._closed = True
            exit_device = getattr(self._device, "exit", None)
            if callable(exit_device):
                exit_device()

    def __enter__(self) -> DHT22Sensor:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
