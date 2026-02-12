from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from twod_to_threed_relief.core.models import FilamentProfile, SwapPlan


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_data(path: str | Path) -> Any:
    p = Path(path)
    text = p.read_text()
    if p.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def load_filaments(path: str | Path) -> list[FilamentProfile]:
    data = read_data(path)
    if isinstance(data, dict) and "filaments" in data:
        data = data["filaments"]
    return [FilamentProfile(**item) for item in data]


def write_json(path: str | Path, data: dict) -> None:
    Path(path).write_text(json.dumps(data, indent=2))


def write_text(path: str | Path, text: str) -> None:
    Path(path).write_text(text)


def write_swap_plan(path: str | Path, plan: SwapPlan) -> None:
    write_json(path, plan.model_dump())
