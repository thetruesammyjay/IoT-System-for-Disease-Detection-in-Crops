from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from src.inference.model_metadata import IMAGENET_MEAN, IMAGENET_STD, ModelMetadata
from src.inference.onnx_runner import OnnxClassifier


@dataclass
class _Node:
    name: str


class _FakeSession:
    def __init__(self) -> None:
        self.received: np.ndarray | None = None

    def get_inputs(self) -> list[_Node]:
        return [_Node("input")]

    def get_outputs(self) -> list[_Node]:
        return [_Node("logits")]

    def run(self, output_names, inputs):
        assert output_names == ["logits"]
        self.received = inputs["input"]
        return [np.asarray([[0.1, 0.2, 0.3, 0.4, 0.5]], dtype=np.float32)]


def _metadata() -> ModelMetadata:
    names = ("A", "B", "C", "D", "E")
    return ModelMetadata(
        schema_version=1,
        architecture="mobilenet_v2",
        model_version="test-v1",
        class_names=names,
        class_to_index={name: index for index, name in enumerate(names)},
        input_size=(224, 224),
        normalization_mean=IMAGENET_MEAN,
        normalization_std=IMAGENET_STD,
        input_name="input",
        output_name="logits",
        opset_version=17,
        checkpoint_path="checkpoint.pt",
        checkpoint_sha256="checkpoint-hash",
        onnx_sha256="onnx-hash",
    )


def test_onnx_classifier_returns_five_logits() -> None:
    session = _FakeSession()
    classifier = OnnxClassifier("unused.onnx", _metadata(), session=session)
    tensor = np.zeros((1, 3, 224, 224), dtype=np.float64)

    output = classifier.predict(tensor)

    assert output.shape == (1, 5)
    assert output.dtype == np.float32
    assert session.received is not None
    assert session.received.dtype == np.float32


def test_onnx_classifier_rejects_wrong_input_shape() -> None:
    classifier = OnnxClassifier("unused.onnx", _metadata(), session=_FakeSession())

    with pytest.raises(ValueError, match="input shape"):
        classifier.predict(np.zeros((1, 3, 640, 640), dtype=np.float32))
