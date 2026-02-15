# 2d-to-3d-relief

**2D→3D Relief Studio** — *Image-to-Flat 3D Relief + Layer Swap Planner (HueForge-lite, but not annoying)*

## Overview
`2d-to-3d-relief` is an offline-first Python toolkit for turning images into flat bas-relief STL models and producing multi-filament layer swap plans for common slicers.

## Install
### CLI only
```bash
pip install -e .
```

### CLI + GUI
```bash
pip install -e ".[gui]"
```

### pipx (recommended)
```bash
pipx install .
```

## CLI quickstart
```bash
relief relief --input image.jpg --output relief.stl --width-mm 120 --min-mm 0.8 --max-mm 3.2
relief plan --input image.jpg --output-dir out --auto-palette 4 --strategy bands --gcode-style m600
relief pipeline --input image.jpg --output-dir out
relief calibrate --output-dir calibration
relief inspect --input image.jpg --palette "#111111,#777777,#ffffff"
```

## GUI quickstart
```bash
relief-gui
```
In the GUI:
1. Open/drag image.
2. Tune relief + planning settings.
3. Run Pipeline (threaded, non-blocking).
4. Export generated artifacts.

## Filament TD explanation + calibration workflow
TD (transmission distance) models how quickly light attenuates through filament. Lower TD means faster opacity.
- Print a thickness step test.
- Record first visually opaque thickness.
- Save as `td_mm` in filament profile YAML.
- Use `tdblend` strategy to approximate stacked appearance.

## Slicer notes
- **PrusaSlicer / OrcaSlicer / Bambu Studio / Cura**: add layer-change pauses at planned layers or heights.
- Optional snippet commands:
  - `M600` filament change
  - `M0` pause
  - `M25` pause SD
- The app outputs generic instructions, not slicer project files.

## Troubleshooting
- If mesh export seems coarse, increase `--mesh-res` or `--mesh-x/--mesh-y`.
- If colors look wrong, adjust gamma/invert and try `--strategy quantize`.
- If GUI import fails, ensure `pip install -e ".[gui]"` and working Qt backend.
- For reproducible palette extraction, set `--seed`.

## Project layout
See `docs/` and `examples/` for deeper references.
