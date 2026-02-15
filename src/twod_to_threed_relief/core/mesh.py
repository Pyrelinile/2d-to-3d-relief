from __future__ import annotations

import struct
from pathlib import Path

import numpy as np


def _normal(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    n = np.cross(b - a, c - a)
    norm = np.linalg.norm(n)
    return n / norm if norm else np.array([0.0, 0.0, 1.0], dtype=np.float32)


def _triangles_from_grid(z: np.ndarray, width_mm: float, height_mm: float) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    h, w = z.shape
    xs = np.linspace(0, width_mm, w, dtype=np.float32)
    ys = np.linspace(0, height_mm, h, dtype=np.float32)
    tris: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for y in range(h - 1):
        for x in range(w - 1):
            p00 = np.array([xs[x], ys[y], z[y, x]], dtype=np.float32)
            p10 = np.array([xs[x + 1], ys[y], z[y, x + 1]], dtype=np.float32)
            p01 = np.array([xs[x], ys[y + 1], z[y + 1, x]], dtype=np.float32)
            p11 = np.array([xs[x + 1], ys[y + 1], z[y + 1, x + 1]], dtype=np.float32)
            tris.extend([(p00, p10, p11), (p00, p11, p01)])
    return tris


def build_relief_mesh(
    thickness: np.ndarray,
    width_mm: float,
    height_mm: float,
    min_mm: float,
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    h, w = thickness.shape
    top = _triangles_from_grid(thickness, width_mm, height_mm)
    bottom = _triangles_from_grid(np.full((h, w), min_mm, dtype=np.float32), width_mm, height_mm)
    bottom = [(c, b, a) for (a, b, c) in bottom]

    xs = np.linspace(0, width_mm, w, dtype=np.float32)
    ys = np.linspace(0, height_mm, h, dtype=np.float32)
    sides: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    for x in range(w - 1):
        t0 = np.array([xs[x], ys[0], thickness[0, x]], dtype=np.float32)
        t1 = np.array([xs[x + 1], ys[0], thickness[0, x + 1]], dtype=np.float32)
        b0 = np.array([xs[x], ys[0], min_mm], dtype=np.float32)
        b1 = np.array([xs[x + 1], ys[0], min_mm], dtype=np.float32)
        sides.extend([(b0, t1, t0), (b0, b1, t1)])

        t0 = np.array([xs[x], ys[-1], thickness[-1, x]], dtype=np.float32)
        t1 = np.array([xs[x + 1], ys[-1], thickness[-1, x + 1]], dtype=np.float32)
        b0 = np.array([xs[x], ys[-1], min_mm], dtype=np.float32)
        b1 = np.array([xs[x + 1], ys[-1], min_mm], dtype=np.float32)
        sides.extend([(b0, t0, t1), (b0, t1, b1)])

    for y in range(h - 1):
        t0 = np.array([xs[0], ys[y], thickness[y, 0]], dtype=np.float32)
        t1 = np.array([xs[0], ys[y + 1], thickness[y + 1, 0]], dtype=np.float32)
        b0 = np.array([xs[0], ys[y], min_mm], dtype=np.float32)
        b1 = np.array([xs[0], ys[y + 1], min_mm], dtype=np.float32)
        sides.extend([(b0, t0, t1), (b0, t1, b1)])

        t0 = np.array([xs[-1], ys[y], thickness[y, -1]], dtype=np.float32)
        t1 = np.array([xs[-1], ys[y + 1], thickness[y + 1, -1]], dtype=np.float32)
        b0 = np.array([xs[-1], ys[y], min_mm], dtype=np.float32)
        b1 = np.array([xs[-1], ys[y + 1], min_mm], dtype=np.float32)
        sides.extend([(b0, t1, t0), (b0, b1, t1)])

    return top + bottom + sides


def write_binary_stl(path: str | Path, triangles: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> None:
    with Path(path).open("wb") as f:
        f.write(b"2d-to-3d-relief".ljust(80, b" "))
        f.write(struct.pack("<I", len(triangles)))
        for a, b, c in triangles:
            n = _normal(a, b, c).astype(np.float32)
            f.write(struct.pack("<3f", *n))
            f.write(struct.pack("<3f", *a))
            f.write(struct.pack("<3f", *b))
            f.write(struct.pack("<3f", *c))
            f.write(struct.pack("<H", 0))
