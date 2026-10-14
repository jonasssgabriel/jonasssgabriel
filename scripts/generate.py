"""Gera assets/hero.svg: banner arcade com retrato em pixel art e rede neural.

Uso: python scripts/generate.py   (le scripts/avatar.jpg)
"""
import math
import random

from PIL import Image, ImageEnhance

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
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
}

YELLOW, CYAN, MAGENTA, DOT = "#ffd800", "#38e8ff", "#ff3ea5", "#ffb8ae"


def pixels(text, cell, gap=1, space=3):
    rects, cx = [], 0
    for ch in text:
        if ch == " ":
            cx += space * cell
            continue
        for r, row in enumerate(G[ch]):
            for c, b in enumerate(row):
                if b == "1":
                    rects.append(f'<rect x="{cx + c * cell}" y="{r * cell}" width="{cell}" height="{cell}"/>')
        cx += (5 + gap) * cell
    return "".join(rects), cx - gap * cell


def portrait(path, n=44, cell=5):
    im = Image.open(path).convert("RGB").crop((50, 0, 350, 300))
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.25)
    im = im.resize((n, n), Image.BOX).quantize(16, method=Image.MEDIANCUT).convert("RGB")
    out = []
    for y in range(n):
        x = 0
        while x < n:
            c = im.getpixel((x, y))
            x2 = x
            while x2 + 1 < n and im.getpixel((x2 + 1, y)) == c:
                x2 += 1
            out.append(f'<rect x="{x * cell}" y="{y * cell}" width="{(x2 - x + 1) * cell + .4}" height="{cell + .4}" fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"/>')
            x = x2 + 1
    return "".join(out), n * cell


def pac_path(deg):
    r = 13
    a = math.radians(deg)
    x, y = r * math.cos(a), r * math.sin(a)
    return f"M0 0L{x:.2f} {-y:.2f}A{r} {r} 0 1 0 {x:.2f} {y:.2f}Z"


def ghost(color, dx):
    return (f'<g transform="translate({dx} 0)"><path d="M-12 13V-1A12 12 0 0 1 12 -1V13L8 9L4 13L0 9L-4 13L-8 9Z" fill="{color}"/>'
            '<circle cx="-4.5" cy="-3" r="3.6" fill="#fff"/><circle cx="4.5" cy="-3" r="3.6" fill="#fff"/>'
            '<circle cx="-3" cy="-3" r="1.8" fill="#2121de"/><circle cx="6" cy="-3" r="1.8" fill="#2121de"/></g>')


def network(rnd, x0, x1, y0, y1):
    cols = [3, 5, 6, 5, 4, 3]
    xs = [x0 + (x1 - x0) * i / (len(cols) - 1) for i in range(len(cols))]
    layers = []
    for i, k in enumerate(cols):
        ys = [y0 + (y1 - y0) * (j + .5) / k + rnd.uniform(-8, 8) for j in range(k)]
        layers.append([(xs[i] + rnd.uniform(-10, 10), y) for y in ys])
    edges = []
    for a, b in zip(layers, layers[1:]):
        for p in a:
            for q in rnd.sample(b, min(3, len(b))):
                edges.append((p, q))
    lines = "".join(f'<line x1="{p[0]:.0f}" y1="{p[1]:.0f}" x2="{q[0]:.0f}" y2="{q[1]:.0f}"/>' for p, q in edges)
    pulses = []
    for i, (p, q) in enumerate(rnd.sample(edges, 16)):
        col = CYAN if i % 2 else MAGENTA
        pulses.append(f'<line class="pulse" style="animation-delay:{rnd.uniform(0, 5):.1f}s" x1="{p[0]:.0f}" y1="{p[1]:.0f}" x2="{q[0]:.0f}" y2="{q[1]:.0f}" stroke="{col}"/>')
    dots = []
    for li, layer in enumerate(layers):
        for j, (x, y) in enumerate(layer):
            col = CYAN if (li + j) % 2 else MAGENTA
            dots.append(f'<circle class="node" style="animation-delay:{rnd.uniform(0, 3):.1f}s" cx="{x:.0f}" cy="{y:.0f}" r="3.2" fill="{col}"/>')
    return lines, "".join(pulses), "".join(dots)


