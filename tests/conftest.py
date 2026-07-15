from __future__ import annotations

from collections.abc import Iterator

import pytest

from src.database.repository import ClassificationRepository
from src.utils.config import AppConfig, load_config


@pytest.fixture
def app_config() -> AppConfig:
    return load_config("config/config.yaml")


@pytest.fixture
def repository(tmp_path) -> Iterator[ClassificationRepository]:
    instance = ClassificationRepository(tmp_path / "test.db")
    instance.create_schema()
    yield instance
    instance.close()
