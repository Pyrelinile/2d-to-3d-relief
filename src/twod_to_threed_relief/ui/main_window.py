from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThreadPool
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QProgressBar,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from twod_to_threed_relief.core.models import PlanSettings, ReliefSettings
from twod_to_threed_relief.ui.widgets.calibration_wizard import CalibrationWizard
from twod_to_threed_relief.ui.widgets.filament_editor import FilamentEditor
from twod_to_threed_relief.ui.widgets.image_viewer import ImageViewer
from twod_to_threed_relief.ui.widgets.palette_editor import PaletteEditor
from twod_to_threed_relief.ui.widgets.slicer_guide import SlicerGuideWidget
from twod_to_threed_relief.ui.widgets.swap_table import SwapTable
from twod_to_threed_relief.ui.workers import PipelineWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("2D→3D Relief Studio")
        self.resize(1400, 820)
        self.settings = QSettings("2d-to-3d-relief", "studio")
        self.thread_pool = QThreadPool.globalInstance()
        self.image_path = ""

        central = QWidget()
        root = QHBoxLayout(central)

        left = self._build_project_panel()
        center = self._build_center_preview()
        right = self._build_outputs_panel()

        root.addWidget(left, 2)
        root.addWidget(center, 3)
        root.addWidget(right, 3)
        self.setCentralWidget(central)

        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.setAcceptDrops(True)
        self._load_settings()

    def _build_project_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        self.input_edit = QLineEdit()
        self.output_edit = QLineEdit(str(Path.cwd() / "output"))
        browse_btn = QPushButton("Open Image")
        browse_btn.clicked.connect(self.open_image)
        run_btn = QPushButton("Run Pipeline")
        run_btn.clicked.connect(self.run_pipeline)

        self.width_mm = QDoubleSpinBox(); self.width_mm.setValue(120.0); self.width_mm.setMaximum(1000)
        self.min_mm = QDoubleSpinBox(); self.min_mm.setValue(0.8)
        self.max_mm = QDoubleSpinBox(); self.max_mm.setValue(3.2)
        self.gamma = QDoubleSpinBox(); self.gamma.setValue(1.0); self.gamma.setSingleStep(0.1)
        self.blur = QDoubleSpinBox(); self.blur.setValue(0.0); self.blur.setSingleStep(0.2)
        self.mesh_res = QSpinBox(); self.mesh_res.setRange(32, 2048); self.mesh_res.setValue(256)

        self.strategy = QComboBox(); self.strategy.addItems(["bands", "quantize", "tdblend"])
        self.slicer = QComboBox(); self.slicer.addItems(["generic", "prusaslicer", "cura", "bambu", "orcaslicer"])
        self.gcode = QComboBox(); self.gcode.addItems(["none", "m600", "m0", "m25"])
        self.layer_height = QDoubleSpinBox(); self.layer_height.setValue(0.2)
        self.swap_count = QSpinBox(); self.swap_count.setValue(6)

        form.addRow("Input", self.input_edit)
        form.addRow("Output dir", self.output_edit)
        form.addRow("Width (mm)", self.width_mm)
        form.addRow("Min (mm)", self.min_mm)
        form.addRow("Max (mm)", self.max_mm)
        form.addRow("Gamma", self.gamma)
        form.addRow("Blur", self.blur)
        form.addRow("Mesh res", self.mesh_res)
        form.addRow("Strategy", self.strategy)
        form.addRow("Layer height", self.layer_height)
        form.addRow("Swap count", self.swap_count)
        form.addRow("Slicer", self.slicer)
        form.addRow("Gcode style", self.gcode)

        layout.addLayout(form)
        self.palette_editor = PaletteEditor()
        self.filament_editor = FilamentEditor()
        layout.addWidget(self.palette_editor)
        layout.addWidget(self.filament_editor)
        layout.addWidget(browse_btn)
        layout.addWidget(run_btn)

        cal = QAction("Calibration Wizard", self)
        cal.triggered.connect(lambda: CalibrationWizard().exec())
        self.menuBar().addAction(cal)

        return widget

    def _build_center_preview(self) -> QWidget:
        tabs = QTabWidget()
        self.original_view = ImageViewer(); tabs.addTab(self.original_view, "Original")
        self.heightmap_view = ImageViewer(); tabs.addTab(self.heightmap_view, "Heightmap")
        self.palette_view = ImageViewer(); tabs.addTab(self.palette_view, "Palette/Quantized")
        self.pred_view = ImageViewer(); tabs.addTab(self.pred_view, "Predicted Preview")
        return tabs

    def _build_outputs_panel(self) -> QWidget:
        panel = QWidget(); layout = QVBoxLayout(panel)
        self.swap_table = SwapTable()
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        self.guide = SlicerGuideWidget()
        export_stl = QPushButton("Export STL")
        export_json = QPushButton("Export swap plan JSON/TXT")
        export_png = QPushButton("Export preview PNGs")
        export_stl.clicked.connect(lambda: self._log("STL exported by pipeline run"))
        export_json.clicked.connect(lambda: self._log("Plan exported by pipeline run"))
        export_png.clicked.connect(lambda: self._log("Preview exported by pipeline run"))
        layout.addWidget(self.swap_table)
        layout.addWidget(self.guide)
        layout.addWidget(export_stl)
        layout.addWidget(export_json)
        layout.addWidget(export_png)
        layout.addWidget(self.log)
        return panel

    def dragEnterEvent(self, event) -> None:  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # type: ignore[override]
        urls = event.mimeData().urls()
        if urls:
            self.image_path = urls[0].toLocalFile()
            self.input_edit.setText(self.image_path)
            self.original_view.set_image(self.image_path)

    def open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.image_path = path
            self.input_edit.setText(path)
            self.original_view.set_image(path)
            self._log(f"Loaded {path}")

    def _relief_settings(self) -> ReliefSettings:
        return ReliefSettings(
            width_mm=self.width_mm.value(),
            min_mm=self.min_mm.value(),
            max_mm=self.max_mm.value(),
            gamma=self.gamma.value(),
            blur=self.blur.value(),
            mesh_res=self.mesh_res.value(),
        )

    def _plan_settings(self) -> PlanSettings:
        return PlanSettings(
            strategy=self.strategy.currentText(),
            layer_height=self.layer_height.value(),
            swap_count=self.swap_count.value(),
            min_mm=self.min_mm.value(),
            max_mm=self.max_mm.value(),
            slicer=self.slicer.currentText(),
            gcode_style=self.gcode.currentText(),
        )

    def run_pipeline(self) -> None:
        image = self.input_edit.text().strip()
        if not image:
            QMessageBox.warning(self, "Missing input", "Please open an image first.")
            return
        out = self.output_edit.text().strip() or str(Path.cwd() / "output")
        worker = PipelineWorker(image, out, self._relief_settings(), self._plan_settings(), self.palette_editor.palette_value())
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        self.thread_pool.start(worker)
        self._log("Pipeline started")

    def _on_progress(self, step: str, value: int) -> None:
        self.progress.setValue(value)
        self.statusBar().showMessage(step)

    def _on_finished(self, result: dict) -> None:
        self._log("Pipeline completed")
        self.swap_table.set_steps(result["plan"]["steps"])
        out = Path(self.output_edit.text())
        preview = out / "preview.png"
        if preview.exists():
            self.pred_view.set_image(str(preview))
        self.guide.update_guide(self.slicer.currentText(), self.gcode.currentText())
        self._save_settings()

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Pipeline error", message)
        self._log(f"Error: {message}")

    def _log(self, text: str) -> None:
        self.log.appendPlainText(text)

    def _save_settings(self) -> None:
        self.settings.setValue("input", self.input_edit.text())
        self.settings.setValue("output", self.output_edit.text())

    def _load_settings(self) -> None:
        self.input_edit.setText(self.settings.value("input", ""))
        self.output_edit.setText(self.settings.value("output", str(Path.cwd() / "output")))
