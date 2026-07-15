"""Classification metrics and confusion-matrix artifact generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def calculate_metrics(
    actual: list[int], predicted: list[int], class_names: list[str]
) -> tuple[dict[str, Any], np.ndarray]:
    """Calculate overall, macro, and per-class classification measurements."""

    labels = list(range(len(class_names)))
    precision, recall, f1_score, support = precision_recall_fscore_support(
        actual,
        predicted,
        labels=labels,
        average=None,
        zero_division=0,
    )
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        actual,
        predicted,
        labels=labels,
        average="macro",
        zero_division=0,
    )
    matrix = confusion_matrix(actual, predicted, labels=labels)
    metrics: dict[str, Any] = {
        "accuracy": float(accuracy_score(actual, predicted)),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1_score": float(macro_f1),
        "test_samples": len(actual),
        "per_class": {
            class_name: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1_score": float(f1_score[index]),
                "support": int(support[index]),
            }
            for index, class_name in enumerate(class_names)
        },
        "confusion_matrix": matrix.tolist(),
    }
    return metrics, matrix


def write_confusion_matrix_csv(
    matrix: np.ndarray, class_names: list[str], output_path: Path
) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["Actual / Predicted", *class_names])
        for class_name, row in zip(class_names, matrix, strict=True):
            writer.writerow([class_name, *[int(value) for value in row]])


def write_confusion_matrix_plot(
    matrix: np.ndarray, class_names: list[str], output_path: Path
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure, axis = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=class_names,
        yticklabels=class_names,
        ax=axis,
    )
    axis.set_xlabel("Predicted class")
    axis.set_ylabel("Actual class")
    axis.set_title("Five-Class Tomato Disease Confusion Matrix")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def write_metrics(metrics: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
