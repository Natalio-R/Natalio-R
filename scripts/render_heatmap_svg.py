"""data/contributions.json -> contrib-heatmap.svg (53x7 grid, diagonal pop-in, then freeze)."""
import json
import os
from datetime import date

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "contrib-heatmap.svg")
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)
DIM, GREEN = "#7d8590", "#39d353"  # grises medios: legibles en tema claro y oscuro
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONTHS = "Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic".split()

CELL, GAP = 13, 3
STEP = CELL + GAP
LEFT, TOP = 36, 24


def fmt(n):
    return f"{n:,}".replace(",", ".")


def level(d, top):
    if d["level"] == 4 and d["count"] >= top:
        return 5
    return d["level"]


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])  # GitHub's calendar starts on Sunday
    nonzero = sorted(d["count"] for d in days if d["count"])
    top = nonzero[int(len(nonzero) * 0.95)] if nonzero else 1
    cols = (date.fromisoformat(days[-1]["date"]) - first).days // 7 + 1  # 53 o 54 semanas
    W = LEFT + cols * STEP - GAP + 2

    cells, months, last_month_col = [], [], -9
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt - first).days // 7, (dt.weekday() + 1) % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        style = "" if STATIC else f' style="animation-delay:{(col + row) * 0.035:.3f}s"'
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{PALETTE[level(d, top)]}"{style}/>')
        if dt.day <= 7 and row == 0 and col - last_month_col >= 3 and x + 28 <= W:
            months.append(f'<text x="{x}" y="{TOP - 8}">{MONTHS[dt.month - 1]}</text>')
            last_month_col = col

    grid_bottom = TOP + 7 * STEP - GAP
    weekdays = "".join(f'<text x="0" y="{TOP + r * STEP + 11}">{n}</text>'
                       for r, n in ((1, "Lun"), (3, "Mié"), (5, "Vie")))
    ly = grid_bottom + 12
    legend_x = W - 2 - 6 * STEP - 30
    legend = (f'<text x="{legend_x - 8}" y="{ly + 11}" text-anchor="end">Menos</text>'
              + "".join(f'<rect x="{legend_x + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
                        for i, c in enumerate(PALETTE))
              + f'<text x="{legend_x + 6 * STEP + 3}" y="{ly + 11}">Más</text>')
    H = ly + CELL + 8

    anim = "" if STATIC else (
        ".c{transform-box:fill-box;transform-origin:center;animation:pop .55s ease-out both}"
        "@keyframes pop{0%{opacity:0;transform:scale(.2)}60%{opacity:1;transform:scale(1.1)}100%{opacity:1;transform:scale(1)}}"
        ".f{animation:fade .6s ease-out 1.5s both}@keyframes fade{from{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.c,.f{animation:none}}")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>{anim}</style>
<g font-size="13" font-weight="600" fill="{DIM}">{"".join(months)}{weekdays}</g>
<g>{"".join(cells)}</g>
<g class="f" font-size="13" fill="{DIM}">
<text x="{LEFT}" y="{ly + 12}" font-size="15" font-weight="700"><tspan fill="{GREEN}">{fmt(data["total"])}</tspan> contribuciones en el último año</text>
{legend}
</g>
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
