from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWizard, QWizardPage


class CalibrationWizard(QWizard):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Calibration Wizard")
        page1 = QWizardPage()
        page1.setTitle("Print Step Tower")
        l1 = QVBoxLayout(page1)
        l1.addWidget(QLabel("Print thickness steps 0.2mm to 2.0mm and record first opaque thickness."))
        page2 = QWizardPage()
        page2.setTitle("Update TD Profile")
        l2 = QVBoxLayout(page2)
        l2.addWidget(QLabel("Set td_mm values in filament profile YAML and reload in app."))
        self.addPage(page1)
        self.addPage(page2)
