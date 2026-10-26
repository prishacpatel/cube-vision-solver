"""Turn raw sticker colors into a Kociemba facelet string.

The Kociemba facelet string has 54 letters in the order U R F D L B (9 stickers per face,
read row by row as the unfolded net is seen from outside the cube). Each letter names the
FACE that sticker belongs to, which we learn from the center sticker of every face. That means
the solver works for any color scheme, not only the standard white/green/red one.
"""
from __future__ import annotations

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

FACE_ORDER = "URFDLB"


def grid_cells(frame_shape, scale: float = 0.6):
    """Return nine (cx, cy, radius) sampling circles for a centered 3x3 grid, row by row."""
    h, w = frame_shape[:2]
    side = int(min(h, w) * scale)
    x0, y0 = (w - side) // 2, (h - side) // 2
    cell = side / 3
    radius = int(cell * 0.18)
    return [
        (int(x0 + cell * (c + 0.5)), int(y0 + cell * (r + 0.5)), radius)
        for r in range(3)
        for c in range(3)
    ]


def sample_face(frame_bgr: np.ndarray, cells=None) -> np.ndarray:
    """Median CIE-LAB color of a small patch at each of the nine stickers. Shape (9, 3)."""
    cells = cells or grid_cells(frame_bgr.shape)
    lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    out = []
    for cx, cy, r in cells:
        patch = lab[max(cy - r, 0): cy + r + 1, max(cx - r, 0): cx + r + 1].reshape(-1, 3)
        out.append(np.median(patch, axis=0))
    return np.array(out)


def facelets_from_samples(faces: dict[str, np.ndarray]) -> str:
    """Classify all 54 stickers.

    Stickers are compared to the six center colors, then assigned with the Hungarian algorithm so
    that every face gets exactly nine stickers. That constraint fixes most lighting mistakes, such
    as one orange sticker looking red.
    """
    missing = [f for f in FACE_ORDER if f not in faces]
    if missing:
        raise ValueError(f"Missing scans for faces: {''.join(missing)}")

    stickers = np.vstack([faces[f] for f in FACE_ORDER])            # (54, 3), in facelet order
    centers = np.array([faces[f][4] for f in FACE_ORDER])           # (6, 3)

    # Chroma matters more than lightness (glare, shadows), so down-weight L.
    weights = np.array([0.5, 1.0, 1.0])
    dist = np.linalg.norm((stickers[:, None, :] - centers[None, :, :]) * weights, axis=2)  # (54, 6)

    # 54 slots: slot k belongs to face k // 9. Cost of putting sticker s into slot k.
    cost = np.repeat(dist, 9, axis=1)                               # (54, 54)
    # A center sticker can only ever be its own face.
    for f in range(6):
        s = f * 9 + 4
        cost[s, :] = 1e6
        cost[s, f * 9: f * 9 + 9] = 0
    rows, cols = linear_sum_assignment(cost)
    letters = [""] * 54
    for s, slot in zip(rows, cols):
        letters[s] = FACE_ORDER[slot // 9]
    return "".join(letters)


def swatch_bgr(letter_or_lab) -> tuple[int, int, int]:
    """BGR color for drawing a LAB sample on screen."""
    lab = np.uint8([[np.clip(letter_or_lab, 0, 255)]])
    b, g, r = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)[0, 0]
    return int(b), int(g), int(r)
