"""data/contributions.json -> contrib-heatmap.svg (53x7 grid, diagonal reveal, then freeze)."""
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
BG, BORDER, FG, DIM = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
MONTHS = "ene feb mar abr may jun jul ago sep oct nov dic".split()

W, CELL, GAP = 860, 12, 3
STEP = CELL + GAP
LEFT, TOP = 44, 40


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

    cells, months, last_month_col = [], [], -9
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt - first).days // 7, (dt.weekday() + 1) % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        delay = (col + row) * 0.018
        style = "" if STATIC else f' style="animation-delay:{delay:.3f}s"'
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{PALETTE[level(d, top)]}"{style}/>')
        if dt.day <= 7 and row == 0 and col - last_month_col >= 3:
            months.append(f'<text x="{x}" y="{TOP - 10}">{MONTHS[dt.month - 1]}</text>')
            last_month_col = col

    grid_bottom = TOP + 7 * STEP - GAP
    weekdays = "".join(f'<text x="{LEFT - 8}" y="{TOP + r * STEP + 10}" text-anchor="end">{n}</text>'
                       for r, n in ((1, "lun"), (3, "mié"), (5, "vie")))
    ly = grid_bottom + 18
    legend_x = W - 24 - 6 * STEP - 30
    legend = (f'<text x="{legend_x - 8}" y="{ly + 10}" text-anchor="end">Menos</text>'
              + "".join(f'<rect x="{legend_x + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
                        for i, c in enumerate(PALETTE))
              + f'<text x="{legend_x + 6 * STEP + 5}" y="{ly + 10}">Más</text>')
    best = data["best_day"]
    best_date = date.fromisoformat(best["date"])
    stats = (f'Racha actual: <tspan fill="{PALETTE[4]}">{data["current_streak"]}</tspan> días'
             f'  ·  Racha más larga: <tspan fill="{PALETTE[4]}">{data["longest_streak"]}</tspan> días'
             f'  ·  Mejor día: <tspan fill="{PALETTE[4]}">{best["count"]}</tspan>'
             f' ({best_date.day} {MONTHS[best_date.month - 1]} {best_date.year})')
    H = ly + 54

    anim = "" if STATIC else (
        ".c{opacity:0;animation:drop .4s ease-out both}"
        "@keyframes drop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        ".f{opacity:0;animation:fade .6s ease-out 1.2s both}"
        "@keyframes fade{to{opacity:1}}")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:{FONT};font-size:11px;fill:{DIM}}}{anim}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<g>{"".join(months)}{weekdays}</g>
<g>{"".join(cells)}</g>
<g class="f">
<text x="{LEFT}" y="{ly + 10}" style="font-size:12px;fill:{FG}"><tspan fill="{PALETTE[4]}" font-weight="bold">{fmt(data["total"])}</tspan> contribuciones en el último año</text>
{legend}
<text x="{LEFT}" y="{ly + 36}">{stats}</text>
</g>
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
