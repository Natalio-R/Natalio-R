"""source-prepped.png -> natalio-ascii.svg: monochrome ASCII that types itself row by row,
inside a macOS terminal window.

usage: python scripts/make_ascii_svg.py [source-prepped.png]   (STATIC=1 for a frozen frame)
"""
import os
import sys
from html import escape

import numpy as np
from PIL import Image

from window import BAR, DIM, FG, GREEN, BORDER, H, W, window

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = os.path.join(ROOT, "natalio-ascii.svg")
STATIC = os.environ.get("STATIC") == "1"
NAME = "Natalio Rabasco"

RAMP = " .`:-=+*cs#%@"   # sparse -> dense; on a dark window, dense = bright
#       ^ leading space clears the background to nothing
MAX_COLS, PAD, FOOT = 140, 20, 48
CW = (W - 2 * PAD) / MAX_COLS  # char width
LH, FS = CW / 0.55, CW / 0.6   # line height, font size
BOX_W, BOX_H = W - 2 * PAD, H - BAR - FOOT - 2 * PAD
ROW_DUR = 0.05


def to_ascii(path):
    img = Image.open(path)
    has_alpha = "A" in img.getbands()
    cols = min(MAX_COLS, round(BOX_W / CW))
    rows = round(cols * img.height / img.width * CW / LH)
    if rows * LH > BOX_H:  # foto alta: ajusta por altura
        rows = int(BOX_H // LH)
        cols = round(rows * LH / CW * img.width / img.height)
    px, alpha = (np.asarray(img.convert("LA").resize((cols, rows), Image.LANCZOS),
                            dtype=np.float32) / 255).transpose(2, 0, 1)
    idx = np.clip((px * len(RAMP)).astype(int), 1, len(RAMP) - 1)  # claro -> denso
    idx[(alpha < 0.5) if has_alpha else (px > 0.94)] = 0  # fondo -> espacio
    return cols, ["".join(RAMP[i] for i in row).rstrip() for row in idx]


def main():
    cols, rows = to_ascii(SRC)
    x0 = PAD + (BOX_W - cols * CW) / 2
    y0 = BAR + PAD + (BOX_H - len(rows) * LH) / 2
    out = []
    for i, row in enumerate(rows):
        if not row:
            continue
        y, rw = y0 + i * LH, len(row) * CW
        text = (f'<text class="a" x="{x0:.1f}" y="{y + FS * 0.9:.1f}" textLength="{rw:.1f}" '
                f'lengthAdjust="spacing" xml:space="preserve">{escape(row)}</text>')
        if STATIC:
            out.append(text)
            continue
        # wipe izquierda->derecha con un "cursor" de bloque en el borde, escalonado por filas
        t = i * ROW_DUR
        dur = f'begin="{t:.2f}s" dur="{ROW_DUR:.2f}s" fill="freeze"'
        out.append(
            f'<clipPath id="r{i}"><rect x="{x0:.1f}" y="{y:.1f}" width="0" height="{LH:.1f}">'
            f'<animate attributeName="width" from="0" to="{rw:.1f}" {dur}/></rect></clipPath>'
            f'<g clip-path="url(#r{i})">{text}</g>'
            f'<rect x="{x0:.1f}" y="{y + 1:.1f}" width="{CW:.1f}" height="{LH - 2:.1f}" fill="{GREEN}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
            f'<animate attributeName="x" from="{x0:.1f}" to="{x0 + rw:.1f}" {dur}/>'
            f'<set attributeName="opacity" to="0" begin="{t + ROW_DUR:.2f}s"/></rect>')

    fy = H - FOOT
    prompt = "natalio@github:~$ whoami "
    cursor_x = PAD + (len(prompt) + len(NAME) + 1) * 12
    blink = "" if STATIC else ('<animate attributeName="opacity" values="1;1;0;0" '
                               'keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>')
    out.append(f'<line x1="0" y1="{fy}" x2="{W}" y2="{fy}" stroke="{BORDER}"/>'
               f'<text x="{PAD}" y="{fy + 31}" font-size="20" fill="{DIM}" textLength="{(len(prompt) + len(NAME)) * 12}" '
               f'xml:space="preserve">{prompt}<tspan fill="{FG}">{NAME}</tspan></text>'
               f'<rect x="{cursor_x}" y="{fy + 14}" width="11" height="22" fill="{GREEN}">{blink}</rect>')

    svg = window("natalio@github: ~$ ./portrait.sh", "\n".join(out),
                 f".a{{font-size:{FS:.2f}px;fill:{FG}}}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)} ({cols}x{len(rows)})")


if __name__ == "__main__":
    main()
