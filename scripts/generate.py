"""Gera assets/header.svg e assets/commits.svg do README.

Uso: python scripts/generate.py cal.json
cal.json vem de: gh api graphql (contributionCalendar do usuario)
"""
import json
import random
import sys
from datetime import date
from xml.sax.saxutils import escape

PAPER = "#efe9dc"
INK = "#22201c"
BLUE = "#2748a8"
MARK = "#f6d84c"
RULE = "#c7d3e4"
MUTED = "#6f6a5e"
MONO = "'Courier New',Courier,monospace"
SERIF = "Georgia,'Times New Roman',serif"
CW = 12  # largura de um caractere monoespacado a 20px


def mono(x, y, s, size=20, fill=INK, extra=""):
    w = len(s) * size * 0.6
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
            f'textLength="{w:.0f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve" {extra}>{escape(s)}</text>')


def header():
    W, H = 900, 340
    lines = [
        "Estudo Ciência da Computação em Palmas, Tocantins.",
        "Mexo com um pouco de tudo: site, API, banco, dashboard, rede.",
        "Ultimamente muito com agentes e workflows de IA, testando",
        "qual o jeito certo de encaixar isso dentro de um projeto.",
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'role="img" aria-label="Oi, eu sou o Jonas. Estudo Ciência da Computação em Palmas, Tocantins. Mexo com um pouco de tudo e, ultimamente, com agentes e workflows de IA.">']
    out.append("""<style>
.hl{transform-box:fill-box;transform-origin:left center;animation:swipe .7s .25s cubic-bezier(.3,.7,.2,1) both}
@keyframes swipe{from{transform:scaleX(0) rotate(-1deg)}to{transform:scaleX(1) rotate(-1deg)}}
.pen{stroke-dasharray:1;stroke-dashoffset:1;animation:ink 1.1s 1.1s ease-out forwards}
@keyframes ink{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){.hl,.pen{animation:none;stroke-dashoffset:0}}
</style>""")
    out.append(f"""<defs>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .2  0 0 0 0 .17  0 0 0 0 .1  0 0 0 .09 0"/></filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="2" seed="2" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3"/></filter>
</defs>""")
    out.append(f'<rect width="{W}" height="{H}" rx="4" fill="{PAPER}"/>')
    for k in range(8):
        y = 82 + 32 * k
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{RULE}" stroke-width="1.2"/>')
    out.append(f'<line x1="76" y1="0" x2="76" y2="{H}" stroke="#e39a9a" stroke-width="1.4"/>')
    out.append(f'<rect width="{W}" height="{H}" rx="4" filter="url(#grain)"/>')
    # fita no canto
    out.append('<rect x="760" y="-8" width="120" height="34" fill="#d8cfb4" opacity=".85" transform="rotate(8 820 10)"/>')
    # titulo com marca-texto
    out.append(f'<rect class="hl" x="494" y="72" width="214" height="46" fill="{MARK}" opacity=".85" filter="url(#rough)"/>')
    out.append(f'<text x="100" y="110" font-family="{SERIF}" font-size="54" font-weight="700" fill="{INK}" textLength="378" lengthAdjust="spacingAndGlyphs">Oi, eu sou o</text>')
    out.append(f'<text x="502" y="110" font-family="{SERIF}" font-size="54" font-weight="700" fill="{INK}" textLength="196" lengthAdjust="spacingAndGlyphs">Jonas.</text>')
    base = [174, 206, 238, 270]
    for s, y in zip(lines, base):
        out.append(mono(100, y, s))
    # sublinhado a caneta em "agentes e workflows de IA"
    start = lines[2].index("agentes")
    end = lines[2].index("IA,") + 2
    x1, x2 = 100 + start * CW, 100 + end * CW
    out.append(f'<path class="pen" pathLength="1" d="M{x1} 243 C{x1+60} 247 {x1+120} 240 {x1+190} 245 S{x2-40} 242 {x2} 246" '
               f'fill="none" stroke="{BLUE}" stroke-width="2.4" stroke-linecap="round" filter="url(#rough)"/>')
    out.append(f'<text x="100" y="312" font-family="{SERIF}" font-style="italic" font-size="19" fill="{BLUE}" transform="rotate(-.8 100 312)">ps: a ordem dessa lista muda toda semana.</text>')
    out.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="4" fill="none" stroke="#cdc3aa"/>')
    out.append("</svg>")
    return "\n".join(out)


def commits(cal):
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    step, size = 15, 11
    gx, gy = 64, 96
    W = gx + len(weeks) * step + 36
    H = 290
    lvl = {"NONE": None, "FIRST_QUARTILE": "#f3e08c", "SECOND_QUARTILE": "#ecc43a",
           "THIRD_QUARTILE": "#d99a14", "FOURTH_QUARTILE": INK}
    days = sum(1 for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)
    best = max(d["contributionCount"] for w in weeks for d in w["contributionDays"])
    rnd = random.Random(7)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{total} commits no último ano, em {days} dias diferentes">']
    o.append("""<style>
.c{opacity:0;animation:pop .35s ease-out forwards}
@keyframes pop{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.c{animation:none;opacity:1}}
</style>""")
    o.append(f"""<defs>
<pattern id="gp" x="{gx}" y="{gy}" width="{step}" height="{step}" patternUnits="userSpaceOnUse"><path d="M{step} 0H0V{step}" fill="none" stroke="{RULE}" stroke-width="1"/></pattern>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 .2  0 0 0 0 .17  0 0 0 0 .1  0 0 0 .09 0"/></filter>
</defs>""")
    o.append(f'<rect width="{W}" height="{H}" rx="4" fill="{PAPER}"/>')
    o.append(f'<rect x="{gx}" y="{gy}" width="{len(weeks)*step}" height="{7*step}" fill="url(#gp)"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="4" filter="url(#grain)"/>')
    o.append(mono(gx, 46, "commits do último ano", 20))
    o.append(mono(gx, 70, f"{total} commits em {days} dias diferentes", 14, MUTED))
    for i, name in ((1, "seg"), (3, "qua"), (5, "sex")):
        o.append(mono(22, gy + i * step + 9, name, 11, MUTED))
    last_m = None
    for ci, w in enumerate(weeks):
        d0 = date.fromisoformat(w["firstDay"])
        if d0.month != last_m and d0.day <= 14:
            names = "jan fev mar abr mai jun jul ago set out nov dez".split()
            o.append(mono(gx + ci * step, gy - 8, names[d0.month - 1], 11, MUTED))
            last_m = d0.month
        for d in w["contributionDays"]:
            col = lvl[d["contributionLevel"]]
            if not col:
                continue
            x = gx + ci * step + 2 + rnd.uniform(-.6, .6)
            y = gy + d["weekday"] * step + 2 + rnd.uniform(-.6, .6)
            r = rnd.uniform(-4, 4)
            o.append(f'<rect class="c" style="animation-delay:{ci*0.025:.2f}s" x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" '
                     f'rx="2" fill="{col}" transform="rotate({r:.1f} {x+size/2:.1f} {y+size/2:.1f})"/>')
    fy = gy + 7 * step + 34
    o.append(f'<text x="{gx}" y="{fy}" font-family="{SERIF}" font-style="italic" font-size="17" fill="{BLUE}">cada quadrado é um dia, o mais escuro foi o dia de {best} commits.</text>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="4" fill="none" stroke="#cdc3aa"/>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    cal = json.load(open(sys.argv[1]))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    open("assets/header.svg", "w", encoding="utf-8").write(header())
    open("assets/commits.svg", "w", encoding="utf-8").write(commits(cal))
    print("ok")
