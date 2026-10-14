"""Gera assets/banner.svg (banner estilo arcade com letras de pixel).

Uso: python scripts/generate.py
"""
import math

G = {
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "N": ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
}

YELLOW = "#ffd800"
BLUE = "#2121de"
WHITE = "#e9e9f2"
DOT = "#ffb8ae"


def pixels(text, x, y, cell, fill, gap=1, space=3):
    rects, cx = [], x
    for ch in text:
        if ch == " ":
            cx += space * cell
            continue
        for r, row in enumerate(G[ch]):
            for c, b in enumerate(row):
                if b == "1":
                    rects.append(f'<rect x="{cx + c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}"/>')
        cx += (5 + gap) * cell
    return f'<g fill="{fill}" shape-rendering="crispEdges">{"".join(rects)}</g>', cx - x


def pac_path(deg):
    r = 13
    a = math.radians(deg)
    x, y = r * math.cos(a), r * math.sin(a)
    return f"M0 0L{x:.2f} {-y:.2f}A{r} {r} 0 1 0 {x:.2f} {y:.2f}Z"


def ghost(color, dx):
    return (f'<g transform="translate({dx} 0)"><path d="M-12 13V-1A12 12 0 0 1 12 -1V13L8 9L4 13L0 9L-4 13L-8 9Z" fill="{color}"/>'
            '<circle cx="-4.5" cy="-3" r="3.6" fill="#fff"/><circle cx="4.5" cy="-3" r="3.6" fill="#fff"/>'
            f'<circle cx="-3" cy="-3" r="1.8" fill="{BLUE}"/><circle cx="6" cy="-3" r="1.8" fill="{BLUE}"/></g>')


def header():
    W, H = 900, 270
    name, nw = pixels("JONAS GABRIEL", 0, 0, 9, YELLOW)
    ox = (W - nw) // 2
    name = name.replace('<g ', f'<g transform="translate({ox} 52)" ', 1)
    sub, sw = pixels("IA  UX  DADOS", 0, 0, 4, WHITE)
    sub = sub.replace('<g ', f'<g transform="translate({(W - sw) // 2} 140)" ', 1)

    x0, x1, n = 66, 834, 30
    step = (x1 - x0) / (n - 1)
    cycle, run = 10.0, 7.5
    css = ["@media (prefers-reduced-motion:reduce){.pm,.dot{animation:none!important}}"]
    dots = []
    for i in range(n):
        t = (i * step) / (x1 - x0) * run / cycle * 100
        css.append(f"@keyframes d{i}{{0%,{t:.2f}%{{opacity:1}}{t + .1:.2f}%,99.9%{{opacity:0}}100%{{opacity:1}}}}")
        dots.append(f'<rect class="dot" style="animation:d{i} {cycle}s linear infinite" x="{x0 + i * step - 2.5:.1f}" y="212.5" width="5" height="5" fill="{DOT}"/>')
    travel = x1 - x0
    pct = run / cycle * 100
    css.append(f".pm{{animation:go {cycle}s linear infinite}}")
    css.append(f"@keyframes go{{0%{{transform:translateX(0);opacity:1}}{pct:.2f}%{{transform:translateX({travel}px);opacity:1}}"
               f"{pct + .1:.2f}%,100%{{transform:translateX({travel}px);opacity:0}}}}")
    o, c = pac_path(36), pac_path(2)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Jonas Gabriel. IA, UX, dados.">
<style>{"".join(css)}</style>
<defs><clipPath id="maze"><rect x="16" y="16" width="{W-32}" height="{H-32}" rx="6"/></clipPath></defs>
<rect width="{W}" height="{H}" rx="14" fill="#05060f"/>
<rect x="7" y="7" width="{W-14}" height="{H-14}" rx="10" fill="none" stroke="{BLUE}" stroke-width="3"/>
<rect x="15" y="15" width="{W-30}" height="{H-30}" rx="6" fill="none" stroke="{BLUE}" stroke-width="1.2" opacity=".7"/>
{name}
{sub}
{"".join(dots)}
<g clip-path="url(#maze)"><g transform="translate({x0} 215)"><g class="pm">
<g>{ghost("#ff3b3b", -62)}</g><g>{ghost("#3de1ff", -104)}</g>
<path fill="{YELLOW}" d="{o}"><animate attributeName="d" dur=".36s" repeatCount="indefinite" values="{o};{c};{o}"/></path>
</g></g></g>
</svg>'''
    return svg


if __name__ == "__main__":
    open("assets/banner.svg", "w", encoding="utf-8").write(header())
    print("ok")
