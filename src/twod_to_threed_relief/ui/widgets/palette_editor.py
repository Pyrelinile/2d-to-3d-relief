from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget


class PaletteEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.row = QHBoxLayout()
        self.input = QLineEdit("#111111,#666666,#BBBBBB,#FFFFFF")
        self.add_btn = QPushButton("Add #")
        self.row.addWidget(self.input)
        self.row.addWidget(self.add_btn)
        self.layout.addLayout(self.row)
        self.add_btn.clicked.connect(self._add_color)

    def _add_color(self) -> None:
        val = self.input.text().strip()
        self.input.setText(f"{val},#000000" if val else "#000000")

    def palette_value(self) -> str:
        return self.input.text().strip()
