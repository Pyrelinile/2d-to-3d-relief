from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ReliefSettings(BaseModel):
    width_mm: float = 120.0
    height_mm: float | None = None
    min_mm: float = 0.8
    max_mm: float = 3.2
    gamma: float = 1.0
    invert: bool = False
    blur: float = 0.0
    dither: bool = False
    mesh_res: int = 256
    mesh_x: int | None = None
    mesh_y: int | None = None
    smooth: int = 0


class FilamentProfile(BaseModel):
    name: str
    color_hex: str = Field(pattern=r"^#?[0-9A-Fa-f]{6}$")
    td_mm: float = Field(gt=0)
    notes: str = ""


class PlanSettings(BaseModel):
    strategy: Literal["bands", "quantize", "tdblend"] = "bands"
    layer_height: float = 0.2
    swap_count: int = 6
    min_mm: float = 0.8
    max_mm: float = 3.2
    colors: int = 4
    palette_method: Literal["kmeans", "median-cut"] = "kmeans"
    slicer: Literal["bambu", "orcaslicer", "prusaslicer", "cura", "generic"] = "generic"
    gcode_style: Literal["m600", "m0", "m25", "none"] = "none"
    seed: int = 42
    preview_scale: float = 0.5


class SwapStep(BaseModel):
    index: int
    height_mm: float
    layer: int
    filament: str
    command: str | None = None


class SwapPlan(BaseModel):
    app: str = "2d-to-3d-relief"
    strategy: str
    layer_height: float
    settings: dict
    palette: list[str]
    filaments: list[FilamentProfile]
    steps: list[SwapStep]
    notes: list[str]


class PipelineConfig(BaseModel):
    input: Path
    output_dir: Path
    relief: ReliefSettings = ReliefSettings()
    plan: PlanSettings = PlanSettings()
