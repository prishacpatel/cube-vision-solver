import numpy as np
import pytest
import cv2

from cubesolver.colors import FACE_ORDER, facelets_from_samples, grid_cells, sample_face
from cubesolver.solver import InvalidCube, SOLVED, invert, solve, validate
from cubesolver.viewer import write_viewer

SCRAMBLED = "DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD"

# Typical sticker colors in BGR (standard scheme), including a deliberately close red/orange pair.
BGR = {
    "U": (235, 235, 235),  # white
    "R": (40, 30, 190),    # red
    "F": (70, 160, 20),    # green
    "D": (30, 215, 230),   # yellow
    "L": (30, 110, 235),   # orange
    "B": (180, 80, 20),    # blue
}


def render_face(letters, rng, noise=12, brightness=1.0):
    """Fake webcam frame of one face: a 3x3 grid of noisy colored squares."""
    frame = np.full((480, 640, 3), 40, np.uint8)
    cells = grid_cells(frame.shape)
    for (cx, cy, _), letter in zip(cells, letters):
        color = np.array(BGR[letter], float) * brightness + rng.normal(0, noise, 3)
        cv2.rectangle(frame, (cx - 50, cy - 50), (cx + 50, cy + 50), np.clip(color, 0, 255).tolist(), -1)
    return frame


@pytest.mark.parametrize("brightness", [1.0, 0.8, 1.15])
def test_scan_pipeline_recovers_state(brightness):
    rng = np.random.default_rng(1)
    faces = {}
    for i, f in enumerate(FACE_ORDER):
        frame = render_face(SCRAMBLED[i * 9:(i + 1) * 9], rng, brightness=brightness)
        faces[f] = sample_face(frame)
    # The scrambled string already uses face letters, and our fake colors are keyed by those letters.
    assert facelets_from_samples(faces) == SCRAMBLED


def test_hungarian_fixes_one_ambiguous_sticker():
    rng = np.random.default_rng(2)
    faces = {f: sample_face(render_face(SCRAMBLED[i * 9:(i + 1) * 9], rng)) for i, f in enumerate(FACE_ORDER)}
    # Make one orange sticker look almost exactly like red (bad glare).
    idx = SCRAMBLED.index("L", 0) if SCRAMBLED[4] != "L" else 0
    face_i, sticker_i = divmod(idx, 9)
    if sticker_i != 4:
        faces[FACE_ORDER[face_i]][sticker_i] = faces["R"][4] * 0.55 + faces["L"][4] * 0.45
    result = facelets_from_samples(faces)
    assert result.count("L") == 9 and result.count("R") == 9


def test_solution_actually_solves():
    moves = solve(SCRAMBLED)
    assert 0 < len(moves) <= 25
    assert solve(SOLVED) == []


def test_invert_roundtrip():
    assert invert(["R", "U'", "F2"]) == ["F2", "U", "R'"]
    assert invert(invert(["R", "U'", "F2"])) == ["R", "U'", "F2"]


def test_invalid_states_are_rejected():
    with pytest.raises(InvalidCube):
        validate("U" * 54)
    swapped = list(SCRAMBLED)
    swapped[0], swapped[1] = swapped[1], swapped[0]      # still 9 of each, but impossible
    swapped[8], swapped[9] = swapped[9], swapped[8]      # twist a corner
    with pytest.raises(InvalidCube):
        solve("".join(swapped))


def test_viewer_writes_html(tmp_path):
    path = write_viewer(["R", "U'"], tmp_path / "s.html", open_browser=False)
    text = path.read_text()
    assert 'alg="R U\'"'.replace("'", "&#x27;") in text
    assert "experimental-setup-alg" in text
