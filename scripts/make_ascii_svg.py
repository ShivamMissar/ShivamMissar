"""Stage B of the ASCII portrait: prepped PNG -> self-typing monochrome SVG.

usage: python scripts/make_ascii_svg.py [data/portrait-prepped.png]

Writes assets/portrait-dark.svg and assets/portrait-light.svg. Each row is revealed
by a clip-rect whose width animates left->right (SMIL, no JS) with a block cursor
riding the edge; rows start staggered top to bottom, play once and freeze.
"""
import os
import sys

import numpy as np
from PIL import Image

from theme import THEMES, FONT, STATIC, ASSETS, esc, window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "portrait-prepped.png")

W, H = 370, 400          # matches the README column width
PAD, TOP = 12, 30
COLS = 72
CW = (W - 2 * PAD) / COLS            # character cell width
LH = CW / 0.6                        # cell height (monospace glyphs are ~0.6 wide)
ROWS = int((H - TOP - 2 * PAD) / LH)
FS = LH * 1.05                       # font size

RAMP = " .`:-=+*cs#%@"  # index 0 = blank, last = most ink

img = Image.open(src).convert("LA")
gray, mask = (np.asarray(c.resize((COLS, ROWS), Image.LANCZOS), dtype=float) / 255 for c in img.split())


def rows_for(theme):
    # dark: light glyphs on dark -> ink follows brightness. light: dark glyphs -> ink follows darkness
    ink = gray if theme == "dark" else 1 - gray
    ink = np.clip((ink - 0.08) / 0.92, 0, 1) * (mask > 0.5)
    out = []
    for r in range(ROWS):
        line = "".join(RAMP[int(round(v * (len(RAMP) - 1)))] for v in ink[r])
        out.append(line.rstrip())
    # drop fully blank rows at top/bottom so the face sits centred
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return out


def build(theme):
    t = THEMES[theme]
    lines = rows_for(theme)
    y0 = TOP + PAD + (H - TOP - 2 * PAD - len(lines) * LH) / 2
    parts = [window(t, W, H, "~/portrait.txt")]
    defs, body = [], []
    start, step, dur = 0.3, 0.06, 0.45
    for i, line in enumerate(lines):
        if not line:
            continue
        y = y0 + i * LH
        w = len(line) * CW
        # every glyph pinned to its own column via an x-list: exact grid in any renderer/font
        cols = [j for j, ch in enumerate(line) if ch != " "]
        xs = " ".join(f"{PAD + j * CW:.1f}" for j in cols)
        text = f'<text x="{xs}" y="{y + LH * 0.82:.2f}">{esc("".join(line[j] for j in cols))}</text>'
        if STATIC:
            body.append(text)
            continue
        b = start + i * step
        defs.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{y:.2f}" height="{LH + 0.5:.2f}" width="0">'
                    f'<animate attributeName="width" from="0" to="{w + 1:.2f}" begin="{b:.2f}s" dur="{dur}s" fill="freeze"/>'
                    f'</rect></clipPath>')
        body.append(f'<g clip-path="url(#r{i})">{text}</g>')
        body.append(f'<rect x="{PAD}" y="{y:.2f}" width="{CW:.2f}" height="{LH:.2f}" fill="{t["accent"]}" opacity="0">'
                    f'<animate attributeName="x" from="{PAD}" to="{PAD + w:.2f}" begin="{b:.2f}s" dur="{dur}s" fill="freeze"/>'
                    f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.97;1" begin="{b:.2f}s" dur="{dur}s" fill="freeze"/>'
                    f'</rect>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{"".join(defs)}</defs>{"".join(parts)}'
           f'<g font-family="{FONT}" font-size="{FS:.2f}" fill="{t["ascii"]}">{"".join(body)}</g></svg>')
    path = os.path.join(ASSETS, f"portrait-{theme}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print("wrote", path, f"({len(lines)} rows x {COLS} cols)")


os.makedirs(ASSETS, exist_ok=True)
for th in THEMES:
    build(th)
