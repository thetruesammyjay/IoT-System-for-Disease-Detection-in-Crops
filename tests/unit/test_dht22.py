from __future__ import annotations

import pytest

from src.sensors.dht22 import DHT22Sensor
from src.sensors.simulated import SimulatedDHT22


def test_simulated_sensor_is_repeatable_and_within_range() -> None:
    first_sensor = SimulatedDHT22((20.0, 35.0), (45.0, 90.0), seed=10)
    second_sensor = SimulatedDHT22((20.0, 35.0), (45.0, 90.0), seed=10)

    first = first_sensor.read()
    second = second_sensor.read()

    assert first.temperature_c == second.temperature_c
    assert first.humidity_pct == second.humidity_pct
    assert 20.0 <= first.temperature_c <= 35.0
    assert 45.0 <= first.humidity_pct <= 90.0


class FakeDHT22Device:
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.exited = False

    @property
    def temperature(self) -> float:
        if self.failures:
            self.failures -= 1
            raise RuntimeError("checksum mismatch")
        return 27.345

    @property
    def humidity(self) -> float:
        return 71.256

    def exit(self) -> None:
        self.exited = True


def test_dht22_adapter_retries_transient_errors_and_releases_gpio() -> None:
    device = FakeDHT22Device(failures=1)
    delays: list[float] = []
    factory_arguments: list[tuple[object, bool]] = []

    def factory(pin: object, use_pulseio: bool) -> FakeDHT22Device:
        factory_arguments.append((pin, use_pulseio))
        return device

    sensor = DHT22Sensor(
        gpio_pin=4,
        use_pulseio=False,
        retries=3,
        retry_delay_s=2.0,
        pin_resolver=lambda pin: f"D{pin}",
        device_factory=factory,
        sleeper=delays.append,
    )

    reading = sensor.read()
    sensor.close()
    sensor.close()

    assert reading.temperature_c == 27.34
    assert reading.humidity_pct == 71.26
    assert factory_arguments == [("D4", False)]
    assert delays == [2.0]
    assert device.exited is True


def test_dht22_adapter_reports_exhausted_retries() -> None:
    device = FakeDHT22Device(failures=3)
    sensor = DHT22Sensor(
        retries=2,
        retry_delay_s=0,
        pin_resolver=lambda pin: pin,
        device_factory=lambda _pin, _pulseio: device,
        sleeper=lambda _delay: None,
    )

    with pytest.raises(RuntimeError, match="after 2 attempts"):
        sensor.read()
