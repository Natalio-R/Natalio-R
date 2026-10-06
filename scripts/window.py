"""Shared macOS-style terminal window chrome. Windows are 840x880 and shown at width 420."""
W, H, BAR = 840, 880, 44
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG_TOP, BG, BORDER, FG, DIM = "#111722", "#0d1117", "#30363d", "#c9d1d9", "#7d8590"
GREEN, NEON = "#39d353", "#69f0a0"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MONTHS = "ene feb mar abr may jun jul ago sep oct nov dic".split()


def window(title, body, style=""):
    dots = "".join(f'<circle cx="{24 + i * 26}" cy="{BAR / 2}" r="8" fill="{c}"/>'
                   for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
<style>{style}</style>
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{BORDER}"/>
<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{BORDER}"/>
{dots}
<text x="{W / 2}" y="{BAR / 2 + 6}" fill="{DIM}" font-size="17" text-anchor="middle">{title}</text>
{body}
</svg>
'''
