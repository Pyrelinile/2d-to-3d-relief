from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class SwapTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 4)
        self.setHorizontalHeaderLabels(["#", "Layer", "Height", "Filament"])

    def set_steps(self, steps: list[dict]) -> None:
        self.setRowCount(len(steps))
        for r, s in enumerate(steps):
            self.setItem(r, 0, QTableWidgetItem(str(s["index"])))
            self.setItem(r, 1, QTableWidgetItem(str(s["layer"])))
            self.setItem(r, 2, QTableWidgetItem(f"{s['height_mm']:.3f}"))
            self.setItem(r, 3, QTableWidgetItem(s["filament"]))
