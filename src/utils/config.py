"""Validated YAML configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.domain import DiseaseClass


class ConfigurationError(ValueError):
    """Raised when project configuration is missing or inconsistent."""


@dataclass(frozen=True, slots=True)
class InferenceConfig:
    backend: str
    onnx_model_path: Path
    hailo_model_path: Path
    confidence_threshold: float
    input_size: tuple[int, int]
    class_count: int
    model_version: str


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    path: Path


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    seed: int
    temperature_range_c: tuple[float, float]
    humidity_range_pct: tuple[float, float]
    generated_image_size: tuple[int, int]


@dataclass(frozen=True, slots=True)
class CameraConfig:
    resolution: tuple[int, int]
    rotation: int
    warmup_seconds: float
    save_captures: bool
    capture_dir: Path


@dataclass(frozen=True, slots=True)
class SensorConfig:
    backend: str
    gpio_pin: int
    use_pulseio: bool
    retries: int
    retry_delay_s: float


@dataclass(frozen=True, slots=True)
class ApiConfig:
    host: str
    port: int
    debug: bool


@dataclass(frozen=True, slots=True)
class MonitoringConfig:
    enabled: bool
    source: str
    capture_interval_s: float
    auto_start: bool
    stop_timeout_s: float


@dataclass(frozen=True, slots=True)
class AppConfig:
    project_root: Path
    inference: InferenceConfig
    database: DatabaseConfig
    simulation: SimulationConfig
    camera: CameraConfig
    sensor: SensorConfig
    api: ApiConfig
    monitoring: MonitoringConfig
    diseases: tuple[DiseaseClass, ...]


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{name} must be a YAML mapping")
    return value


def _pair(value: Any, name: str, converter: type[int] | type[float]) -> tuple[Any, Any]:
    if not isinstance(value, list) or len(value) != 2:
        raise ConfigurationError(f"{name} must contain exactly two values")
    return converter(value[0]), converter(value[1])


def _resolve(project_root: Path, value: Any, name: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{name} must be a non-empty path")
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {path}")
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {path}: {exc}") from exc
    return _mapping(parsed, str(path))


def _load_diseases(path: Path, expected_count: int) -> tuple[DiseaseClass, ...]:
    data = _load_yaml(path)
    raw_classes = data.get("classes")
    if not isinstance(raw_classes, list):
        raise ConfigurationError("diseases.yaml must define a classes list")

    diseases: list[DiseaseClass] = []
    for raw in raw_classes:
        item = _mapping(raw, "disease class")
        try:
            diseases.append(
                DiseaseClass(
                    index=int(item["index"]),
                    label=str(item["label"]),
                    dataset_label=str(item["dataset_label"]),
                    severity=str(item["severity"]),
                )
            )
        except KeyError as exc:
            raise ConfigurationError(f"Disease class is missing {exc.args[0]}") from exc

    diseases.sort(key=lambda disease: disease.index)
    if len(diseases) != expected_count:
        raise ConfigurationError(
            f"Expected {expected_count} disease classes but found {len(diseases)}"
        )
    if [disease.index for disease in diseases] != list(range(expected_count)):
        raise ConfigurationError("Disease indices must be contiguous and start at zero")
    if len({disease.label for disease in diseases}) != expected_count:
        raise ConfigurationError("Disease labels must be unique")
    return tuple(diseases)


def load_config(path: str | Path = "config/config.yaml") -> AppConfig:
    """Load and validate application and disease configuration."""

    config_path = Path(path).resolve()
    project_root = config_path.parent.parent
    data = _load_yaml(config_path)

    inference_data = _mapping(data.get("inference"), "inference")
    class_count = int(inference_data.get("class_count", 5))
    threshold = float(inference_data.get("confidence_threshold", 0.70))
    backend = str(inference_data.get("backend", "simulation")).lower()
    if backend not in {"simulation", "onnx", "hailo"}:
        raise ConfigurationError("inference.backend must be simulation, onnx, or hailo")
    if not 0.0 < threshold <= 1.0:
        raise ConfigurationError("confidence_threshold must be greater than 0 and at most 1")

    input_size = _pair(inference_data.get("input_size", [224, 224]), "input_size", int)
    if min(input_size) <= 0:
        raise ConfigurationError("input_size values must be positive")

    database_data = _mapping(data.get("database"), "database")
    simulation_data = _mapping(data.get("simulation"), "simulation")
    camera_data = _mapping(data.get("camera", {}), "camera")
    sensor_data = _mapping(data.get("sensor", {}), "sensor")
    api_data = _mapping(data.get("api"), "api")
    monitoring_data = _mapping(data.get("monitoring", {}), "monitoring")

    temperature_range = _pair(
        simulation_data.get("temperature_range_c", [20.0, 35.0]),
        "temperature_range_c",
        float,
    )
    humidity_range = _pair(
        simulation_data.get("humidity_range_pct", [45.0, 90.0]),
        "humidity_range_pct",
        float,
    )
    generated_size = _pair(
        simulation_data.get("generated_image_size", [640, 480]),
        "generated_image_size",
        int,
    )
    if temperature_range[0] > temperature_range[1]:
        raise ConfigurationError("temperature_range_c minimum cannot exceed maximum")
    if humidity_range[0] > humidity_range[1]:
        raise ConfigurationError("humidity_range_pct minimum cannot exceed maximum")
    camera_resolution = _pair(
        camera_data.get("resolution", [1920, 1080]),
        "camera.resolution",
        int,
    )
    if min(camera_resolution) <= 0:
        raise ConfigurationError("camera.resolution values must be positive")
    camera_rotation = int(camera_data.get("rotation", 0))
    if camera_rotation not in {0, 90, 180, 270}:
        raise ConfigurationError("camera.rotation must be 0, 90, 180, or 270")
    camera_warmup_seconds = float(camera_data.get("warmup_seconds", 2.0))
    if camera_warmup_seconds < 0:
        raise ConfigurationError("camera.warmup_seconds cannot be negative")

    sensor_backend = str(sensor_data.get("backend", "simulation")).lower()
    if sensor_backend not in {"simulation", "dht22"}:
        raise ConfigurationError("sensor.backend must be simulation or dht22")
    sensor_gpio_pin = int(sensor_data.get("gpio_pin", 4))
    sensor_retries = int(sensor_data.get("retries", 3))
    sensor_retry_delay_s = float(sensor_data.get("retry_delay_s", 2.0))
    if sensor_gpio_pin < 0:
        raise ConfigurationError("sensor.gpio_pin cannot be negative")
    if sensor_retries < 1:
        raise ConfigurationError("sensor.retries must be at least 1")
    if sensor_retry_delay_s < 0:
        raise ConfigurationError("sensor.retry_delay_s cannot be negative")

    monitoring_source = str(monitoring_data.get("source", "simulation")).lower()
    if monitoring_source not in {"simulation", "picamera2"}:
        raise ConfigurationError("monitoring.source must be simulation or picamera2")
    capture_interval_s = float(monitoring_data.get("capture_interval_s", 5.0))
    stop_timeout_s = float(monitoring_data.get("stop_timeout_s", 5.0))
    if capture_interval_s <= 0 or stop_timeout_s <= 0:
        raise ConfigurationError("Monitoring intervals and timeouts must be greater than zero")

    disease_path = _resolve(
        project_root,
        data.get("diseases_path", "config/diseases.yaml"),
        "diseases_path",
    )

    return AppConfig(
        project_root=project_root,
        inference=InferenceConfig(
            backend=backend,
            onnx_model_path=_resolve(
                project_root,
                inference_data.get("onnx_model_path", "models/onnx/tomato_mobilenet_v2.onnx"),
                "onnx_model_path",
            ),
            hailo_model_path=_resolve(
                project_root,
                inference_data.get("hailo_model_path", "models/hailo/tomato_classifier.hef"),
                "hailo_model_path",
            ),
            confidence_threshold=threshold,
            input_size=(int(input_size[0]), int(input_size[1])),
            class_count=class_count,
            model_version=str(inference_data.get("model_version", "simulation-v1")),
        ),
        database=DatabaseConfig(
            path=_resolve(
                project_root,
                database_data.get("path", "data/detections.db"),
                "database.path",
            )
        ),
        simulation=SimulationConfig(
            seed=int(simulation_data.get("seed", 2026)),
            temperature_range_c=(float(temperature_range[0]), float(temperature_range[1])),
            humidity_range_pct=(float(humidity_range[0]), float(humidity_range[1])),
            generated_image_size=(int(generated_size[0]), int(generated_size[1])),
        ),
        camera=CameraConfig(
            resolution=(int(camera_resolution[0]), int(camera_resolution[1])),
            rotation=camera_rotation,
            warmup_seconds=camera_warmup_seconds,
            save_captures=bool(camera_data.get("save_captures", False)),
            capture_dir=_resolve(
                project_root,
                camera_data.get("capture_dir", "data/captures"),
                "camera.capture_dir",
            ),
        ),
        sensor=SensorConfig(
            backend=sensor_backend,
            gpio_pin=sensor_gpio_pin,
            use_pulseio=bool(sensor_data.get("use_pulseio", False)),
            retries=sensor_retries,
            retry_delay_s=sensor_retry_delay_s,
        ),
        api=ApiConfig(
            host=str(api_data.get("host", "127.0.0.1")),
            port=int(api_data.get("port", 5000)),
            debug=bool(api_data.get("debug", False)),
        ),
        monitoring=MonitoringConfig(
            enabled=bool(monitoring_data.get("enabled", True)),
            source=monitoring_source,
            capture_interval_s=capture_interval_s,
            auto_start=bool(monitoring_data.get("auto_start", False)),
            stop_timeout_s=stop_timeout_s,
        ),
        diseases=_load_diseases(disease_path, class_count),
    )
