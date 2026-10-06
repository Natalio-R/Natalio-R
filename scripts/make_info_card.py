"""Neofetch-style info card -> info-card.svg. STATIC=1 emits a frozen frame."""
import os
import textwrap
from html import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
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

W = 490
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG, BORDER, BAR, FG, DIM = "#0d1117", "#30363d", "#161b22", "#c9d1d9", "#8b949e"
KEY, ACCENT = "#39d353", "#69f0a0"
FS, LH, PAD, BAR_H = 12.5, 19, 20, 30
KEY_COLS, VAL_COLS = 12, 45  # ~7.5px per char at 12.5px


def lines():
    yield f'<tspan fill="{ACCENT}" font-weight="bold">{USER_HOST}</tspan>'
    yield f'<tspan fill="{DIM}">{"-" * len(USER_HOST)}</tspan>'
    for key, val in ROWS:
        for i, chunk in enumerate(textwrap.wrap(val, VAL_COLS)):
            k = f"{key}:" if key and i == 0 else ""
            yield (f'<tspan fill="{KEY}" font-weight="bold">{escape(k.ljust(KEY_COLS))}</tspan>'
                   f'<tspan fill="{FG}">{escape(chunk)}</tspan>')
    yield ""
    yield "".join(f'<tspan fill="{c}">███</tspan>' for c in
                  ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"))


def main():
    body = list(lines())
    H = BAR_H + PAD + len(body) * LH + PAD - 4
    rows = []
    for i, content in enumerate(body):
        y = BAR_H + PAD + i * LH + FS
        style = "" if STATIC else f' style="animation-delay:{0.25 + i * 0.12:.2f}s"'
        rows.append(f'<text class="l" x="{PAD}" y="{y:.0f}" xml:space="preserve"{style}>{content}</text>')
    anim = "" if STATIC else (
        ".l{opacity:0;animation:in .45s ease-out both}"
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}")
    dots = "".join(f'<circle cx="{18 + i * 18}" cy="{BAR_H / 2}" r="5.5" fill="{c}"/>'
                   for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:{FONT};font-size:{FS}px;fill:{FG}}}{anim}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M.5 {BAR_H}V10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10V{BAR_H}z" fill="{BAR}" stroke="{BORDER}"/>
{dots}
<text x="{W / 2}" y="{BAR_H / 2 + 4}" text-anchor="middle" style="fill:{DIM};font-size:11px">{USER_HOST}: ~ $ neofetch</text>
{chr(10).join(rows)}
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"-> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
