"""Shared domain objects for classification, sensing, and persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from PIL import Image


@dataclass(frozen=True, slots=True)
class DiseaseClass:
    """One model output class and its project metadata."""

    index: int
    label: str
    dataset_label: str
    severity: str


@dataclass(frozen=True, slots=True)
class ClassificationOutcome:
    """Postprocessed output from one classifier invocation."""

    label: str
    confidence: float
    status: str
    severity: str
    probabilities: dict[str, float]
    model_version: str


@dataclass(frozen=True, slots=True)
class SensorMeasurement:
    """Temperature and humidity observed near classification time."""

    temperature_c: float
    humidity_pct: float
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class CapturedImage:
    """An image and the source identifier stored with its classification."""

    image: Image.Image
    image_path: str


@dataclass(frozen=True, slots=True)
class StoredSensorReading:
    """Serializable environmental reading loaded from persistence."""

    id: int
    temperature_c: float
    humidity_pct: float
    recorded_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "recorded_at": self.recorded_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class StoredClassification:
    """Serializable representation of a persisted classification record."""

    id: int
    image_path: str
    disease_label: str
    confidence: float
    prediction_status: str
    severity: str
    model_version: str
    processing_time_ms: float
    captured_at: datetime
    temperature_c: float
    humidity_pct: float
    probabilities: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        """Return an API- and CLI-friendly representation."""

        return {
            "id": self.id,
            "image_path": self.image_path,
            "disease_label": self.disease_label,
            "confidence": self.confidence,
            "prediction_status": self.prediction_status,
            "severity": self.severity,
            "model_version": self.model_version,
            "processing_time_ms": self.processing_time_ms,
            "captured_at": self.captured_at.isoformat(),
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "probabilities": self.probabilities,
        }
