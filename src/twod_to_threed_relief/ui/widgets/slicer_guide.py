from __future__ import annotations

from PySide6.QtWidgets import QTextEdit

from twod_to_threed_relief.core.plan import slicer_guide


class SlicerGuideWidget(QTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.update_guide("generic", "none")

    def update_guide(self, slicer: str, gcode_style: str) -> None:
        self.setPlainText(slicer_guide(slicer, gcode_style))
