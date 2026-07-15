"""Portable metadata contract for exported classification models."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.domain import DiseaseClass

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class ModelMetadataError(ValueError):
    """Raised when model metadata is missing or incompatible with the application."""


@dataclass(frozen=True, slots=True)
class ModelMetadata:
    schema_version: int
    architecture: str
    model_version: str
    class_names: tuple[str, ...]
    class_to_index: dict[str, int]
    input_size: tuple[int, int]
    normalization_mean: tuple[float, float, float]
    normalization_std: tuple[float, float, float]
    input_name: str
    output_name: str
    opset_version: int
    checkpoint_path: str
    checkpoint_sha256: str
    onnx_sha256: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["class_names"] = list(self.class_names)
        data["input_size"] = list(self.input_size)
        data["normalization_mean"] = list(self.normalization_mean)
        data["normalization_std"] = list(self.normalization_std)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelMetadata:
        try:
            metadata = cls(
                schema_version=int(data["schema_version"]),
                architecture=str(data["architecture"]),
                model_version=str(data["model_version"]),
                class_names=tuple(str(value) for value in data["class_names"]),
                class_to_index={
                    str(label): int(index) for label, index in data["class_to_index"].items()
                },
                input_size=tuple(int(value) for value in data["input_size"]),
                normalization_mean=tuple(float(value) for value in data["normalization_mean"]),
                normalization_std=tuple(float(value) for value in data["normalization_std"]),
                input_name=str(data["input_name"]),
                output_name=str(data["output_name"]),
                opset_version=int(data["opset_version"]),
                checkpoint_path=str(data["checkpoint_path"]),
                checkpoint_sha256=str(data["checkpoint_sha256"]),
                onnx_sha256=str(data["onnx_sha256"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelMetadataError(f"Invalid model metadata: {exc}") from exc
        metadata.validate()
        return metadata

    def validate(self) -> None:
        if self.schema_version != 1:
            raise ModelMetadataError(
                f"Unsupported model metadata schema version: {self.schema_version}"
            )
        if self.architecture != "mobilenet_v2":
            raise ModelMetadataError(f"Unsupported architecture: {self.architecture}")
        if len(self.class_names) != 5:
            raise ModelMetadataError("The deployed model must contain exactly five classes")
        expected_mapping = {label: index for index, label in enumerate(self.class_names)}
        if self.class_to_index != expected_mapping:
            raise ModelMetadataError("class_to_index does not match class_names order")
        if len(self.input_size) != 2 or min(self.input_size) <= 0:
            raise ModelMetadataError("input_size must contain two positive dimensions")
        if len(self.normalization_mean) != 3 or len(self.normalization_std) != 3:
            raise ModelMetadataError("Normalization metadata must contain three channels")
        if not self.model_version or not self.input_name or not self.output_name:
            raise ModelMetadataError("Model version and tensor names cannot be empty")
        if self.opset_version <= 0:
            raise ModelMetadataError("ONNX opset version must be positive")
        if not self.checkpoint_sha256 or not self.onnx_sha256:
            raise ModelMetadataError("Model hashes cannot be empty")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def metadata_path_for_model(model_path: str | Path) -> Path:
    return Path(model_path).with_suffix(".metadata.json")


def save_model_metadata(metadata: ModelMetadata, path: str | Path) -> None:
    metadata.validate()
    Path(path).write_text(json.dumps(metadata.to_dict(), indent=2) + "\n", encoding="utf-8")


def load_model_metadata(path: str | Path) -> ModelMetadata:
    metadata_path = Path(path)
    if not metadata_path.is_file():
        raise ModelMetadataError(f"Model metadata file does not exist: {metadata_path}")
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ModelMetadataError(f"Invalid JSON in {metadata_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ModelMetadataError("Model metadata must be a JSON object")
    return ModelMetadata.from_dict(data)


def validate_runtime_contract(
    metadata: ModelMetadata,
    diseases: tuple[DiseaseClass, ...],
    configured_input_size: tuple[int, int],
    model_path: str | Path,
) -> None:
    configured_labels = tuple(disease.label for disease in diseases)
    if metadata.class_names != configured_labels:
        raise ModelMetadataError(
            "ONNX class order does not match config/diseases.yaml: "
            f"{metadata.class_names} != {configured_labels}"
        )
    if metadata.input_size != configured_input_size:
        raise ModelMetadataError(
            f"ONNX input size {metadata.input_size} does not match configured size "
            f"{configured_input_size}"
        )
    if metadata.normalization_mean != IMAGENET_MEAN:
        raise ModelMetadataError("ONNX normalization mean does not match the runtime contract")
    if metadata.normalization_std != IMAGENET_STD:
        raise ModelMetadataError("ONNX normalization standard deviation does not match runtime")
    actual_hash = sha256_file(model_path)
    if actual_hash != metadata.onnx_sha256:
        raise ModelMetadataError("ONNX file hash does not match its metadata")
