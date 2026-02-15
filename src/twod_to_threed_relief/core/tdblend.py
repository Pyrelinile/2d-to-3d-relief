from __future__ import annotations

import numpy as np


def transmittance(thickness: np.ndarray, td_mm: float) -> np.ndarray:
    return np.exp(-thickness / max(td_mm, 1e-6))


def estimate_blend_layers(heightmap: np.ndarray, td_values: list[float], max_layers: int) -> np.ndarray:
    flat = heightmap.flatten()
    td = np.mean(td_values) if td_values else 0.8
    layers = np.clip(np.round((1 - np.exp(-flat / td)) * max_layers), 0, max_layers)
    return layers.reshape(heightmap.shape).astype(int)
