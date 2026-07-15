"""Evaluate the best checkpoint once on the held-out test manifest."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from models.training.dataset import ManifestDataset
from models.training.metrics import (
    calculate_metrics,
    write_confusion_matrix_csv,
    write_confusion_matrix_plot,
    write_metrics,
)
from models.training.modeling import build_mobilenet_v2, evaluation_transform, select_device


def _load_checkpoint(path: Path, device: torch.device) -> dict[str, object]:
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


def evaluate(args: argparse.Namespace) -> dict[str, object]:
    device = select_device(args.device)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = _load_checkpoint(args.checkpoint.resolve(), device)
    class_names = list(checkpoint["classes"])
    input_size = int(checkpoint.get("input_size", 224))

    test_dataset = ManifestDataset(
        args.data_dir.resolve(), "test", evaluation_transform(input_size)
    )
    if test_dataset.classes != class_names:
        raise ValueError("Checkpoint and test-manifest class orders do not match")
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
    )

    model = build_mobilenet_v2(len(class_names), pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    actual: list[int] = []
    predicted: list[int] = []
    prediction_rows: list[dict[str, object]] = []
    with torch.inference_mode():
        for images, targets, image_paths in test_loader:
            probabilities = torch.softmax(model(images.to(device)), dim=1).cpu()
            confidences, predictions = torch.max(probabilities, dim=1)
            actual.extend(targets.tolist())
            predicted.extend(predictions.tolist())
            for position, image_path in enumerate(image_paths):
                actual_index = int(targets[position])
                predicted_index = int(predictions[position])
                row: dict[str, object] = {
                    "image_path": image_path,
                    "actual_index": actual_index,
                    "actual_label": class_names[actual_index],
                    "predicted_index": predicted_index,
                    "predicted_label": class_names[predicted_index],
                    "confidence": float(confidences[position]),
                    "correct": actual_index == predicted_index,
                }
                for class_index, class_name in enumerate(class_names):
                    row[f"probability_{class_name}"] = float(probabilities[position, class_index])
                prediction_rows.append(row)

    metrics, matrix = calculate_metrics(actual, predicted, class_names)
    metrics["checkpoint"] = str(args.checkpoint.resolve())
    metrics["checkpoint_epoch"] = checkpoint.get("epoch")
    metrics["model_version"] = checkpoint.get("model_version")
    write_metrics(metrics, output_dir / "metrics.json")
    write_confusion_matrix_csv(matrix, class_names, output_dir / "confusion_matrix.csv")
    write_confusion_matrix_plot(matrix, class_names, output_dir / "confusion_matrix.png")

    if prediction_rows:
        with (output_dir / "predictions.csv").open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(prediction_rows[0]))
            writer.writeheader()
            writer.writerows(prediction_rows)

    print(json.dumps(metrics, indent=2))
    print(f"Evaluation artifacts written to {output_dir}")
    return metrics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate MobileNetV2 on the held-out test set")
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed/tomato_5class"))
    parser.add_argument("--output-dir", type=Path, default=Path("models/evaluation/baseline"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser


def main(arguments: list[str] | None = None) -> int:
    evaluate(build_parser().parse_args(arguments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
