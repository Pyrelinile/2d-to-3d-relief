from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget


class FilamentEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Color Hex", "td_mm", "Notes"])
        defaults = [
            ("Black PLA", "#111111", "0.65", "high opacity"),
            ("Blue PLA", "#1B5EAA", "0.75", "mid"),
            ("Orange PLA", "#E67E22", "0.85", "mid"),
            ("White PLA", "#F2F2F2", "1.05", "low opacity"),
        ]
        for r, row in enumerate(defaults):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))
        layout.addWidget(self.table)
