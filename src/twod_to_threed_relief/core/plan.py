from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from twod_to_threed_relief.core.imageproc import build_heightmap
from twod_to_threed_relief.core.models import FilamentProfile, PlanSettings, SwapPlan, SwapStep
from twod_to_threed_relief.core.palette import auto_palette
from twod_to_threed_relief.core.tdblend import estimate_blend_layers


def _cmd(style: str) -> str | None:
    return {"m600": "M600", "m0": "M0", "m25": "M25", "none": None}[style]


def build_swap_plan(
    image: Image.Image,
    settings: PlanSettings,
    palette: list[str] | None = None,
    filaments: list[FilamentProfile] | None = None,
) -> SwapPlan:
    if not palette:
        palette = auto_palette(image, settings.colors, settings.palette_method, settings.seed)
    if not filaments:
        filaments = [
            FilamentProfile(name=f"Color {i+1}", color_hex=hex_c, td_mm=0.8)
            for i, hex_c in enumerate(palette)
        ]

    hm = build_heightmap(image, mesh_x=256, mesh_y=256)
    steps: list[SwapStep] = []
    if settings.strategy == "bands":
        levels = np.quantile(hm, np.linspace(0, 1, settings.swap_count + 2)[1:-1])
        for i, lv in enumerate(levels, 1):
            h_mm = settings.min_mm + lv * (settings.max_mm - settings.min_mm)
            layer = int(round(h_mm / settings.layer_height))
            steps.append(
                SwapStep(
                    index=i,
                    height_mm=float(h_mm),
                    layer=layer,
                    filament=filaments[min(i - 1, len(filaments) - 1)].name,
                    command=_cmd(settings.gcode_style),
                )
            )
    elif settings.strategy == "quantize":
        for i in range(1, settings.swap_count + 1):
            ratio = i / (settings.swap_count + 1)
            h_mm = settings.min_mm + ratio * (settings.max_mm - settings.min_mm)
            steps.append(
                SwapStep(
                    index=i,
                    height_mm=float(h_mm),
                    layer=int(round(h_mm / settings.layer_height)),
                    filament=filaments[min(i - 1, len(filaments) - 1)].name,
                    command=_cmd(settings.gcode_style),
                )
            )
    else:
        td = [f.td_mm for f in filaments]
        blend = estimate_blend_layers(hm, td, settings.swap_count)
        uniq = sorted(int(v) for v in np.unique(blend) if v > 0)[: settings.swap_count]
        for i, v in enumerate(uniq, 1):
            ratio = v / settings.swap_count
            h_mm = settings.min_mm + ratio * (settings.max_mm - settings.min_mm)
            steps.append(
                SwapStep(
                    index=i,
                    height_mm=float(h_mm),
                    layer=int(round(h_mm / settings.layer_height)),
                    filament=filaments[min(i - 1, len(filaments) - 1)].name,
                    command=_cmd(settings.gcode_style),
                )
            )

    notes = [
        f"Slicer target: {settings.slicer}",
        "Use planned swap heights in slicer layer-change UI.",
        "TD blend is approximate and intended for planning only.",
    ]

    return SwapPlan(
        strategy=settings.strategy,
        layer_height=settings.layer_height,
        settings=settings.model_dump(),
        palette=palette,
        filaments=filaments,
        steps=steps,
        notes=notes,
    )


def preview_plan_image(image: Image.Image, plan: SwapPlan, scale: float = 0.5) -> Image.Image:
    img = image.convert("RGB")
    w, h = img.size
    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    arr = np.asarray(img, dtype=np.uint8).copy()
    band_h = max(1, arr.shape[0] // (len(plan.steps) + 1))
    for i, step in enumerate(plan.steps):
        y = min(arr.shape[0] - 1, (i + 1) * band_h)
        arr[y : y + 2, :, :] = (255, 255, 255)
    return Image.fromarray(arr)


def plan_to_text(plan: SwapPlan) -> str:
    lines = ["2D→3D Relief Swap Plan", f"Strategy: {plan.strategy}", ""]
    lines.append("Idx | Layer | Height(mm) | Filament | Command")
    lines.append("----|-------|------------|----------|--------")
    for s in plan.steps:
        lines.append(f"{s.index:>3} | {s.layer:>5} | {s.height_mm:>10.3f} | {s.filament} | {s.command or '-'}")
    lines.append("")
    lines.extend(plan.notes)
    return "\n".join(lines)


def slicer_guide(slicer: str, gcode_style: str) -> str:
    cmd = {"m600": "M600", "m0": "M0", "m25": "M25", "none": "(none)"}[gcode_style]
    return (
        f"{slicer.title()} guide:\n"
        "1) Open print settings and layer preview.\n"
        "2) Add pauses at planned layers/heights.\n"
        f"3) Pause command: {cmd}.\n"
        "4) Resume print after filament swap and purge."
    )


def export_snippet(path: str | Path, plan: SwapPlan) -> None:
    lines = ["; swap snippet"]
    for s in plan.steps:
        if s.command:
            lines.extend([f"; Layer {s.layer}", s.command])
    Path(path).write_text("\n".join(lines) + "\n")
