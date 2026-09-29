from __future__ import annotations

import json
from datetime import UTC, datetime
from io import BytesIO

from PIL import Image

from src.api import create_app
from src.camera.simulation import GeneratedImageSource
from src.database.repository import ClassificationRepository
from src.domain import ClassificationOutcome, SensorMeasurement
from src.inference.postprocessor import ClassificationPostprocessor
from src.inference.preprocessor import MobileNetPreprocessor
from src.inference.simulated_runner import SimulatedClassifier
from src.monitoring import ContinuousMonitoringService
from src.pipeline import ClassificationPipeline
from src.sensors.simulated import SimulatedDHT22
from src.utils.config import AppConfig


def _save_record(
    repository: ClassificationRepository,
    label: str = "Late Blight",
    status: str = "accepted",
) -> None:
    now = datetime.now(UTC)
    repository.save_classification(
        outcome=ClassificationOutcome(
            label=label,
            confidence=0.91,
            status=status,
            severity="high" if status == "accepted" else "unassigned",
            probabilities={label: 0.91},
            model_version="test-v1",
        ),
        sensor=SensorMeasurement(temperature_c=27.0, humidity_pct=70.0, recorded_at=now),
        image_path="test://leaf",
        processing_time_ms=12.5,
        captured_at=now,
    )


def _build_monitoring(
    repository: ClassificationRepository,
    app_config: AppConfig,
) -> ContinuousMonitoringService:
    pipeline = ClassificationPipeline(
        preprocessor=MobileNetPreprocessor(app_config.inference.input_size),
        classifier=SimulatedClassifier(app_config.inference.class_count),
        postprocessor=ClassificationPostprocessor(
            app_config.diseases,
            app_config.inference.confidence_threshold,
            app_config.inference.model_version,
        ),
        sensor=SimulatedDHT22(
            app_config.simulation.temperature_range_c,
            app_config.simulation.humidity_range_pct,
            seed=app_config.simulation.seed,
        ),
        repository=repository,
    )
    return ContinuousMonitoringService(
        pipeline,
        GeneratedImageSource(app_config.simulation.generated_image_size),
        capture_interval_s=1.0,
    )


