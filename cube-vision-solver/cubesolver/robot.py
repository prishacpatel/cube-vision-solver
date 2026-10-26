"""Send a solution to the Arduino robot over USB serial (optional)."""
from __future__ import annotations

import time


def send_moves(moves: list[str], port: str, baud: int = 115200) -> None:
    import serial  # imported lazily so the rest of the project works without pyserial

    with serial.Serial(port, baud, timeout=60) as ser:
        time.sleep(2.0)  # Arduino resets when the port opens
        ser.reset_input_buffer()
        line = " ".join(moves) + "\n"
        ser.write(line.encode("ascii"))
        reply = ser.readline().decode(errors="replace").strip()
        if reply != "DONE":
            raise RuntimeError(f"Robot replied {reply!r} instead of 'DONE'")
