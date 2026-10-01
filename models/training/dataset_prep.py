"""Validate PlantVillage images and create reproducible stratified split manifests."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from src.domain import DiseaseClass
from src.utils.config import load_config

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
SPLIT_NAMES = ("train", "validation", "test")


class DatasetPreparationError(ValueError):
    """Raised when the source dataset cannot satisfy the project contract."""


@dataclass(frozen=True, slots=True)
class ImageRecord:
    image_path: str
    class_index: int
    class_label: str
    dataset_label: str
    split: str
    sha256: str


def _find_class_directory(dataset_root: Path, dataset_label: str) -> Path:
    matches = sorted(
        path
        for path in dataset_root.rglob(dataset_label)
        if path.is_dir() and path.name == dataset_label
    )
    if not matches:
        raise DatasetPreparationError(
            f"Could not find PlantVillage class directory {dataset_label!r} under {dataset_root}"
        )
    if len(matches) > 1:
        locations = ", ".join(str(path) for path in matches)
        raise DatasetPreparationError(
            f"Found multiple directories for {dataset_label!r}: {locations}. "
            "Use a more specific --dataset-root."
        )
    return matches[0]


def _inspect_image(path: Path) -> tuple[str, tuple[int, int]]:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)

    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        width, height = image.size
    if width < 32 or height < 32:
        raise DatasetPreparationError("image dimensions are smaller than 32 x 32")
    return digest.hexdigest(), (width, height)


def _split_images(
    images: list[tuple[Path, str]],
    disease: DiseaseClass,
    dataset_root: Path,
    train_ratio: float,
    validation_ratio: float,
    test_ratio: float,
    seed: int,
) -> list[ImageRecord]:
    if len(images) < 3:
        raise DatasetPreparationError(
            f"{disease.dataset_label} needs at least three valid unique images"
        )

    shuffled = sorted(images, key=lambda item: item[0].as_posix().lower())
    random.Random(seed + disease.index).shuffle(shuffled)

    validation_count = max(1, int(len(shuffled) * validation_ratio))
    test_count = max(1, int(len(shuffled) * test_ratio))
    train_count = len(shuffled) - validation_count - test_count
    if train_count < 1:
        raise DatasetPreparationError(f"Split ratios leave no training images for {disease.label}")

    boundaries = (train_count, train_count + validation_count)
    split_for_position = (
        ["train"] * boundaries[0] + ["validation"] * validation_count + ["test"] * test_count
    )
    if len(split_for_position) != len(shuffled):
        raise DatasetPreparationError("Internal split calculation failed")

    return [
        ImageRecord(
            image_path=path.relative_to(dataset_root).as_posix(),
            class_index=disease.index,
            class_label=disease.label,
            dataset_label=disease.dataset_label,
            split=split_for_position[position],
            sha256=digest,
        )
        for position, (path, digest) in enumerate(shuffled)
    ]


def _write_manifest(path: Path, records: list[ImageRecord]) -> None:
    fields = ["image_path", "class_index", "class_label", "dataset_label", "split", "sha256"]
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def prepare_dataset(
    dataset_root: Path,
    output_dir: Path,
    diseases: tuple[DiseaseClass, ...],
    seed: int = 42,
    train_ratio: float = 0.80,
    validation_ratio: float = 0.10,
    test_ratio: float = 0.10,
) -> dict[str, object]:
    """Create class-stratified manifests without copying source images."""

    dataset_root = dataset_root.resolve()
    output_dir = output_dir.resolve()
    if not dataset_root.is_dir():
        raise DatasetPreparationError(f"Dataset root does not exist: {dataset_root}")
    if any(ratio <= 0 for ratio in (train_ratio, validation_ratio, test_ratio)):
        raise DatasetPreparationError("All split ratios must be greater than zero")
    if abs(train_ratio + validation_ratio + test_ratio - 1.0) > 1e-9:
        raise DatasetPreparationError("Train, validation, and test ratios must sum to 1.0")

    records: list[ImageRecord] = []
    seen_hashes: dict[str, tuple[Path, int]] = {}
    invalid_images: list[dict[str, str]] = []
    duplicate_images: list[dict[str, str]] = []

    for disease in diseases:
        class_directory = _find_class_directory(dataset_root, disease.dataset_label)
        valid_images: list[tuple[Path, str]] = []
        candidates = sorted(
            path
            for path in class_directory.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        for image_path in candidates:
            try:
                digest, _ = _inspect_image(image_path)
            except (OSError, UnidentifiedImageError, DatasetPreparationError) as exc:
                invalid_images.append(
                    {"image_path": str(image_path), "reason": str(exc), "class": disease.label}
                )
                continue

            previous = seen_hashes.get(digest)
            if previous is not None:
                previous_path, previous_class = previous
                if previous_class != disease.index:
                    raise DatasetPreparationError(
                        "The same image content appears under two disease labels: "
                        f"{previous_path} and {image_path}"
                    )
                duplicate_images.append(
                    {
                        "image_path": str(image_path),
                        "duplicate_of": str(previous_path),
                        "class": disease.label,
                    }
                )
                continue

            seen_hashes[digest] = (image_path, disease.index)
            valid_images.append((image_path, digest))

        records.extend(
            _split_images(
                valid_images,
                disease,
                dataset_root,
                train_ratio,
                validation_ratio,
                test_ratio,
                seed,
            )
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    split_counts: dict[str, dict[str, int]] = {}
    for split in SPLIT_NAMES:
        split_records = [record for record in records if record.split == split]
        split_records.sort(key=lambda record: (record.class_index, record.image_path))
        _write_manifest(output_dir / f"{split}.csv", split_records)
        split_counts[split] = {
            disease.label: sum(record.class_index == disease.index for record in split_records)
            for disease in diseases
        }

    class_to_index = {disease.label: disease.index for disease in diseases}
    (output_dir / "class_to_index.json").write_text(
        json.dumps(class_to_index, indent=2) + "\n", encoding="utf-8"
    )

    metadata: dict[str, object] = {
        "dataset_root": str(dataset_root),
        "seed": seed,
        "ratios": {
            "train": train_ratio,
            "validation": validation_ratio,
            "test": test_ratio,
        },
        "classes": [asdict(disease) for disease in diseases],
        "split_counts": split_counts,
        "valid_unique_images": len(records),
        "invalid_images": invalid_images,
        "duplicate_images_removed": duplicate_images,
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare configured PlantVillage tomato classes for reproducible training"
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/tomato_5class"))
    parser.add_argument("--config", type=Path, default=Path("config/config.yaml"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.80)
    parser.add_argument("--validation-ratio", type=float, default=0.10)
    parser.add_argument("--test-ratio", type=float, default=0.10)
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    config = load_config(args.config)
    try:
        metadata = prepare_dataset(
            dataset_root=args.dataset_root,
            output_dir=args.output_dir,
            diseases=config.diseases,
            seed=args.seed,
            train_ratio=args.train_ratio,
            validation_ratio=args.validation_ratio,
            test_ratio=args.test_ratio,
        )
    except DatasetPreparationError as exc:
        raise SystemExit(f"dataset preparation failed: {exc}") from exc

    print(json.dumps(metadata["split_counts"], indent=2))
    print(f"Manifests written to {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
