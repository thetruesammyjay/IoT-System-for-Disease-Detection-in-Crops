"""Export a trained MobileNetV2 checkpoint to ONNX with deployment metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import onnx
import torch

from models.training.modeling import IMAGENET_MEAN, IMAGENET_STD, build_mobilenet_v2
from src.inference.model_metadata import (
    ModelMetadata,
    metadata_path_for_model,
    save_model_metadata,
    sha256_file,
)


def _load_checkpoint(path: Path) -> dict[str, object]:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(path, map_location="cpu")


def _verify_runtime_parity(
    model: torch.nn.Module,
    dummy_input: torch.Tensor,
    output_path: Path,
) -> None:
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError(
            "ONNX Runtime is required for export verification. Install the simulation extra "
            "or use --no-verify-runtime."
        ) from exc

    with torch.inference_mode():
        pytorch_logits = model(dummy_input).detach().cpu().numpy()
    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    onnx_logits = session.run(["logits"], {"input": dummy_input.numpy()})[0]
    np.testing.assert_allclose(onnx_logits, pytorch_logits, rtol=1e-4, atol=1e-5)


def export_onnx(args: argparse.Namespace) -> tuple[Path, Path]:
    checkpoint_path = args.checkpoint.resolve()
    output_path = args.output.resolve()
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Checkpoint does not exist: {checkpoint_path}")

    checkpoint = _load_checkpoint(checkpoint_path)
    architecture = str(checkpoint.get("architecture", ""))
    if architecture != "mobilenet_v2":
        raise ValueError(f"Unsupported checkpoint architecture: {architecture}")
    class_names = tuple(str(value) for value in checkpoint["classes"])
    class_to_index = {
        str(label): int(index) for label, index in checkpoint["class_to_index"].items()
    }
    input_size_value = checkpoint.get("input_size", 224)
    input_size = int(input_size_value)

    model = build_mobilenet_v2(len(class_names), pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dummy_input = torch.zeros((1, 3, input_size, input_size), dtype=torch.float32)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=args.opset,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
        dynamo=False,
    )
    exported_model = onnx.load(output_path)
    onnx.checker.check_model(exported_model)
    if args.verify_runtime:
        _verify_runtime_parity(model, dummy_input, output_path)

    metadata = ModelMetadata(
        schema_version=1,
        architecture="mobilenet_v2",
        model_version=str(checkpoint.get("model_version", "tomato-mobilenetv2-v1")),
        class_names=class_names,
        class_to_index=class_to_index,
        input_size=(input_size, input_size),
        normalization_mean=IMAGENET_MEAN,
        normalization_std=IMAGENET_STD,
        input_name="input",
        output_name="logits",
        opset_version=args.opset,
        checkpoint_path=str(checkpoint_path),
        checkpoint_sha256=sha256_file(checkpoint_path),
        onnx_sha256=sha256_file(output_path),
    )
    metadata_path = metadata_path_for_model(output_path)
    save_model_metadata(metadata, metadata_path)
    print(f"ONNX model written to {output_path}")
    print(f"Model metadata written to {metadata_path}")
    return output_path, metadata_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export MobileNetV2 checkpoint to ONNX")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("models/onnx/tomato_mobilenet_v2.onnx"))
    parser.add_argument("--opset", type=int, default=17)
    parser.add_argument("--verify-runtime", action=argparse.BooleanOptionalAction, default=True)
    return parser


def main(arguments: list[str] | None = None) -> int:
    export_onnx(build_parser().parse_args(arguments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
