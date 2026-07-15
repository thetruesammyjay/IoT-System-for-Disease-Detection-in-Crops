"""Train a five-class MobileNetV2 and retain the best validation checkpoint."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import precision_recall_fscore_support
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

from models.training.dataset import ManifestDataset
from models.training.modeling import (
    build_mobilenet_v2,
    evaluation_transform,
    select_device,
    set_reproducible_seed,
    training_transform,
)


def _class_weights(targets: list[int], class_count: int, device: torch.device) -> torch.Tensor:
    counts = Counter(targets)
    if any(counts[index] == 0 for index in range(class_count)):
        raise ValueError("Every class must have at least one training image")
    sample_count = len(targets)
    values = [sample_count / (class_count * counts[index]) for index in range(class_count)]
    return torch.tensor(values, dtype=torch.float32, device=device)


def _run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: AdamW | None = None,
) -> dict[str, float]:
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    actual: list[int] = []
    predicted: list[int] = []

    for images, targets, _ in loader:
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)
        if training:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(training):
            logits = model(images)
            loss = criterion(logits, targets)
            if training:
                loss.backward()
                optimizer.step()

        total_loss += float(loss.item()) * targets.size(0)
        actual.extend(targets.detach().cpu().tolist())
        predicted.extend(torch.argmax(logits, dim=1).detach().cpu().tolist())

    _, _, macro_f1, _ = precision_recall_fscore_support(
        actual, predicted, average="macro", zero_division=0
    )
    accuracy = float(np.mean(np.asarray(actual) == np.asarray(predicted)))
    return {
        "loss": total_loss / len(loader.dataset),
        "accuracy": accuracy,
        "macro_f1_score": float(macro_f1),
    }


def _write_history(history: list[dict[str, Any]], output_dir: Path) -> None:
    (output_dir / "history.json").write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    fields = [
        "epoch",
        "train_loss",
        "train_accuracy",
        "train_macro_f1_score",
        "validation_loss",
        "validation_accuracy",
        "validation_macro_f1_score",
        "learning_rate",
    ]
    with (output_dir / "history.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(history)


def train(args: argparse.Namespace) -> Path:
    set_reproducible_seed(args.seed)
    device = select_device(args.device)
    data_dir = args.data_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    train_dataset = ManifestDataset(data_dir, "train", training_transform(args.input_size))
    validation_dataset = ManifestDataset(
        data_dir, "validation", evaluation_transform(args.input_size)
    )
    if train_dataset.classes != validation_dataset.classes:
        raise ValueError("Training and validation class orders do not match")
    class_count = len(train_dataset.classes)

    generator = torch.Generator().manual_seed(args.seed)
    common_loader_options = {
        "batch_size": args.batch_size,
        "num_workers": args.workers,
        "pin_memory": device.type == "cuda",
    }
    train_loader = DataLoader(
        train_dataset,
        shuffle=True,
        generator=generator,
        **common_loader_options,
    )
    validation_loader = DataLoader(
        validation_dataset,
        shuffle=False,
        **common_loader_options,
    )

    model = build_mobilenet_v2(class_count, pretrained=args.pretrained).to(device)
    if args.freeze_backbone_epochs > 0:
        for parameter in model.features.parameters():
            parameter.requires_grad = False

    criterion = nn.CrossEntropyLoss(
        weight=_class_weights(train_dataset.targets, class_count, device)
    )
    optimizer = AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    history: list[dict[str, Any]] = []
    best_macro_f1 = -1.0
    best_validation_loss = float("inf")
    epochs_without_improvement = 0
    checkpoint_path = output_dir / "best_model.pt"

    print(f"Training on {device} with {len(train_dataset)} training images")
    for epoch in range(1, args.epochs + 1):
        if epoch == args.freeze_backbone_epochs + 1 and args.freeze_backbone_epochs > 0:
            for parameter in model.features.parameters():
                parameter.requires_grad = True
            optimizer = AdamW(
                model.parameters(),
                lr=args.learning_rate * args.finetune_learning_rate_factor,
                weight_decay=args.weight_decay,
            )

        train_metrics = _run_epoch(model, train_loader, criterion, device, optimizer)
        validation_metrics = _run_epoch(model, validation_loader, criterion, device)
        row = {
            "epoch": epoch,
            "train_loss": train_metrics["loss"],
            "train_accuracy": train_metrics["accuracy"],
            "train_macro_f1_score": train_metrics["macro_f1_score"],
            "validation_loss": validation_metrics["loss"],
            "validation_accuracy": validation_metrics["accuracy"],
            "validation_macro_f1_score": validation_metrics["macro_f1_score"],
            "learning_rate": optimizer.param_groups[0]["lr"],
        }
        history.append(row)
        _write_history(history, output_dir)
        print(json.dumps(row))

        macro_f1 = validation_metrics["macro_f1_score"]
        validation_loss = validation_metrics["loss"]
        improved = macro_f1 > best_macro_f1 or (
            macro_f1 == best_macro_f1 and validation_loss < best_validation_loss
        )
        if improved:
            best_macro_f1 = macro_f1
            best_validation_loss = validation_loss
            epochs_without_improvement = 0
            torch.save(
                {
                    "architecture": "mobilenet_v2",
                    "model_state_dict": model.state_dict(),
                    "classes": train_dataset.classes,
                    "class_to_index": train_dataset.class_to_index,
                    "input_size": args.input_size,
                    "epoch": epoch,
                    "validation_metrics": validation_metrics,
                    "seed": args.seed,
                    "pretrained": args.pretrained,
                    "model_version": args.model_version,
                },
                checkpoint_path,
            )
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= args.early_stopping_patience:
            print(f"Early stopping after epoch {epoch}")
            break

    print(f"Best checkpoint written to {checkpoint_path}")
    return checkpoint_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train the five-class MobileNetV2 model")
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed/tomato_5class"))
    parser.add_argument("--output-dir", type=Path, default=Path("models/training/runs/baseline"))
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--freeze-backbone-epochs", type=int, default=3)
    parser.add_argument("--finetune-learning-rate-factor", type=float, default=0.1)
    parser.add_argument("--early-stopping-patience", type=int, default=7)
    parser.add_argument("--input-size", type=int, default=224)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--pretrained", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--model-version", default="tomato-mobilenetv2-v1")
    return parser


def main(arguments: list[str] | None = None) -> int:
    train(build_parser().parse_args(arguments))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
