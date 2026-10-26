"""Write a self-contained HTML page that animates the solution in 3D.

The page uses cubing.js's <twisty-player>. It starts from a solved cube, applies the INVERSE of the
solution as a setup (which produces exactly the scanned state), then plays the solution forward.
"""
from __future__ import annotations

import html
import webbrowser
from pathlib import Path

from .solver import invert

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cube solution</title>
<script type="module" src="https://cdn.cubing.net/v0/js/cubing/twisty"></script>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; }}
  twisty-player {{ width: 100%; height: 420px; }}
  code {{ display: block; padding: .8rem 1rem; background: #f2f2f2; border-radius: 6px;
          font-size: 1.1rem; line-height: 1.7; word-spacing: .5ch; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#17191a; color:#eee; }} code {{ background:#262a2c; }} }}
</style></head>
<body>
<h1>Solution: {count} moves</h1>
<twisty-player experimental-setup-alg="{setup}" alg="{alg}" control-panel="bottom-row"
               background="none" hint-facelets="none"></twisty-player>
<p>Press play, or step through with the controls.</p>
<code>{alg}</code>
</body></html>
"""


def write_viewer(moves: list[str], path: str | Path = "solution.html", open_browser: bool = True) -> Path:
    path = Path(path)
    page = TEMPLATE.format(
        count=len(moves),
        setup=html.escape(" ".join(invert(moves))),
        alg=html.escape(" ".join(moves)),
    )
    path.write_text(page, encoding="utf-8")
    if open_browser:
        webbrowser.open(path.resolve().as_uri())
    return path
