"""Classification probability and confidence handling."""

from __future__ import annotations

import numpy as np

from src.domain import ClassificationOutcome, DiseaseClass


class ClassificationOutputError(ValueError):
    """Raised when classifier output does not match the configured class contract."""


class ClassificationPostprocessor:
    def __init__(
        self,
        diseases: tuple[DiseaseClass, ...],
        confidence_threshold: float,
        model_version: str,
    ) -> None:
        self.diseases = diseases
        self.confidence_threshold = confidence_threshold
        self.model_version = model_version

    def process(self, logits: np.ndarray) -> ClassificationOutcome:
        values = np.asarray(logits, dtype=np.float64).squeeze()
        if values.ndim != 1 or values.size != len(self.diseases):
            raise ClassificationOutputError(
                f"Expected {len(self.diseases)} logits but received shape {np.shape(logits)}"
            )
        if not np.all(np.isfinite(values)):
            raise ClassificationOutputError("Classifier output contains a non-finite value")

        shifted = values - np.max(values)
        exponentials = np.exp(shifted)
        probabilities = exponentials / np.sum(exponentials)
        best_index = int(np.argmax(probabilities))
        disease = self.diseases[best_index]
        confidence = float(probabilities[best_index])
        accepted = confidence >= self.confidence_threshold

        return ClassificationOutcome(
            label=disease.label,
            confidence=confidence,
            status="accepted" if accepted else "uncertain",
            severity=disease.severity if accepted else "unassigned",
            probabilities={item.label: float(probabilities[item.index]) for item in self.diseases},
            model_version=self.model_version,
        )
