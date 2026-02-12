from __future__ import annotations

from pathlib import Path

from twod_to_threed_relief.core.io import read_data
from twod_to_threed_relief.core.models import PipelineConfig


def load_config(path: str | Path) -> PipelineConfig:
    data = read_data(path)
    return PipelineConfig(**data)
