"""ONNX Runtime backend for the five-class MobileNetV2 model."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import numpy as np

from src.inference.model_metadata import ModelMetadata


class _Session(Protocol):
    def get_inputs(self) -> list[Any]: ...

    def get_outputs(self) -> list[Any]: ...

    def run(self, output_names: list[str], inputs: dict[str, np.ndarray]) -> list[Any]: ...


class OnnxClassifier:
    """Execute exported logits through ONNX Runtime."""

    def __init__(
        self,
        model_path: str | Path,
        metadata: ModelMetadata,
        session: _Session | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata = metadata
        if session is None:
            if not self.model_path.is_file():
                raise FileNotFoundError(f"ONNX model does not exist: {self.model_path}")
            try:
                import onnxruntime as ort
            except ImportError as exc:
                raise RuntimeError(
                    "ONNX Runtime is not installed. Run uv sync --extra simulation."
                ) from exc
            session = ort.InferenceSession(str(self.model_path), providers=["CPUExecutionProvider"])
        self.session = session

        input_names = [item.name for item in self.session.get_inputs()]
        output_names = [item.name for item in self.session.get_outputs()]
        if metadata.input_name not in input_names:
            raise ValueError(
                f"ONNX input {metadata.input_name!r} was not found; available inputs: {input_names}"
            )
        if metadata.output_name not in output_names:
            raise ValueError(
                f"ONNX output {metadata.output_name!r} was not found; "
                f"available outputs: {output_names}"
            )

    def predict(self, tensor: np.ndarray) -> np.ndarray:
        expected_shape = (1, 3, *self.metadata.input_size)
        if tensor.shape != expected_shape:
            raise ValueError(f"Expected ONNX input shape {expected_shape}, received {tensor.shape}")
        prepared = np.ascontiguousarray(tensor, dtype=np.float32)
        outputs = self.session.run(
            [self.metadata.output_name], {self.metadata.input_name: prepared}
        )
        if len(outputs) != 1:
            raise ValueError(f"Expected one ONNX output but received {len(outputs)}")
        logits = np.asarray(outputs[0], dtype=np.float32)
        expected_output_shape = (1, len(self.metadata.class_names))
        if logits.shape != expected_output_shape:
            raise ValueError(
                f"Expected ONNX output shape {expected_output_shape}, received {logits.shape}"
            )
        return logits
