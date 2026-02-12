from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image


def parse_palette_string(value: str) -> list[str]:
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return [p if p.startswith("#") else f"#{p}" for p in parts]


def load_palette(path_or_csv: str) -> list[str]:
    path = Path(path_or_csv)
    if path.exists():
        if path.suffix.lower() in {".json"}:
            return [c if c.startswith("#") else f"#{c}" for c in json.loads(path.read_text())]
        return parse_palette_string(path.read_text().strip())
    return parse_palette_string(path_or_csv)


def auto_palette(image: Image.Image, colors: int, method: str, seed: int = 42) -> list[str]:
    if method == "median-cut":
        q = image.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
        p = q.getpalette()[: colors * 3]
        return [f"#{p[i]:02x}{p[i+1]:02x}{p[i+2]:02x}" for i in range(0, len(p), 3)]

    rng = np.random.default_rng(seed)
    arr = np.asarray(image.convert("RGB").resize((256, 256)), dtype=np.float32).reshape(-1, 3)
    idx = rng.choice(arr.shape[0], size=colors, replace=False)
    centers = arr[idx]
    for _ in range(10):
        dist = ((arr[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = dist.argmin(axis=1)
        for k in range(colors):
            pts = arr[labels == k]
            if len(pts):
                centers[k] = pts.mean(axis=0)
    centers = np.clip(centers, 0, 255).astype(np.uint8)
    return [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in centers]
