"""PyTorch dataset backed by preparation manifests."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from PIL import Image


class ManifestDataset:
    """Load images and labels from one generated split manifest."""

    def __init__(self, data_dir: str | Path, split: str, transform: Any = None) -> None:
        self.data_dir = Path(data_dir).resolve()
        metadata_path = self.data_dir / "metadata.json"
        manifest_path = self.data_dir / f"{split}.csv"
        if not metadata_path.is_file() or not manifest_path.is_file():
            raise FileNotFoundError(
                f"Prepared metadata or {split} manifest is missing from {self.data_dir}"
            )

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.dataset_root = Path(metadata["dataset_root"]).resolve()
        self.classes = [item["label"] for item in metadata["classes"]]
        self.class_to_index = {item["label"]: int(item["index"]) for item in metadata["classes"]}
        self.transform = transform
        with manifest_path.open("r", encoding="utf-8", newline="") as source:
            self.records = list(csv.DictReader(source))
        if not self.records:
            raise ValueError(f"The {split} manifest contains no images")
        self.targets = [int(record["class_index"]) for record in self.records]

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> tuple[Any, int, str]:
        record = self.records[index]
        image_path = (self.dataset_root / record["image_path"]).resolve()
        if not image_path.is_relative_to(self.dataset_root):
            raise ValueError(f"Manifest path escapes the dataset root: {image_path}")
        with Image.open(image_path) as source:
            image = source.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, int(record["class_index"]), record["image_path"]
