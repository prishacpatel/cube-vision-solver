from __future__ import annotations

import argparse
import sys

from .solver import InvalidCube, solve
from .viewer import write_viewer

DEMO = "DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cubesolver", description="Webcam Rubik's Cube solver")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--demo", action="store_true", help="solve a built-in scrambled cube (no webcam)")
    src.add_argument("--facelets", metavar="STRING", help="54-letter state in URFDLB order")
    p.add_argument("--camera", type=int, default=0, help="camera index (default 0)")
    p.add_argument("--no-open", action="store_true", help="write solution.html but do not open a browser")
    p.add_argument("--robot", metavar="PORT", help="serial port of the Arduino robot, e.g. COM3 or /dev/ttyACM0")
    args = p.parse_args(argv)

    if args.demo:
        facelets = DEMO
    elif args.facelets:
        facelets = args.facelets.strip().upper()
    else:
        from .scanner import scan_cube  # needs OpenCV GUI support
        try:
            facelets = scan_cube(args.camera)
        except KeyboardInterrupt:
            print("Cancelled.")
            return 1
        print("Scanned state:", facelets)

    try:
        moves = solve(facelets)
    except InvalidCube as exc:
        print("Cannot solve:", exc, file=sys.stderr)
        return 2

    print(f"Solution ({len(moves)} moves): {' '.join(moves) or '(already solved)'}")
    path = write_viewer(moves, open_browser=not args.no_open)
    print("Animation written to", path)

    if args.robot:
        from .robot import send_moves
        print("Sending to robot on", args.robot)
        send_moves(moves, args.robot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
