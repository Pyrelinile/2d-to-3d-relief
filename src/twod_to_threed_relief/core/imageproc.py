from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def luminance_array(image: Image.Image, linear: bool = False) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32) / 255.0
    if linear:
        arr = np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    return lum


def build_heightmap(
    image: Image.Image,
    gamma: float = 1.0,
    invert: bool = False,
    blur: float = 0.0,
    mesh_x: int = 256,
    mesh_y: int = 256,
) -> np.ndarray:
    if blur > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur))
    image = image.resize((mesh_x, mesh_y), Image.Resampling.LANCZOS)
    lum = luminance_array(image)
    lum = np.clip(lum, 0, 1) ** gamma
    if invert:
        lum = 1.0 - lum
    mn, mx = float(lum.min()), float(lum.max())
    if mx > mn:
        lum = (lum - mn) / (mx - mn)
    return lum


def heightmap_to_image(heightmap: np.ndarray) -> Image.Image:
    arr = np.clip(heightmap * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="L")


def map_height_range(heightmap: np.ndarray, min_mm: float, max_mm: float) -> np.ndarray:
    return min_mm + heightmap * (max_mm - min_mm)
