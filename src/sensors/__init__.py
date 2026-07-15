"""Environmental sensor adapters."""

from src.sensors.dht22 import DHT22Sensor, DHT22UnavailableError

__all__ = ["DHT22Sensor", "DHT22UnavailableError"]
