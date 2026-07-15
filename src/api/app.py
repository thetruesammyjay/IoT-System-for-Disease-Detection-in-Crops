"""REST API for monitoring control, classifications, sensors, and reports."""

from __future__ import annotations

import csv
import io
import json
import platform
import sys
from datetime import UTC, datetime
from typing import Any

from flask import Flask, Response, jsonify, render_template, request

from src.database.repository import ClassificationRepository
from src.monitoring import ContinuousMonitoringService, MonitoringBusyError


class ApiValidationError(ValueError):
    pass


def _integer_query(name: str, default: int, minimum: int, maximum: int) -> int:
    raw_value = request.args.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ApiValidationError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ApiValidationError(f"{name} must be between {minimum} and {maximum}")
    return value


def _datetime_query(name: str) -> datetime | None:
    raw_value = request.args.get(name)
    if not raw_value:
        return None
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApiValidationError(f"{name} must be an ISO 8601 timestamp") from exc
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed


def _classification_filters() -> dict[str, Any]:
    status = request.args.get("status")
    if status is not None and status not in {"accepted", "uncertain"}:
        raise ApiValidationError("status must be accepted or uncertain")
    from_time = _datetime_query("from")
    to_time = _datetime_query("to")
    if from_time is not None and to_time is not None and from_time > to_time:
        raise ApiValidationError("from cannot be later than to")
    return {
        "disease": request.args.get("disease"),
        "status": status,
        "from_time": from_time,
        "to_time": to_time,
    }


def _monitoring_unavailable() -> tuple[object, int]:
    return jsonify({"error": "Continuous monitoring is not configured"}), 503


def create_app(
    repository: ClassificationRepository,
    monitoring: ContinuousMonitoringService | None = None,
) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def dashboard() -> str:
        return render_template("dashboard.html")

    @app.errorhandler(ApiValidationError)
    def validation_error(error: ApiValidationError) -> tuple[object, int]:
        return jsonify({"error": str(error)}), 400

    @app.get("/api/v1/system/health")
    def health() -> tuple[object, int]:
        database_available = repository.ping()
        payload: dict[str, object] = {
            "status": "ok" if database_available else "degraded",
            "database": "available" if database_available else "unavailable",
        }
        if monitoring is not None:
            payload["monitoring"] = monitoring.status().to_dict()
        return jsonify(payload), 200 if database_available else 503

    @app.get("/api/v1/system/info")
    def system_info() -> tuple[object, int]:
        return (
            jsonify(
                {
                    "application": "iot-tomato-disease-detection",
                    "version": "0.1.0",
                    "python_version": sys.version.split()[0],
                    "platform": platform.platform(),
                    "classification_records": repository.count(),
                    "monitoring_configured": monitoring is not None,
                }
            ),
            200,
        )

    @app.get("/api/v1/detections/latest")
    def latest() -> tuple[object, int]:
        record = repository.latest()
        if record is None:
            return jsonify({"error": "No classification records are available"}), 404
        return jsonify(record.to_dict()), 200

    @app.get("/api/v1/detections/<int:record_id>")
    def detection_by_id(record_id: int) -> tuple[object, int]:
        record = repository.get_by_id(record_id)
        if record is None:
            return jsonify({"error": "Classification record was not found"}), 404
        return jsonify(record.to_dict()), 200

    @app.get("/api/v1/detections")
    def detections() -> tuple[object, int]:
        limit = _integer_query("limit", 20, 1, 100)
        offset = _integer_query("offset", 0, 0, 1_000_000)
        filters = _classification_filters()
        records, total = repository.query_classifications(
            limit=limit,
            offset=offset,
            **filters,
        )
        return (
            jsonify(
                {
                    "items": [record.to_dict() for record in records],
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "returned": len(records),
                        "total": total,
                    },
                }
            ),
            200,
        )

    @app.get("/api/v1/sensors/latest")
    def latest_sensor() -> tuple[object, int]:
        reading = repository.latest_sensor_reading()
        if reading is None:
            return jsonify({"error": "No sensor readings are available"}), 404
        return jsonify(reading.to_dict()), 200

    @app.get("/api/v1/sensors/history")
    def sensor_history() -> tuple[object, int]:
        limit = _integer_query("limit", 100, 1, 500)
        offset = _integer_query("offset", 0, 0, 1_000_000)
        from_time = _datetime_query("from")
        to_time = _datetime_query("to")
        if from_time is not None and to_time is not None and from_time > to_time:
            raise ApiValidationError("from cannot be later than to")
        readings, total = repository.query_sensor_readings(
            limit=limit,
            offset=offset,
            from_time=from_time,
            to_time=to_time,
        )
        return (
            jsonify(
                {
                    "items": [reading.to_dict() for reading in readings],
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "returned": len(readings),
                        "total": total,
                    },
                }
            ),
            200,
        )

    @app.post("/api/v1/inference/trigger")
    def trigger_inference() -> tuple[object, int]:
        if monitoring is None:
            return _monitoring_unavailable()
        try:
            result = monitoring.run_once()
        except MonitoringBusyError as exc:
            return jsonify({"error": str(exc)}), 409
        except Exception as exc:
            return jsonify({"error": f"Classification failed: {exc}"}), 500
        return jsonify(result.to_dict()), 201

    @app.get("/api/v1/monitoring/status")
    def monitoring_status() -> tuple[object, int]:
        if monitoring is None:
            return _monitoring_unavailable()
        return jsonify(monitoring.status().to_dict()), 200

    @app.post("/api/v1/monitoring/start")
    def start_monitoring() -> tuple[object, int]:
        if monitoring is None:
            return _monitoring_unavailable()
        started = monitoring.start()
        return (
            jsonify({"changed": started, "monitoring": monitoring.status().to_dict()}),
            202 if started else 200,
        )

    @app.post("/api/v1/monitoring/stop")
    def stop_monitoring() -> tuple[object, int]:
        if monitoring is None:
            return _monitoring_unavailable()
        try:
            stopped = monitoring.stop()
        except TimeoutError as exc:
            return jsonify({"error": str(exc)}), 503
        return jsonify({"changed": stopped, "monitoring": monitoring.status().to_dict()}), 200

    @app.get("/api/v1/reports/export")
    def export_report() -> Response | tuple[object, int]:
        export_format = request.args.get("format", "json").lower()
        if export_format not in {"csv", "json"}:
            raise ApiValidationError("format must be csv or json")
        filters = _classification_filters()
        records = repository.all_classifications(**filters)
        payload = [record.to_dict() for record in records]
        if export_format == "json":
            content = json.dumps({"items": payload}, indent=2)
            return Response(
                content,
                mimetype="application/json",
                headers={"Content-Disposition": "attachment; filename=classifications.json"},
            )

        output = io.StringIO(newline="")
        fields = [
            "id",
            "image_path",
            "disease_label",
            "confidence",
            "prediction_status",
            "severity",
            "model_version",
            "processing_time_ms",
            "captured_at",
            "temperature_c",
            "humidity_pct",
            "probabilities",
        ]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in payload:
            row["probabilities"] = json.dumps(row["probabilities"], sort_keys=True)
            writer.writerow(row)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=classifications.csv"},
        )

    return app
