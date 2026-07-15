from __future__ import annotations

from pathlib import Path

import pytest

from src.inference.model_metadata import (
    IMAGENET_MEAN,
    IMAGENET_STD,
    ModelMetadata,
    ModelMetadataError,
    load_model_metadata,
    save_model_metadata,
    sha256_file,
    validate_runtime_contract,
)
from src.utils.config import AppConfig


def _metadata(onnx_hash: str, app_config: AppConfig) -> ModelMetadata:
    class_names = tuple(disease.label for disease in app_config.diseases)
    return ModelMetadata(
        schema_version=1,
        architecture="mobilenet_v2",
        model_version="test-model-v1",
        class_names=class_names,
        class_to_index={label: index for index, label in enumerate(class_names)},
        input_size=(224, 224),
        normalization_mean=IMAGENET_MEAN,
        normalization_std=IMAGENET_STD,
        input_name="input",
        output_name="logits",
        opset_version=17,
        checkpoint_path="test.pt",
        checkpoint_sha256="checkpoint-hash",
        onnx_sha256=onnx_hash,
    )


def test_model_metadata_round_trip_and_runtime_validation(
    tmp_path: Path, app_config: AppConfig
) -> None:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"test-onnx-content")
    metadata = _metadata(sha256_file(model_path), app_config)
    metadata_path = tmp_path / "model.metadata.json"

    save_model_metadata(metadata, metadata_path)
    loaded = load_model_metadata(metadata_path)
    validate_runtime_contract(
        loaded, app_config.diseases, app_config.inference.input_size, model_path
    )

    assert loaded == metadata


def test_runtime_contract_rejects_modified_model(tmp_path: Path, app_config: AppConfig) -> None:
    model_path = tmp_path / "model.onnx"
    model_path.write_bytes(b"original")
    metadata = _metadata(sha256_file(model_path), app_config)
    model_path.write_bytes(b"modified")

    with pytest.raises(ModelMetadataError, match="hash"):
        validate_runtime_contract(
            metadata, app_config.diseases, app_config.inference.input_size, model_path
        )
