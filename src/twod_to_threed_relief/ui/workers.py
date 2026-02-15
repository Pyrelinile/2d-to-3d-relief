from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from twod_to_threed_relief.core.imageproc import build_heightmap, load_image, map_height_range
from twod_to_threed_relief.core.io import ensure_dir, load_filaments, write_swap_plan, write_text
from twod_to_threed_relief.core.mesh import build_relief_mesh, write_binary_stl
from twod_to_threed_relief.core.models import PlanSettings, ReliefSettings
from twod_to_threed_relief.core.palette import auto_palette, load_palette
from twod_to_threed_relief.core.plan import build_swap_plan, export_snippet, plan_to_text, preview_plan_image


class WorkerSignals(QObject):
    progress = Signal(str, int)
    finished = Signal(dict)
    error = Signal(str)


class PipelineWorker(QRunnable):
    def __init__(self, image_path: str, output_dir: str, relief: ReliefSettings, plan: PlanSettings, palette_value: str | None = None, filaments_path: str | None = None) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self.image_path = image_path
        self.output_dir = output_dir
        self.relief = relief
        self.plan = plan
        self.palette_value = palette_value
        self.filaments_path = filaments_path

    def run(self) -> None:
        try:
            out = ensure_dir(self.output_dir)
            self.signals.progress.emit("Loading image", 5)
            image = load_image(self.image_path)
            mx = self.relief.mesh_x or self.relief.mesh_res
            my = self.relief.mesh_y or self.relief.mesh_res
            ratio = image.size[1] / image.size[0]
            h_mm = self.relief.height_mm or self.relief.width_mm * ratio

            self.signals.progress.emit("Building heightmap", 20)
            hmap = build_heightmap(image, self.relief.gamma, self.relief.invert, self.relief.blur, mx, my)
            thickness = map_height_range(hmap, self.relief.min_mm, self.relief.max_mm)
            self.signals.progress.emit("Building mesh", 40)
            tris = build_relief_mesh(thickness, self.relief.width_mm, h_mm, self.relief.min_mm)
            stl_path = out / "relief.stl"
            write_binary_stl(stl_path, tris)

            self.signals.progress.emit("Planning swaps", 70)
            pal = load_palette(self.palette_value) if self.palette_value else auto_palette(image, self.plan.colors, self.plan.palette_method, self.plan.seed)
            fils = load_filaments(self.filaments_path) if self.filaments_path else None
            swap = build_swap_plan(image, self.plan, palette=pal, filaments=fils)
            write_swap_plan(out / "swap_plan.json", swap)
            write_text(out / "swap_plan.txt", plan_to_text(swap))
            preview_plan_image(image, swap, self.plan.preview_scale).save(out / "preview.png")
            if self.plan.gcode_style != "none":
                export_snippet(out / "swap_snippets.gcode", swap)
            self.signals.progress.emit("Done", 100)
            self.signals.finished.emit({"stl": str(stl_path), "plan": swap.model_dump()})
        except Exception as exc:  # noqa: BLE001
            self.signals.error.emit(str(exc))