def test_health_endpoint(repository: ClassificationRepository) -> None:
    client = create_app(repository).test_client()

    response = client.get("/api/v1/system/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_dashboard_and_static_assets_are_served(repository: ClassificationRepository) -> None:
    client = create_app(repository).test_client()

    dashboard = client.get("/")
    stylesheet = client.get("/static/dashboard.css")
    script = client.get("/static/dashboard.js")

    assert dashboard.status_code == 200
    assert "Tomato crop overview" in dashboard.get_data(as_text=True)
    assert "Analyze a tomato leaf image" in dashboard.get_data(as_text=True)
    assert stylesheet.status_code == 200
    assert script.status_code == 200


def test_latest_endpoint_returns_stored_classification(
    repository: ClassificationRepository,
) -> None:
    _save_record(repository)
    client = create_app(repository).test_client()

    response = client.get("/api/v1/detections/latest")

    assert response.status_code == 200
    assert response.get_json()["disease_label"] == "Late Blight"


def test_latest_endpoint_returns_404_when_database_is_empty(
    repository: ClassificationRepository,
) -> None:
    client = create_app(repository).test_client()

    response = client.get("/api/v1/detections/latest")

    assert response.status_code == 404


def test_detection_listing_supports_filters_and_pagination(
    repository: ClassificationRepository,
) -> None:
    _save_record(repository, "Late Blight", "accepted")
    _save_record(repository, "Early Blight", "uncertain")
    client = create_app(repository).test_client()

    response = client.get("/api/v1/detections?status=accepted&limit=1&offset=0")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["disease_label"] == "Late Blight"


def test_detection_and_sensor_records_can_be_retrieved(
    repository: ClassificationRepository,
) -> None:
    _save_record(repository)
    client = create_app(repository).test_client()

    detection_response = client.get("/api/v1/detections/1")
    sensor_response = client.get("/api/v1/sensors/latest")
    history_response = client.get("/api/v1/sensors/history")

    assert detection_response.status_code == 200
    assert sensor_response.status_code == 200
    assert history_response.get_json()["pagination"]["total"] == 1


def test_report_export_supports_csv_and_json(repository: ClassificationRepository) -> None:
    _save_record(repository)
    client = create_app(repository).test_client()

    csv_response = client.get("/api/v1/reports/export?format=csv")
    json_response = client.get("/api/v1/reports/export?format=json")

    assert csv_response.status_code == 200
    assert "disease_label" in csv_response.get_data(as_text=True).splitlines()[0]
    assert json_response.status_code == 200
    assert json.loads(json_response.get_data(as_text=True))["items"][0]["id"] == 1


def test_invalid_query_parameters_return_400(repository: ClassificationRepository) -> None:
    client = create_app(repository).test_client()

    response = client.get("/api/v1/detections?limit=invalid")

    assert response.status_code == 400
    assert "integer" in response.get_json()["error"]


def test_manual_inference_trigger_uses_monitoring_service(
    repository: ClassificationRepository,
    app_config: AppConfig,
) -> None:
    monitoring = _build_monitoring(repository, app_config)
    client = create_app(repository, monitoring).test_client()

    response = client.post("/api/v1/inference/trigger")
    status_response = client.get("/api/v1/monitoring/status")
    start_response = client.post("/api/v1/monitoring/start")
    stop_response = client.post("/api/v1/monitoring/stop")

    assert response.status_code == 201
    assert status_response.get_json()["cycles_completed"] == 1
    assert start_response.status_code == 202
    assert stop_response.status_code == 200
    assert stop_response.get_json()["monitoring"]["running"] is False


def test_leaf_image_upload_is_classified_and_stored(
    repository: ClassificationRepository,
    app_config: AppConfig,
    tmp_path,
) -> None:
    monitoring = _build_monitoring(repository, app_config)
    client = create_app(repository, monitoring, upload_dir=tmp_path / "uploads").test_client()
    image_bytes = BytesIO()
    Image.new("RGB", (96, 96), color=(48, 126, 64)).save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/api/v1/inference/upload",
        data={"image": (image_bytes, "tomato-leaf.png")},
        content_type="multipart/form-data",
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["uploaded_filename"] == "tomato-leaf.png"
    assert payload["id"] == 1
    assert repository.count() == 1
    assert len(list((tmp_path / "uploads").glob("*.png"))) == 1


def test_leaf_image_upload_rejects_invalid_content(
    repository: ClassificationRepository,
    app_config: AppConfig,
    tmp_path,
) -> None:
    monitoring = _build_monitoring(repository, app_config)
    client = create_app(repository, monitoring, upload_dir=tmp_path / "uploads").test_client()

    response = client.post(
        "/api/v1/inference/upload",
        data={"image": (BytesIO(b"not an image"), "leaf.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "The uploaded file is not a valid image"
    assert repository.count() == 0


def test_leaf_image_upload_enforces_size_limit(
    repository: ClassificationRepository,
    app_config: AppConfig,
    tmp_path,
) -> None:
    monitoring = _build_monitoring(repository, app_config)
    client = create_app(
        repository,
        monitoring,
        upload_dir=tmp_path / "uploads",
        max_upload_bytes=32,
    ).test_client()

    response = client.post(
        "/api/v1/inference/upload",
        data={"image": (BytesIO(b"x" * 128), "leaf.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert "must not exceed" in response.get_json()["error"]


def test_monitoring_endpoints_are_unavailable_without_service(
    repository: ClassificationRepository,
) -> None:
    client = create_app(repository).test_client()

    response = client.post("/api/v1/inference/trigger")

    assert response.status_code == 503
