"""Kociemba wrapper plus small helpers for move strings."""
from __future__ import annotations

import kociemba

SOLVED = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"


class InvalidCube(ValueError):
    """The scanned cube cannot exist (misread color, twisted corner, etc.)."""


def validate(facelets: str) -> None:
    if len(facelets) != 54:
        raise InvalidCube(f"Expected 54 stickers, got {len(facelets)}.")
    for letter in "URFDLB":
        n = facelets.count(letter)
        if n != 9:
            raise InvalidCube(f"Face {letter} has {n} stickers instead of 9. Re-scan the faces with bad lighting.")
    for i, letter in enumerate("URFDLB"):
        if facelets[i * 9 + 4] != letter:
            raise InvalidCube(f"Center of face {letter} is wrong.")


def solve(facelets: str) -> list[str]:
    """Return the solution as a list of moves like ['R', "U'", 'F2']."""
    validate(facelets)
    if facelets == SOLVED:
        return []
    try:
        result = kociemba.solve(facelets)
    except ValueError as exc:
        raise InvalidCube(
            "That cube state is not solvable. Usually one sticker was misread, or two stickers were "
            "swapped by hand. Check the lighting and re-scan, or fix the string by hand."
        ) from exc
    return result.split()


def invert(moves: list[str]) -> list[str]:
    """Moves that undo `moves`."""
    def inv(m: str) -> str:
        if m.endswith("2"):
            return m
        return m[:-1] if m.endswith("'") else m + "'"
    return [inv(m) for m in reversed(moves)]
