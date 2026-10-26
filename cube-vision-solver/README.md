# Cube vision solver

Scan a Rubik's Cube with a webcam, detect its colors with OpenCV, solve it with Kociemba's two-phase algorithm, and watch the solution play back as a 3D animation. An optional Arduino robot can then turn the real cube.

> Developed a computer-vision Rubik's Cube solver that detects cube state from a webcam and solves it in ~20 moves.

**Stack:** Python, OpenCV, NumPy/SciPy, Kociemba algorithm, cubing.js (animation), optional Arduino (C++)

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m cubesolver --demo      # no webcam: solves a built-in scramble and opens the animation
python -m cubesolver             # scan your own cube with the webcam
```

Run the tests with `python -m pytest`.

## Scanning your cube

1. Start with the cube in your hand: one center color facing up (Top), another facing you (Front). On a standard cube, white on top and green in front.
2. The window prompts for the faces in this order: **Top, Right, Front, Bottom, Left, Back**. Each prompt says which edge should point toward the top or bottom of the image. These match the unfolded cube net, which is what the solver expects.
3. Line the face up with the circles and press **Space**. Circles show the color the camera sees, so you can spot glare before capturing. **Backspace** redoes the previous face.
4. After the sixth face, press **Enter**. The solution prints in the terminal and the animation opens in your browser.

Tips: use even, diffuse light (not a window behind the cube), a plain dark background, and keep the cube about 20-30 cm from the camera.

If the cube is reported unsolvable, one sticker was almost certainly misread. Re-scan with better light, or pass the state yourself: `python -m cubesolver --facelets <54 letters in URFDLB order>`.

## How it works

| Step | File | What happens |
|---|---|---|
| Capture | `cubesolver/scanner.py` | Webcam UI, one face at a time |
| Color detection | `cubesolver/colors.py` | Median CIE-LAB color per sticker. Every sticker is compared to the six center colors, then the **Hungarian algorithm** assigns exactly nine stickers to each face, which corrects most glare and red/orange confusion |
| Solving | `cubesolver/solver.py` | Validates the state, then runs Kociemba's two-phase solver (typically 19-22 moves) |
| Animation | `cubesolver/viewer.py` | Writes `solution.html` using the cubing.js `twisty-player`. It plays the solution from the scanned state |
| Robot (optional) | `cubesolver/robot.py` + `arduino/` | Sends the moves over USB serial |

The animation needs internet access, since it loads cubing.js from a CDN. The move list is also printed in the terminal.

## Optional: turning the real cube with a robot

`arduino/cube_robot/cube_robot.ino` drives six stepper motors (one per face) through A4988 or DRV8825 drivers. Pins and wiring are documented at the top of the sketch.

```bash
python -m cubesolver --robot COM3          # or /dev/ttyACM0 on Linux/Mac
```

This uses steppers rather than hobby servos because a servo only swings about 180 degrees and cannot make repeated continuous quarter turns of a face. You still need a mechanical frame with a cross-shaped adapter on each motor shaft. Plenty of open 3D-printable designs exist for this layout. Calibrate `INVERT_DIR` and `STEP_DELAY_US` first, with the cube out of the frame.

## Project layout

```
cubesolver/     scanner, color detection, solver, viewer, robot link, CLI
arduino/        stepper robot firmware
tests/          pipeline tests using synthetic webcam frames
```
