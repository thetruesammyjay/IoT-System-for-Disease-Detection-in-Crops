from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from models.training.dataset_prep import prepare_dataset
from src.utils.config import AppConfig


def _create_dataset(root: Path, app_config: AppConfig, images_per_class: int = 10) -> None:
    for disease in app_config.diseases:
        class_directory = root / "color" / disease.dataset_label
        class_directory.mkdir(parents=True)
        for image_index in range(images_per_class):
            color = (
                20 + disease.index * 30,
                40 + image_index * 10,
                60 + disease.index * 10 + image_index,
            )
            Image.new("RGB", (64, 64), color=color).save(
                class_directory / f"image_{image_index:02d}.png"
            )


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def test_dataset_splits_are_stratified_and_reproducible(
    tmp_path: Path, app_config: AppConfig
) -> None:
    dataset_root = tmp_path / "plantvillage"
    first_output = tmp_path / "prepared_first"
    second_output = tmp_path / "prepared_second"
    _create_dataset(dataset_root, app_config)

    first_metadata = prepare_dataset(dataset_root, first_output, app_config.diseases, seed=42)
    second_metadata = prepare_dataset(dataset_root, second_output, app_config.diseases, seed=42)

    assert first_metadata["split_counts"] == second_metadata["split_counts"]
    assert first_metadata["valid_unique_images"] == 50
    for disease in app_config.diseases:
        assert first_metadata["split_counts"]["train"][disease.label] == 8
        assert first_metadata["split_counts"]["validation"][disease.label] == 1
        assert first_metadata["split_counts"]["test"][disease.label] == 1

    for split in ("train", "validation", "test"):
        assert (first_output / f"{split}.csv").read_text(encoding="utf-8") == (
            second_output / f"{split}.csv"
        ).read_text(encoding="utf-8")

    split_hashes = {
        split: {record["sha256"] for record in _read_manifest(first_output / f"{split}.csv")}
        for split in ("train", "validation", "test")
    }
    assert split_hashes["train"].isdisjoint(split_hashes["validation"])
    assert split_hashes["train"].isdisjoint(split_hashes["test"])
    assert split_hashes["validation"].isdisjoint(split_hashes["test"])
