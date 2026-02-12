from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress

from twod_to_threed_relief.core.config import load_config
from twod_to_threed_relief.core.imageproc import build_heightmap, heightmap_to_image, load_image, map_height_range
from twod_to_threed_relief.core.io import ensure_dir, load_filaments, write_swap_plan, write_text
from twod_to_threed_relief.core.mesh import build_relief_mesh, write_binary_stl
from twod_to_threed_relief.core.models import PlanSettings, ReliefSettings
from twod_to_threed_relief.core.palette import auto_palette, load_palette
from twod_to_threed_relief.core.plan import build_swap_plan, export_snippet, plan_to_text, preview_plan_image

app = typer.Typer(help="2D→3D Relief Studio CLI")
console = Console()


def _mesh_dims(img_size: tuple[int, int], settings: ReliefSettings) -> tuple[int, int, float]:
    mx = settings.mesh_x or settings.mesh_res
    my = settings.mesh_y or settings.mesh_res
    ratio = img_size[1] / img_size[0]
    h_mm = settings.height_mm or settings.width_mm * ratio
    return mx, my, h_mm


@app.command("relief")
def relief_cmd(
    input: Annotated[Path, typer.Option("--input", exists=True)],
    output: Annotated[Path, typer.Option("--output")],
    width_mm: float = 120.0,
    height_mm: float | None = None,
    min_mm: float = 0.8,
    max_mm: float = 3.2,
    gamma: float = 1.0,
    invert: bool = False,
    blur: float = 0.0,
    dither: bool = False,
    mesh_res: int = 256,
    mesh_x: int | None = None,
    mesh_y: int | None = None,
    smooth: int = 0,
    export_heightmap: Path | None = typer.Option(None, "--export-heightmap"),
) -> None:
    settings = ReliefSettings(
        width_mm=width_mm,
        height_mm=height_mm,
        min_mm=min_mm,
        max_mm=max_mm,
        gamma=gamma,
        invert=invert,
        blur=blur,
        dither=dither,
        mesh_res=mesh_res,
        mesh_x=mesh_x,
        mesh_y=mesh_y,
        smooth=smooth,
    )
    image = load_image(str(input))
    mx, my, hm = _mesh_dims(image.size, settings)
    with Progress() as progress:
        task = progress.add_task("Generating relief", total=3)
        hmap = build_heightmap(image, gamma=gamma, invert=invert, blur=blur, mesh_x=mx, mesh_y=my)
        progress.advance(task)
        th = map_height_range(hmap, min_mm=min_mm, max_mm=max_mm)
        tris = build_relief_mesh(th, width_mm=width_mm, height_mm=hm, min_mm=min_mm)
        progress.advance(task)
        write_binary_stl(output, tris)
        progress.advance(task)
    if export_heightmap:
        heightmap_to_image(hmap).save(export_heightmap)
    console.print(f"[green]STL written:[/green] {output}")


@app.command("plan")
def plan_cmd(
    input: Annotated[Path, typer.Option("--input", exists=True)],
    output_dir: Annotated[Path, typer.Option("--output-dir")],
    palette: str | None = None,
    auto_palette_n: int | None = typer.Option(None, "--auto-palette"),
    colors: int = 4,
    palette_method: str = "kmeans",
    strategy: str = "bands",
    layer_height: float = 0.2,
    swap_count: int = 6,
    min_mm: float = 0.8,
    max_mm: float = 3.2,
    filaments: Path | None = None,
    slicer: str = "generic",
    gcode_style: str = "none",
    seed: int = 42,
    preview_scale: float = 0.5,
) -> None:
    out = ensure_dir(output_dir)
    image = load_image(str(input))
    pal = load_palette(palette) if palette else None
    if auto_palette_n:
        pal = auto_palette(image, auto_palette_n, palette_method, seed)
    filament_list = load_filaments(filaments) if filaments else None
    settings = PlanSettings(
        strategy=strategy,
        layer_height=layer_height,
        swap_count=swap_count,
        min_mm=min_mm,
        max_mm=max_mm,
        colors=colors,
        palette_method=palette_method,
        slicer=slicer,
        gcode_style=gcode_style,
        seed=seed,
        preview_scale=preview_scale,
    )
    plan = build_swap_plan(image, settings=settings, palette=pal, filaments=filament_list)
    write_swap_plan(out / "swap_plan.json", plan)
    write_text(out / "swap_plan.txt", plan_to_text(plan))
    preview_plan_image(image, plan, scale=preview_scale).save(out / "preview.png")
    if gcode_style != "none":
        export_snippet(out / "swap_snippets.gcode", plan)
    console.print(f"[green]Plan outputs written:[/green] {out}")


@app.command("pipeline")
def pipeline_cmd(
    input: Path = typer.Option(..., "--input"),
    output_dir: Path = typer.Option(..., "--output-dir"),
    config: Path | None = typer.Option(None, "--config"),
    width_mm: float | None = None,
) -> None:
    cfg = load_config(config) if config else None
    in_path = input if input else cfg.input
    out_dir = output_dir if output_dir else cfg.output_dir
    ensure_dir(out_dir)
    relief_args = cfg.relief.model_dump() if cfg else ReliefSettings().model_dump()
    if width_mm is not None:
        relief_args["width_mm"] = width_mm
    relief_cmd(input=in_path, output=out_dir / "relief.stl", **relief_args)
    plan_args = cfg.plan.model_dump() if cfg else PlanSettings().model_dump()
    plan_cmd(input=in_path, output_dir=out_dir, **plan_args)


@app.command("calibrate")
def calibrate_cmd(output_dir: Path = typer.Option(Path("calibration"), "--output-dir")) -> None:
    out = ensure_dir(output_dir)
    content = (
        "Calibration workflow:\n"
        "1) Print thickness steps from 0.2 to 2.0mm.\n"
        "2) Measure first opaque thickness for each filament.\n"
        "3) Save td_mm per filament in YAML profile."
    )
    write_text(out / "calibration_steps.txt", content)
    write_text(
        out / "filaments_template.yaml",
        "filaments:\n  - name: Sample\n    color_hex: '#FFFFFF'\n    td_mm: 0.8\n    notes: measured\n",
    )
    console.print(f"[green]Calibration assets written:[/green] {out}")


@app.command("inspect")
def inspect_cmd(
    input: Path | None = typer.Option(None, "--input"),
    filaments: Path | None = None,
    palette: str | None = None,
) -> None:
    if input:
        image = load_image(str(input))
        console.print(f"Image size: {image.size[0]}x{image.size[1]}")
    if filaments:
        items = load_filaments(filaments)
        console.print(f"Filaments: {len(items)}")
    if palette:
        pal = load_palette(palette)
        console.print(f"Palette entries: {len(pal)}")


if __name__ == "__main__":
    app()