def banner():
    W, H = 900, 320
    rnd = random.Random(11)
    name, nw = pixels("JONAS GABRIEL", 6)
    sub, sw = pixels("IA  UX  DADOS", 4)
    por, pw = portrait("scripts/avatar.jpg")
    edges, pulses, nodes = network(rnd, 300, 860, 36, 236)

    x0, x1, n = 66, 834, 30
    step = (x1 - x0) / (n - 1)
    cycle, run = 10.0, 7.5
    css = ["@media (prefers-reduced-motion:reduce){*{animation:none!important}}"]
    dots = []
    for i in range(n):
        t = (i * step) / (x1 - x0) * run / cycle * 100
        css.append(f"@keyframes d{i}{{0%,{t:.2f}%{{opacity:1}}{t + .1:.2f}%,99.9%{{opacity:0}}100%{{opacity:1}}}}")
        dots.append(f'<rect style="animation:d{i} {cycle}s linear infinite" x="{x0 + i * step - 2.5:.1f}" y="287.5" width="5" height="5" fill="{DOT}"/>')
    pct = run / cycle * 100
    travel = x1 - x0
    css.append(f".pm{{animation:go {cycle}s linear infinite}}")
    css.append(f"@keyframes go{{0%{{transform:translateX(0);opacity:1}}{pct:.2f}%{{transform:translateX({travel}px);opacity:1}}{pct + .1:.2f}%,100%{{transform:translateX({travel}px);opacity:0}}}}")
    css.append(".net line{stroke:#7a5cff;stroke-width:1;opacity:.22}")
    css.append(".pulse{stroke-width:2;stroke-dasharray:8 120;stroke-linecap:round;opacity:.95;animation:zap 3.6s linear infinite}")
    css.append("@keyframes zap{from{stroke-dashoffset:128}to{stroke-dashoffset:-60}}")
    css.append(".node{animation:blip 3s ease-in-out infinite}@keyframes blip{0%,100%{opacity:.35}50%{opacity:1}}")
    css.append(".gm,.gc{opacity:0}.gm{animation:gm 6s steps(1) infinite}.gc{animation:gc 6s steps(1) infinite}")
    css.append("@keyframes gm{0%,92%{opacity:0;transform:none}93%{opacity:.9;transform:translate(-4px,1px)}95%{opacity:.9;transform:translate(3px,-1px)}96%,100%{opacity:0}}")
    css.append("@keyframes gc{0%,92%{opacity:0;transform:none}93%{opacity:.9;transform:translate(4px,-1px)}95%{opacity:.9;transform:translate(-3px,1px)}96%,100%{opacity:0}}")
    css.append(".cur{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}")
    o, c = pac_path(36), pac_path(2)
    nx, ny = 300, 78
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Jonas Gabriel. IA, UX, dados.">
<style>{"".join(css)}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0620"/><stop offset="1" stop-color="#1c0c45"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#000" opacity=".28"/></pattern>
<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="3"/></filter>
<clipPath id="maze"><rect x="16" y="16" width="{W-32}" height="{H-32}" rx="8"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>
<g clip-path="url(#maze)">
<g class="net">{edges}</g>{pulses}{nodes}
<g transform="translate(44 40)">
<rect x="-6" y="-6" width="{pw+12}" height="{pw+12}" fill="{CYAN}" opacity=".35" filter="url(#glow)"/>
{por}
<rect x="-3" y="-3" width="{pw+6}" height="{pw+6}" fill="none" stroke="{CYAN}" stroke-width="3"/>
</g>
<g transform="translate({nx+4} {ny+4})" fill="{MAGENTA}" shape-rendering="crispEdges" opacity=".9">{name}</g>
<g class="gm" fill="{MAGENTA}" shape-rendering="crispEdges"><g transform="translate({nx} {ny})">{name}</g></g>
<g class="gc" fill="{CYAN}" shape-rendering="crispEdges"><g transform="translate({nx} {ny})">{name}</g></g>
<g transform="translate({nx} {ny})" fill="{YELLOW}" shape-rendering="crispEdges">{name}</g>
<g transform="translate({nx} {ny+74})" fill="{CYAN}" shape-rendering="crispEdges">{sub}<rect class="cur" x="{sw+12}" y="0" width="12" height="28"/></g>
{"".join(dots)}
<g transform="translate({x0} 290)"><g class="pm">
{ghost(MAGENTA, -62)}{ghost(CYAN, -104)}
<path fill="{YELLOW}" d="{o}"><animate attributeName="d" dur=".36s" repeatCount="indefinite" values="{o};{c};{o}"/></path>
</g></g>
</g>
<rect width="{W}" height="{H}" rx="16" fill="url(#scan)"/>
<rect x="7" y="7" width="{W-14}" height="{H-14}" rx="11" fill="none" stroke="{CYAN}" stroke-width="3"/>
<rect x="15" y="15" width="{W-30}" height="{H-30}" rx="7" fill="none" stroke="{MAGENTA}" stroke-width="1.4" opacity=".8"/>
</svg>'''


def button(label, color, filled=False):
    w, h, cell = 200, 48, 3
    glyphs, tw = pixels(label, cell)
    tx, ty = 52 + (w - 52 - 18 - tw) // 2, (h - 7 * cell) // 2
    fg = "#0b0620" if filled else color
    bg = color if filled else "#0b0620"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label.title()}">
<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="8" fill="{bg}" stroke="{color}" stroke-width="3"/>
<polygon points="20,{h/2-8} 20,{h/2+8} 34,{h/2}" fill="{fg}"/>
<g transform="translate({tx} {ty})" fill="{fg}" shape-rendering="crispEdges">{glyphs}</g>
</svg>'''


if __name__ == "__main__":
    for name, label, col, fill in (("projetos", "PROJETOS", CYAN, False), ("stack", "STACK", MAGENTA, False), ("email", "EMAIL", YELLOW, True)):
        open(f"assets/btn-{name}.svg", "w", encoding="utf-8").write(button(label, col, fill))
    open("assets/hero.svg", "w", encoding="utf-8").write(banner())
    print("ok")
