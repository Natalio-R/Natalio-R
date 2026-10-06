"""Neofetch-style info card in a macOS window -> info-card.svg. STATIC=1 emits a frozen frame.

Reads data/contributions.json (if present) for the live GitHub rows, so the daily
workflow regenerates it alongside the heatmap.
"""
import json
import os
import textwrap
from datetime import date
from html import escape

from window import BAR, DIM, FG, GREEN, MONTHS, NEON, PALETTE, W, window

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "info-card.svg")
DATA = os.path.join(ROOT, "data", "contributions.json")
STATIC = os.environ.get("STATIC") == "1"

USER_HOST = "natalio@github"
ROWS = [
    ("Ahora", "NTT Data (BBVA) · Big Data, IA y Frontend"),
    ("Founder", "Cofundador de Fractal Agency"),
    ("Antes", "SALTWAVE (Malta) · Web Dev & Digital Mgr"),
    ("", "Movil Europa · Full Stack E-commerce"),
    ("Stack", "JavaScript, React, HTML5, CSS3, WordPress"),
    ("Data/IA", "Big Data, IA, automatizaciones"),
    ("Marketing", "Google Ads, Facebook Ads, Email marketing"),
    ("Ubicación", "Alicante, España (remoto)"),
    ("Idiomas", "Español (nativo) · Inglés (B1)"),
    ("Highlights", "+8 años transformando curiosidad en código"),
    ("", "E-commerce de cero: pagos y logística 24-48h"),
    ("", "Side-projects SaaS con nuevas tecnologías"),
]

FS, LH, PAD = 21, 31.5, 28
CW = FS * 0.6
KEY_COLS, VAL_COLS = 12, 45
BARS_H = 64  # altura del mini gráfico mensual


def fmt(n):
    return f"{n:,}".replace(",", ".")


def dias(n):
    return f"{n} día" if n == 1 else f"{n} días"


def github_rows():
    if not os.path.exists(DATA):
        return []
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)
    active = sum(1 for x in d["days"] if x["count"])
    best = date.fromisoformat(d["best_day"]["date"])
    return [
        ("Contribs", f"{fmt(d['total'])} en el último año"),
        ("Racha", f"{dias(d['current_streak'])} (máx. {d['longest_streak']})"),
        ("Mejor día", f"{d['best_day']['count']} contribuciones ({best.day} {MONTHS[best.month - 1]})"),
        ("Activo", f"{active} de {len(d['days'])} días ({round(100 * active / len(d['days']))}%)"),
        ("Actividad", d["monthly"]),
    ]


def text_line(key, val):
    for i, chunk in enumerate(textwrap.wrap(val, VAL_COLS)):
        k = f"{key}:" if key and i == 0 else ""
        yield (f'<tspan fill="{GREEN}" font-weight="bold">{escape(k.ljust(KEY_COLS))}</tspan>'
               f'<tspan fill="{FG}">{escape(chunk)}</tspan>')


def bars(monthly, x, y, delay):
    """Mini gráfico de barras por mes (rects, no glifos: no depende de la fuente)."""
    items = sorted(monthly.items())[-13:]
    top = max((v for _, v in items), default=0) or 1
    step = (W - PAD - x) / len(items)
    out = []
    for i, (ym, v) in enumerate(items):
        h = max(3, BARS_H * v / top)
        color = NEON if v == top and v else PALETTE[2 + min(3, int(3 * v / top))] if v else PALETTE[0]
        bx = x + i * step
        base = y + BARS_H
        grow = "" if STATIC else (
            f'<animate attributeName="height" from="0" to="{h:.1f}" begin="{delay + i * 0.05:.2f}s" dur=".6s" fill="freeze"/>'
            f'<animate attributeName="y" from="{base}" to="{base - h:.1f}" begin="{delay + i * 0.05:.2f}s" dur=".6s" fill="freeze"/>')
        out.append(f'<rect x="{bx:.1f}" y="{base if grow else base - h:.1f}" width="{step * 0.7:.1f}" '
                   f'height="{0 if grow else h:.1f}" rx="3" fill="{color}">{grow}</rect>'
                   f'<text x="{bx + step * 0.35:.1f}" y="{y + BARS_H + 20}" font-size="14" fill="{DIM}" '
                   f'text-anchor="middle">{MONTHS[int(ym[5:]) - 1][0].upper()}</text>')
    return "".join(out)


def main():
    lines = [f'<tspan fill="{NEON}" font-weight="bold">{USER_HOST}</tspan>',
             f'<tspan fill="{DIM}">{"-" * len(USER_HOST)}</tspan>']
    for key, val in ROWS:
        lines += text_line(key, val)
    lines.append("")
    for key, val in github_rows():
        if isinstance(val, dict):
            lines += [(key, val), "", "", ""]  # 3 líneas extra para las barras
        else:
            lines += text_line(key, val)

    out, y = [], BAR + PAD + FS
    for i, content in enumerate(lines):
        delay = f' style="animation-delay:{0.3 + i * 0.09:.2f}s"' if not STATIC else ""
        if isinstance(content, tuple):  # fila "Actividad": etiqueta + barras
            key, monthly = content
            out.append(f'<g class="l"{delay}><text x="{PAD}" y="{y:.0f}" xml:space="preserve">'
                       f'<tspan fill="{GREEN}" font-weight="bold">{key}:</tspan></text>'
                       f'{bars(monthly, PAD + KEY_COLS * CW, y - FS + 4, 0.3 + i * 0.09)}</g>')
        elif content:
            out.append(f'<text class="l" x="{PAD}" y="{y:.0f}" xml:space="preserve"{delay}>{content}</text>')
        y += LH

    # paleta de colores estilo neofetch
    sw = 44
    out.append(f'<g class="l" style="animation-delay:{0.3 + len(lines) * 0.09:.2f}s">' if not STATIC else "<g>")
    out += [f'<rect x="{PAD + i * sw}" y="{y - FS:.0f}" width="{sw}" height="{FS + 4}" fill="{c}"/>'
            for i, c in enumerate(PALETTE)]
    out.append("</g>")

    anim = "" if STATIC else (
        ".l{opacity:0;animation:in .45s ease-out both}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}")
    body = f'<g font-size="{FS}" fill="{FG}">' + "\n".join(out) + "</g>"
    svg = window(f"{USER_HOST}: ~$ neofetch", body, anim)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)} (contenido hasta y={y:.0f})")


if __name__ == "__main__":
    main()
