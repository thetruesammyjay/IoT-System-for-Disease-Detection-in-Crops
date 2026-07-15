"""End-to-end image classification pipeline."""

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from typing import Protocol

import numpy as np
from PIL import Image

from src.database.repository import ClassificationRepository
from src.domain import SensorMeasurement, StoredClassification
from src.inference.postprocessor import ClassificationPostprocessor
from src.inference.preprocessor import MobileNetPreprocessor


class Classifier(Protocol):
    def predict(self, tensor: np.ndarray) -> np.ndarray: ...


class Sensor(Protocol):
    def read(self) -> SensorMeasurement: ...


class ClassificationPipeline:
    def __init__(
        self,
        preprocessor: MobileNetPreprocessor,
        classifier: Classifier,
        postprocessor: ClassificationPostprocessor,
        sensor: Sensor,
        repository: ClassificationRepository,
    ) -> None:
        self.preprocessor = preprocessor
        self.classifier = classifier
        self.postprocessor = postprocessor
        self.sensor = sensor
        self.repository = repository

    def run(self, image: Image.Image, image_path: str) -> StoredClassification:
        started_at = perf_counter()
        captured_at = datetime.now(UTC)
        tensor = self.preprocessor.preprocess(image)
        logits = self.classifier.predict(tensor)
        outcome = self.postprocessor.process(logits)
        sensor_measurement = self.sensor.read()
        processing_time_ms = (perf_counter() - started_at) * 1000.0

        return self.repository.save_classification(
            outcome=outcome,
            sensor=sensor_measurement,
            image_path=image_path,
            processing_time_ms=round(processing_time_ms, 3),
            captured_at=captured_at,
        )

    def close(self) -> None:
        """Release optional hardware resources owned by pipeline components."""

        for component in (self.sensor, self.classifier):
            close = getattr(component, "close", None)
            if callable(close):
                close()
