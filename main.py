"""Command-line entry point for simulation and local API development."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.api import create_app
from src.camera import PiCameraSource
from src.camera.simulation import (
    GeneratedImageSource,
    create_generated_leaf_image,
    load_local_image,
)
from src.database.repository import ClassificationRepository
from src.inference.model_metadata import (
    load_model_metadata,
    metadata_path_for_model,
    validate_runtime_contract,
)
from src.inference.onnx_runner import OnnxClassifier
from src.inference.postprocessor import ClassificationPostprocessor
from src.inference.preprocessor import MobileNetPreprocessor
from src.inference.simulated_runner import SimulatedClassifier
from src.monitoring import ContinuousMonitoringService
from src.pipeline import ClassificationPipeline
from src.sensors import DHT22Sensor
from src.sensors.simulated import SimulatedDHT22
from src.utils.config import AppConfig, ConfigurationError, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tomato disease classification system")
    parser.add_argument("--config", default="config/config.yaml", help="YAML configuration path")
    parser.add_argument("--init-db", action="store_true", help="Create missing database tables")
    parser.add_argument("--simulate", action="store_true", help="Run one simulated classification")
    parser.add_argument("--classify", action="store_true", help="Run one classification")
    parser.add_argument(
        "--backend", choices=("simulation", "onnx", "hailo"), help="Override inference backend"
    )
    parser.add_argument("--image", type=Path, help="Local image to classify")
    parser.add_argument("--serve", action="store_true", help="Start the local REST API")
    parser.add_argument(
        "--check-hardware",
        action="store_true",
        help="Capture one Pi Camera frame and read the physical DHT22",
    )
    return parser


def build_simulation_pipeline(
    config: AppConfig, repository: ClassificationRepository
) -> ClassificationPipeline:
    return ClassificationPipeline(
        preprocessor=MobileNetPreprocessor(config.inference.input_size),
        classifier=SimulatedClassifier(config.inference.class_count),
        postprocessor=ClassificationPostprocessor(
            diseases=config.diseases,
            confidence_threshold=config.inference.confidence_threshold,
            model_version=config.inference.model_version,
        ),
        sensor=build_sensor(config),
        repository=repository,
    )


def build_onnx_pipeline(
    config: AppConfig, repository: ClassificationRepository
) -> ClassificationPipeline:
    model_path = config.inference.onnx_model_path
    metadata = load_model_metadata(metadata_path_for_model(model_path))
    validate_runtime_contract(
        metadata,
        config.diseases,
        config.inference.input_size,
        model_path,
    )
    return ClassificationPipeline(
        preprocessor=MobileNetPreprocessor(config.inference.input_size),
        classifier=OnnxClassifier(model_path, metadata),
        postprocessor=ClassificationPostprocessor(
            diseases=config.diseases,
            confidence_threshold=config.inference.confidence_threshold,
            model_version=metadata.model_version,
        ),
        sensor=build_sensor(config),
        repository=repository,
    )


def build_pipeline(
    config: AppConfig,
    repository: ClassificationRepository,
    backend: str,
) -> ClassificationPipeline:
    if backend == "simulation":
        return build_simulation_pipeline(config, repository)
    if backend == "onnx":
        return build_onnx_pipeline(config, repository)
    if backend == "hailo":
        raise ValueError("The Hailo backend has not been implemented yet")
    raise ValueError(f"Unsupported inference backend: {backend}")


def build_sensor(config: AppConfig) -> SimulatedDHT22 | DHT22Sensor:
    """Create the configured environmental sensor without importing GPIO on desktop."""

    if config.sensor.backend == "simulation":
        return SimulatedDHT22(
            temperature_range_c=config.simulation.temperature_range_c,
            humidity_range_pct=config.simulation.humidity_range_pct,
            seed=config.simulation.seed,
        )
    if config.sensor.backend == "dht22":
        return DHT22Sensor(
            gpio_pin=config.sensor.gpio_pin,
            use_pulseio=config.sensor.use_pulseio,
            retries=config.sensor.retries,
            retry_delay_s=config.sensor.retry_delay_s,
        )
    raise ValueError(f"Unsupported sensor backend: {config.sensor.backend}")


def build_image_source(config: AppConfig) -> GeneratedImageSource | PiCameraSource:
    """Create the configured continuous-monitoring image source."""

    if config.monitoring.source == "simulation":
        return GeneratedImageSource(config.simulation.generated_image_size)
    if config.monitoring.source == "picamera2":
        return PiCameraSource(
            resolution=config.camera.resolution,
            rotation=config.camera.rotation,
            warmup_seconds=config.camera.warmup_seconds,
            save_captures=config.camera.save_captures,
            capture_dir=config.camera.capture_dir,
        )
    raise ValueError(f"Unsupported monitoring source: {config.monitoring.source}")


def run(arguments: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(arguments)
    if args.simulate and args.classify:
        parser.error("Use either --simulate or --classify, not both")
    if args.simulate and args.backend:
        parser.error("--simulate already selects the simulation backend")
    if args.image and not (args.simulate or args.classify):
        parser.error("--image requires --simulate or --classify")
    if not (args.init_db or args.simulate or args.classify or args.serve or args.check_hardware):
        parser.print_help()
        return 0

    repository: ClassificationRepository | None = None
    monitoring_service: ContinuousMonitoringService | None = None
    try:
        config = load_config(args.config)
        repository = ClassificationRepository(config.database.path)
        repository.create_schema()

        if args.init_db:
            print(json.dumps({"database": str(config.database.path), "status": "initialized"}))

        if args.check_hardware:
            camera = PiCameraSource(
                resolution=config.camera.resolution,
                rotation=config.camera.rotation,
                warmup_seconds=config.camera.warmup_seconds,
                save_captures=config.camera.save_captures,
                capture_dir=config.camera.capture_dir,
            )
            sensor = None
            try:
                sensor = DHT22Sensor(
                    gpio_pin=config.sensor.gpio_pin,
                    use_pulseio=config.sensor.use_pulseio,
                    retries=config.sensor.retries,
                    retry_delay_s=config.sensor.retry_delay_s,
                )
                captured = camera.capture()
                measurement = sensor.read()
                print(
                    json.dumps(
                        {
                            "status": "hardware_available",
                            "camera": {
                                "image_path": captured.image_path,
                                "size": list(captured.image.size),
                                "mode": captured.image.mode,
                            },
                            "sensor": {
                                "gpio_pin": config.sensor.gpio_pin,
                                "temperature_c": measurement.temperature_c,
                                "humidity_pct": measurement.humidity_pct,
                                "recorded_at": measurement.recorded_at.isoformat(),
                            },
                        },
                        indent=2,
                    )
                )
            finally:
                if sensor is not None:
                    sensor.close()
                camera.close()

        if args.simulate or args.classify:
            backend = "simulation" if args.simulate else (args.backend or config.inference.backend)
            if backend != "simulation" and args.image is None:
                raise ValueError(f"--image is required when using the {backend} backend")
            pipeline = build_pipeline(config, repository, backend)
            try:
                if args.image:
                    image = load_local_image(args.image)
                    image_path = str(args.image.resolve())
                else:
                    image = create_generated_leaf_image(config.simulation.generated_image_size)
                    image_path = "simulation://generated-leaf"
                result = pipeline.run(image, image_path)
                print(json.dumps(result.to_dict(), indent=2))
            finally:
                pipeline.close()

        if args.serve:
            if config.monitoring.enabled:
                monitoring_pipeline = build_pipeline(config, repository, config.inference.backend)
                monitoring_source = None
                try:
                    monitoring_source = build_image_source(config)
                    monitoring_service = ContinuousMonitoringService(
                        pipeline=monitoring_pipeline,
                        image_source=monitoring_source,
                        capture_interval_s=config.monitoring.capture_interval_s,
                        stop_timeout_s=config.monitoring.stop_timeout_s,
                    )
                except Exception:
                    if monitoring_source is not None:
                        close_source = getattr(monitoring_source, "close", None)
                        if callable(close_source):
                            close_source()
                    monitoring_pipeline.close()
                    raise
                if config.monitoring.auto_start:
                    monitoring_service.start()
            app = create_app(repository, monitoring_service)
            app.run(
                host=config.api.host,
                port=config.api.port,
                debug=config.api.debug,
                use_reloader=False,
            )

        return 0
    except (ConfigurationError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            if monitoring_service is not None:
                monitoring_service.close()
        finally:
            if repository is not None:
                repository.close()


if __name__ == "__main__":
    raise SystemExit(run())
