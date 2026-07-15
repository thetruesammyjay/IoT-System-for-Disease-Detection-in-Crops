"""Repeatable DHT22-like readings for development without hardware."""

from __future__ import annotations

import random
from datetime import UTC, datetime

from src.domain import SensorMeasurement


class SimulatedDHT22:
    def __init__(
        self,
        temperature_range_c: tuple[float, float],
        humidity_range_pct: tuple[float, float],
        seed: int = 2026,
    ) -> None:
        self.temperature_range_c = temperature_range_c
        self.humidity_range_pct = humidity_range_pct
        self._random = random.Random(seed)

    def read(self) -> SensorMeasurement:
        temperature = self._random.uniform(*self.temperature_range_c)
        humidity = self._random.uniform(*self.humidity_range_pct)
        return SensorMeasurement(
            temperature_c=round(temperature, 2),
            humidity_pct=round(humidity, 2),
            recorded_at=datetime.now(UTC),
        )
