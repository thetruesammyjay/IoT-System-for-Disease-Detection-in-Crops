from __future__ import annotations

import pytest

from src.camera.simulation import create_generated_leaf_image
from src.database.repository import ClassificationRepository
from src.inference.postprocessor import ClassificationPostprocessor
from src.inference.preprocessor import MobileNetPreprocessor
from src.inference.simulated_runner import SimulatedClassifier
from src.pipeline import ClassificationPipeline
from src.sensors.simulated import SimulatedDHT22
from src.utils.config import AppConfig


@pytest.mark.integration
def test_simulated_pipeline_classifies_and_stores_one_image(
    app_config: AppConfig,
    repository: ClassificationRepository,
) -> None:
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

    result = pipeline.run(
        create_generated_leaf_image(app_config.simulation.generated_image_size),
        "simulation://integration-test",
    )

    assert result.id == 1
    assert result.disease_label in {disease.label for disease in app_config.diseases}
    assert result.prediction_status in {"accepted", "uncertain"}
    assert len(result.probabilities) == 5
    assert repository.count() == 1
