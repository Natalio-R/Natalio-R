"""source-prepped.png -> natalio-ascii.svg: monochrome ASCII that types itself row by row.

usage: python scripts/make_ascii_svg.py [source-prepped.png]   (STATIC=1 for a frozen frame)
"""
import os
import sys
from html import escape

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = os.path.join(ROOT, "natalio-ascii.svg")
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"   # sparse -> dense; on a dark card, dense = bright
#       ^ leading space clears the background to nothing
COLS, MAX_ROWS = 100, 60
CW, LH, FS, PAD = 6.6, 12, 11, 16  # char width, line height, font size
FILL, BG, BORDER, CURSOR = "#c9d1d9", "#0d1117", "#30363d", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
ROW_DUR = 0.06


def to_ascii(path):
    img = Image.open(path)
    has_alpha = "A" in img.getbands()
    rows = min(MAX_ROWS, round(COLS * img.height / img.width * CW / LH))
    px, alpha = (np.asarray(img.convert("LA").resize((COLS, rows), Image.LANCZOS),
                            dtype=np.float32) / 255).transpose(2, 0, 1)
    idx = np.clip((px * len(RAMP)).astype(int), 1, len(RAMP) - 1)  # claro -> denso
    idx[(alpha < 0.5) if has_alpha else (px > 0.94)] = 0  # fondo -> espacio
    return ["".join(RAMP[i] for i in row).rstrip() for row in idx]


def main():
    rows = to_ascii(SRC)
    tw = COLS * CW
    W, H = tw + 2 * PAD, len(rows) * LH + 2 * PAD
    out = []
    for i, row in enumerate(rows):
        if not row:
            continue
        y = PAD + i * LH
        text = (f'<text x="{PAD}" y="{y + FS - 1}" textLength="{len(row) * CW:.1f}" '
                f'lengthAdjust="spacing" xml:space="preserve">{escape(row)}</text>')
        if STATIC:
            out.append(text)
            continue
        # wipe izquierda->derecha con un "cursor" de bloque en el borde, escalonado por filas
        t, rw = i * ROW_DUR, len(row) * CW
        dur = f'begin="{t:.2f}s" dur="{ROW_DUR:.2f}s" fill="freeze"'
        out.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{y}" width="0" height="{LH}">'
            f'<animate attributeName="width" from="0" to="{rw:.1f}" {dur}/></rect></clipPath>'
            f'<g clip-path="url(#r{i})">{text}</g>'
            f'<rect x="{PAD}" y="{y + 1}" width="{CW:.1f}" height="{LH - 2}" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + rw:.1f}" {dur}/>'
            f'<set attributeName="opacity" to="0" begin="{t + ROW_DUR:.2f}s"/></rect>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}">
<style>text{{font-family:{FONT};font-size:{FS}px;fill:{FILL}}}</style>
<rect x=".5" y=".5" width="{W - 1:.0f}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
{chr(10).join(out)}
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)} ({COLS}x{len(rows)})")


if __name__ == "__main__":
    main()
