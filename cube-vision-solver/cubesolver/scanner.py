"""Interactive webcam scanner: show each face in the grid, press SPACE, repeat six times."""
from __future__ import annotations

import cv2
import numpy as np

from .colors import FACE_ORDER, facelets_from_samples, grid_cells, sample_face, swatch_bgr

# How to hold the cube for each face. All six match the unfolded net seen from outside the cube,
# which is what the Kociemba facelet order assumes.
PROMPTS = {
    "U": "Top face (U). Put the Front face's edge at the BOTTOM of the image.",
    "R": "Right face (R). Keep the Top face toward the TOP of the image.",
    "F": "Front face (F). Keep the Top face toward the TOP of the image.",
    "D": "Bottom face (D). Put the Front face's edge at the TOP of the image.",
    "L": "Left face (L). Keep the Top face toward the TOP of the image.",
    "B": "Back face (B). Keep the Top face toward the TOP of the image.",
}
START_HINT = "Start: hold the cube with one center color up (Top) and another toward you (Front)."


def _put(img, text, y, scale=0.6, color=(255, 255, 255)):
    cv2.putText(img, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def draw_net(canvas, faces, origin=(14, 80), size=14):
    """Small unfolded net of everything captured so far, drawn with the true sticker colors."""
    layout = {"U": (3, 0), "L": (0, 3), "F": (3, 3), "R": (6, 3), "B": (9, 3), "D": (3, 6)}
    ox, oy = origin
    for face, (gx, gy) in layout.items():
        for i in range(9):
            x = ox + (gx + i % 3) * size
            y = oy + (gy + i // 3) * size
            color = swatch_bgr(faces[face][i]) if face in faces else (60, 60, 60)
            cv2.rectangle(canvas, (x, y), (x + size - 1, y + size - 1), color, -1)
            cv2.rectangle(canvas, (x, y), (x + size - 1, y + size - 1), (0, 0, 0), 1)


def scan_cube(camera_index: int = 0) -> str:
    """Run the scanner and return the 54-letter facelet string. Raises KeyboardInterrupt on quit."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}. Try --camera 1, or close other apps using it.")

    faces: dict[str, np.ndarray] = {}
    step = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Camera stopped sending frames.")
            view = frame.copy()
            cells = grid_cells(frame.shape)
            live = sample_face(frame, cells)

            for (cx, cy, r), lab in zip(cells, live):
                cv2.circle(view, (cx, cy), r + 3, (0, 0, 0), 2)
                cv2.circle(view, (cx, cy), r, swatch_bgr(lab), -1)

            if step < 6:
                face = FACE_ORDER[step]
                _put(view, f"Face {step + 1} of 6: {PROMPTS[face]}", 28)
                _put(view, START_HINT if step == 0 else "SPACE = capture   BACKSPACE = redo previous   Q = quit", 52, 0.5)
            else:
                _put(view, "All faces captured. ENTER = solve   BACKSPACE = redo last face   Q = quit", 28)
            draw_net(view, faces, origin=(14, 80))
            cv2.imshow("Cube scanner", view)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                raise KeyboardInterrupt
            if key == ord(" ") and step < 6:
                faces[FACE_ORDER[step]] = live.copy()
                step += 1
            elif key in (8, 127) and step > 0:
                step -= 1
                faces.pop(FACE_ORDER[step], None)
            elif key in (13, 10) and step == 6:
                return facelets_from_samples(faces)
    finally:
        cap.release()
        cv2.destroyAllWindows()
