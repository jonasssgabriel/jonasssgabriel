"""Gera os SVGs (claro/escuro, desktop/mobile) e o README do perfil.

Conceito "Planta tecnica": folha de desenho de engenharia, grade fina,
cotas, bloco de legenda, azul como unica cor de destaque.

Uso (na raiz do repositorio):  python scripts/build.py
Saida: assets/*.svg e README.md
"""
import math
import os
import re
import urllib.request

SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SF Mono',Consolas,Menlo,monospace"

PAL = {
    "dark": dict(bg="#0e1218", panel="#121821", minor="#161e2b", major="#1d2839", frame="#34415a",
                 text="#eaf0fb", muted="#8795ad", blue="#5b9bff", blue2="#9cc0ff"),
    "light": dict(bg="#fafbfd", panel="#ffffff", minor="#eef2f8", major="#dde5f0", frame="#b4c1d6",
                  text="#0f1623", muted="#566275", blue="#1d5fe0", blue2="#4b83ee"),
}

BASE_CSS = (".once{display:none}"
            ".draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.6s .15s cubic-bezier(.3,.7,.2,1) forwards}"
            "@keyframes draw{to{stroke-dashoffset:0}}"
            ".fade{opacity:0;animation:fade .9s ease-out forwards}@keyframes fade{to{opacity:1}}"
            ".cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
            ".ring{transform-box:fill-box;transform-origin:center;animation:ring 3.2s ease-out infinite}"
            "@keyframes ring{0%{transform:scale(.35);opacity:.9}100%{transform:scale(1.7);opacity:0}}"
            ".flow{stroke-dasharray:4 7;animation:flow 1.6s linear infinite}@keyframes flow{to{stroke-dashoffset:-22}}"
            ".bob{animation:bob 4s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-4px)}}")

REDUCED = ("@media (prefers-reduced-motion:reduce){"
           ".ring,.flow,.bob,.cur{animation:none!important}.live{display:none}.once{display:inline}}")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return (f"{v:.5f}".rstrip("0").rstrip(".")) or "0"


def svg(w, h, body, label="", defs="", extra_css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f"<style>{BASE_CSS}{extra_css}{REDUCED}</style><defs>{defs}</defs>{body}</svg>")


def grid_defs(P):
    return (f'<pattern id="gm" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M12 0H0V12" fill="none" stroke="{P["minor"]}" stroke-width="1"/></pattern>'
            f'<pattern id="gM" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0H0V60" fill="none" stroke="{P["major"]}" stroke-width="1"/></pattern>')


def sheet(P, W, H, r=12):
    return (f'<rect width="{W}" height="{H}" rx="{r}" fill="{P["bg"]}"/><rect width="{W}" height="{H}" rx="{r}" fill="url(#gm)"/>'
            f'<rect width="{W}" height="{H}" rx="{r}" fill="url(#gM)"/>'
            f'<path class="draw" pathLength="1" d="M14 14H{W-14}V{H-14}H14Z" fill="none" stroke="{P["frame"]}" stroke-width="1.3"/>')


def mark(P, cx, cy, delay=0):
    return (f'<g class="fade" style="animation-delay:{delay}s" stroke="{P["blue"]}" stroke-width="1.2" fill="none">'
            f'<path d="M{cx-9} {cy}h18M{cx} {cy-9}v18"/><circle cx="{cx}" cy="{cy}" r="4.5"/></g>')


# ------------------------------------------------------------------ hero
LINES = [
    ("Olá, meu nome é Jonas Gabriel", 3.6),
    ("Estudante de Ciência da Computação", 2.4),
    ("Web, mobile e sistemas", 2.4),
    ("IA aplicada a projetos de software", 2.4),
]


def hero(mode, mobile=False):
    P = PAL[mode]
    if mobile:
        W, H, FS, x0, yb, bw, bh, lab, val, cm = 520, 330, 22, 40, 150, 270, 84, 10.5, 13.5, 40
    else:
        W, H, FS, x0, yb, bw, bh, lab, val, cm = 900, 360, 38, 64, 186, 300, 84, 10.5, 14, 44
    CW = FS * 0.6
    t_per, e_per, gap = 0.07, 0.022, 0.5
    segs, cur = [], 0.0
    for text, hold in LINES:
        n = len(text)
        a = cur
        b = a + n * t_per
        c = b + hold
        d = c + n * e_per
        segs.append((a, b, c, d))
        cur = d + gap
    T = cur
    body = [sheet(P, W, H)]
    for x in range(74, W - 14, 60):
        body.append(f'<path d="M{x} 14v7M{x} {H-14}v-7" stroke="{P["frame"]}" stroke-width="1"/>')
    for y in range(74, H - 14, 60):
        body.append(f'<path d="M14 {y}h7M{W-14} {y}h-7" stroke="{P["frame"]}" stroke-width="1"/>')
    for cx, cy in ((cm, cm), (W - cm, cm), (cm, H - cm), (W - cm, H - cm)):
        body.append(mark(P, cx, cy))
    body.append(f'<text class="fade" x="{cm+28}" y="{cm+6}" font-family="{MONO}" font-size="{11.5 if mobile else 12.5}" letter-spacing="1.3" fill="{P["muted"]}" style="animation-delay:.4s">github.com/jonasssgabriel</text>')
    live = []
    for i, ((text, hold), (a, b, c, d)) in enumerate(zip(LINES, segs)):
        n = len(text)
        w = n * CW
        times, widths = [0.0], [0.0]
        for j in range(1, n + 1):
            times.append((a + j * t_per) / T)
            widths.append(j * CW)
        for k in range(1, n + 1):
            times.append((c + k * e_per) / T)
            widths.append((n - k) * CW)
        kt = ";".join(f(v) for v in times)
        wv = ";".join(f(v) for v in widths)
        xv = ";".join(f(x0 + 5 + v) for v in widths)
        okt, ov = (f"0;{f(d / T)}", "1;0") if a == 0 else (f"0;{f(a / T)};{f(d / T)}", "0;1;0")
        dur = f'dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"'
        full = i == 0
        live.append(f'<clipPath id="cp{i}"><rect x="{x0}" y="{yb-FS}" width="{f(w) if full else 0}" height="{FS+24}"><animate attributeName="width" {dur} keyTimes="{kt}" values="{wv}"/></rect></clipPath>')
        live.append(f'<g clip-path="url(#cp{i})"><text x="{x0}" y="{yb}" font-family="{MONO}" font-size="{FS}" font-weight="600" fill="{P["text"]}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(text)}</text>'
                    f'<path d="M{x0} {yb+18}H{x0+w:.1f}M{x0} {yb+12}v12M{x0+w:.1f} {yb+12}v12" stroke="{P["blue"]}" stroke-width="1.4" fill="none"/></g>')
        live.append(f'<g class="cur"><rect x="{f(x0 + 5 + (w if full else 0))}" y="{yb-FS+6}" width="{FS*.32:.1f}" height="{FS-2}" fill="{P["blue"]}" opacity="{1 if full else 0}">'
                    f'<animate attributeName="x" {dur} keyTimes="{kt}" values="{xv}"/><animate attributeName="opacity" {dur} keyTimes="{okt}" values="{ov}"/></rect></g>')
    body.append(f'<g class="live">{"".join(live)}</g>')
    t0, n0 = LINES[0][0], len(LINES[0][0])
    w0 = n0 * CW
    a0, b0 = 0.4, 0.4 + n0 * t_per
    ts = [0.0] + [(j * t_per) / (b0 - a0) for j in range(1, n0 + 1)]
    ts = [min(v, 1.0) for v in ts]
    ts[-1] = 1.0
    kt1 = ";".join(f(v) for v in ts[:-1]) + ";1"
    wv1 = ";".join(f(j * CW) for j in range(0, n0 + 1))
    durn = f'begin="0.4s" dur="{n0 * t_per:.2f}s" repeatCount="1" fill="freeze" calcMode="discrete"'
    body.append(f'<g class="once"><clipPath id="cpo"><rect x="{x0}" y="{yb-FS}" width="0" height="{FS+24}"><animate attributeName="width" {durn} keyTimes="{kt1}" values="{wv1}"/></rect></clipPath>'
                f'<g clip-path="url(#cpo)"><text x="{x0}" y="{yb}" font-family="{MONO}" font-size="{FS}" font-weight="600" fill="{P["text"]}" textLength="{w0:.1f}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(t0)}</text>'
                f'<path d="M{x0} {yb+18}H{x0+w0:.1f}M{x0} {yb+12}v12M{x0+w0:.1f} {yb+12}v12" stroke="{P["blue"]}" stroke-width="1.4" fill="none"/></g></g>')
    bx, by = W - 30 - bw, H - 30 - bh
    rows = (("AUTOR", "Jonas Gabriel"), ("CURSO", "Ciência da Computação"), ("LOCAL", "Palmas, Tocantins"))
    rh = bh / 3
    tb = [f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{P["bg"]}" stroke="{P["frame"]}" stroke-width="1.3"/>']
    for k, (lb, vl) in enumerate(rows):
        y = by + k * rh
        if k:
            tb.append(f'<path d="M{bx} {y}H{bx+bw}" stroke="{P["frame"]}" stroke-width="1"/>')
        tb.append(f'<text x="{bx+14}" y="{y+rh/2+4}" font-family="{MONO}" font-size="{lab}" letter-spacing="1.2" fill="{P["muted"]}">{lb}</text>'
                  f'<text x="{bx+88}" y="{y+rh/2+5}" font-family="{SANS}" font-size="{val}" font-weight="600" fill="{P["text"]}">{esc(vl)}</text>')
    tb.append(f'<path d="M{bx+78} {by}V{by+bh}" stroke="{P["frame"]}" stroke-width="1"/><rect x="{bx}" y="{by}" width="4" height="{bh}" fill="{P["blue"]}"/>')
    body.append(f'<g class="fade" style="animation-delay:.9s">{"".join(tb)}</g>')
    return svg(W, H, "".join(body), "Jonas Gabriel, estudante de Ciência da Computação em Palmas, TO. Desenvolvimento web, mobile e sistemas.", grid_defs(P))


# ------------------------------------------------------------------ faixa de seção
def strip(mode, num, title, mobile=False):
    P = PAL[mode]
    W, H = (520, 52) if mobile else (900, 60)
    tw = len(title) * 13.2
    x1 = 56 + tw + 18
    body = [f'<text x="4" y="{H*.63:.0f}" font-family="{MONO}" font-size="14" font-weight="600" fill="{P["blue"]}">{num}</text>',
            f'<text x="42" y="{H*.66:.0f}" font-family="{SANS}" font-size="22" font-weight="700" fill="{P["text"]}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(title)}</text>',
            f'<path class="draw" pathLength="1" d="M{x1:.0f} {H*.55:.0f}H{W-4}" stroke="{P["frame"]}" stroke-width="1.3" fill="none"/>']
    ticks, x, k = [], x1 + 10, 0
    while x < W - 6:
        ticks.append(f'M{x:.0f} {H*.55:.0f}v{-9 if k % 5 == 0 else -5}')
        x += 20
        k += 1
    body.append(f'<path class="fade" style="animation-delay:.5s" d="{"".join(ticks)}" stroke="{P["blue"]}" stroke-width="1.2" fill="none" opacity=".85"/>')
    return svg(W, H, "".join(body), f"{num} {title}")


# ------------------------------------------------------------------ placas de projeto
def plate(mode, idx, title, kicker, art, badge, mobile=False):
    P = PAL[mode]
    if mobile:
        W, H, artx, ifs, tfs, tx, ix, kfs = 520, 168, 330, 52, 26, 100, 22, 11
    else:
        W, H, artx, ifs, tfs, tx, ix, kfs = 900, 190, 560, 76, 34, 170, 34, 12.5
    cx, cy = artx + (W - artx) / 2, H / 2
    body = [f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="12" fill="{P["panel"]}" stroke="{P["frame"]}" stroke-width="1.3"/>',
            f'<clipPath id="art"><rect x="{artx}" y="1" width="{W-artx-1}" height="{H-2}" rx="11"/></clipPath>',
            f'<g clip-path="url(#art)"><rect x="{artx}" y="0" width="{W-artx}" height="{H}" fill="url(#gm)"/><rect x="{artx}" y="0" width="{W-artx}" height="{H}" fill="url(#gM)"/></g>',
            f'<path d="M{artx} 14V{H-14}" stroke="{P["frame"]}" stroke-width="1" stroke-dasharray="3 5"/>',
            f'<text x="{ix}" y="{H/2+ifs*.3:.0f}" font-family="{MONO}" font-size="{ifs}" font-weight="700" fill="none" stroke="{P["blue"]}" stroke-width="1.3" opacity=".9">{idx}</text>',
            f'<text x="{tx}" y="{H/2-4:.0f}" font-family="{SANS}" font-size="{tfs}" font-weight="800" fill="{P["text"]}" letter-spacing="-.5">{esc(title)}</text>',
            f'<text x="{tx+1}" y="{H/2+kfs+14:.0f}" font-family="{MONO}" font-size="{kfs}" letter-spacing="1" fill="{P["muted"]}">{esc(kicker)}</text>',
            f'<text x="{W-22}" y="30" text-anchor="end" font-family="{MONO}" font-size="{9.5 if mobile else 11}" letter-spacing="1.2" fill="{P["muted"]}">{esc(badge)}</text>']
    if art == "pin":
        body.append(f'<g clip-path="url(#art)"><g fill="none" stroke="{P["frame"]}" stroke-width="1.2" opacity=".9">'
                    f'<path d="M{artx} {H*.32:.0f}C{artx+50} {H*.4:.0f} {artx+90} {H*.2:.0f} {artx+160} {H*.33:.0f}S{artx+260} {H*.48:.0f} {W} {H*.36:.0f}"/>'
                    f'<path d="M{artx} {H*.72:.0f}C{artx+60} {H*.6:.0f} {artx+100} {H*.85:.0f} {artx+170} {H*.74:.0f}S{artx+270} {H*.62:.0f} {W} {H*.78:.0f}"/>'
                    f'<path d="M{artx+50} 0C{artx+60} {H*.3:.0f} {artx+40} {H*.6:.0f} {artx+68} {H}"/><path d="M{artx+200} 0C{artx+190} {H*.35:.0f} {artx+230} {H*.65:.0f} {artx+210} {H}"/></g></g>'
                    f'<g stroke="{P["blue"]}" fill="none" stroke-width="1.6">' + "".join(f'<circle class="ring" style="animation-delay:{k*1.1}s" cx="{cx:.0f}" cy="{cy+10:.0f}" r="{44 if mobile else 52}"/>' for k in range(3)) + '</g>'
                    f'<g class="bob"><path d="M{cx:.0f} {cy+24:.0f}c-16-16-22-26-22-36a22 22 0 0 1 44 0c0 10-6 20-22 36z" fill="{P["blue"]}"/><circle cx="{cx:.0f}" cy="{cy-12:.0f}" r="8" fill="{P["panel"]}"/></g>')
    else:
        rx_, ry_ = ((W - artx) / 2 - 30, H * .32) if mobile else (78, 62)
        pts = [(cx + rx_ * math.cos(math.radians(a)), cy + ry_ * math.sin(math.radians(a))) for a in (-90, -18, 54, 126, 198)]
        body.append(f'<g stroke="{P["blue"]}" stroke-width="1.5" fill="none" opacity=".8">' + "".join(f'<path class="flow" style="animation-delay:{i*.25}s" d="M{cx:.0f} {cy:.0f}L{x:.0f} {y:.0f}"/>' for i, (x, y) in enumerate(pts)) + '</g>')
        poly = "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
        body.append(f'<path d="M{poly}Z" fill="none" stroke="{P["frame"]}" stroke-width="1.1" stroke-dasharray="2 6"/>')
        body.append("".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{P["panel"]}" stroke="{P["blue"]}" stroke-width="1.6"/><circle cx="{x:.0f}" cy="{y:.0f}" r="3" fill="{P["blue"]}"/>' for x, y in pts))
        body.append(f'<circle class="ring" cx="{cx:.0f}" cy="{cy:.0f}" r="26" fill="none" stroke="{P["blue"]}" stroke-width="1.4"/><circle cx="{cx:.0f}" cy="{cy:.0f}" r="15" fill="{P["blue"]}"/>')
    return svg(W, H, "".join(body), f"{idx} {title}. {kicker}", grid_defs(P))


# ------------------------------------------------------------------ rodape
def footer(mode, mobile=False):
    P = PAL[mode]
    W, H = (520, 124) if mobile else (900, 150)
    m = 40 if mobile else 84
    body = [sheet(P, W, H),
            mark(P, 44, 44) + mark(P, W - 44, H - 44),
            f'<text class="fade" x="{m}" y="{H/2+4:.0f}" font-family="{SANS}" font-size="{22 if mobile else 26}" font-weight="800" fill="{P["text"]}" style="animation-delay:.4s">Jonas Gabriel</text>',
            f'<text class="fade" x="{m+1}" y="{H/2+26:.0f}" font-family="{MONO}" font-size="{10.5 if mobile else 12.5}" letter-spacing="1" fill="{P["muted"]}" style="animation-delay:.5s">PALMAS, TOCANTINS  /  2026</text>',
            f'<rect x="{W-m-4}" y="{H/2-24:.0f}" width="4" height="52" fill="{P["blue"]}"/>',
            f'<text class="fade" x="{W-m-16}" y="{H/2:.0f}" text-anchor="end" font-family="{MONO}" font-size="{10.5 if mobile else 12}" letter-spacing="1.2" fill="{P["muted"]}" style="animation-delay:.6s">FOLHA 1 DE 1</text>',
            f'<text class="fade" x="{W-m-16}" y="{H/2+22:.0f}" text-anchor="end" font-family="{SANS}" font-size="{12.5 if mobile else 14}" font-weight="600" fill="{P["text"]}" style="animation-delay:.6s">Obrigado pela visita</text>']
    return svg(W, H, "".join(body), "Jonas Gabriel, Palmas, Tocantins", grid_defs(P))


# ------------------------------------------------------------------ pacman recolorido
PAC_DARK = {"#0d1117": "#0e1218", "#161b22": "#171f2d", "#0e4429": "#1f3d73", "#006d32": "#2f66c4",
            "#26a641": "#5b9bff", "#39d353": "#b0cdff", "#8b949e": "#8795ad"}
PAC_LIGHT = {"#ffffff": "#fafbfd", "#ebedf0": "#e7edf6", "#9be9a8": "#c0d4f8", "#40c463": "#84a9ef",
             "#30a14e": "#4580e2", "#216e39": "#1d5fe0", "#57606a": "#566275", "#000000": "#0f1623"}


def pacman(mode, src_dir):
    name = "pacman-contribution-graph" + ("-dark" if mode == "dark" else "")
    path = os.path.join(src_dir, name + ".svg")
    if os.path.exists(path):
        s = open(path, encoding="utf-8").read()
    else:
        s = urllib.request.urlopen(f"https://raw.githubusercontent.com/jonasssgabriel/jonasssgabriel/output/{name}.svg?z={os.getpid()}").read().decode()
    m = PAC_DARK if mode == "dark" else PAC_LIGHT
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda x: m.get(x.group(0).lower(), x.group(0)), s)


# ------------------------------------------------------------------ README
def pic(name, alt, mobile=True):
    src = ""
    if mobile:
        src += (f'  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{name}-mobile-dark.svg">\n'
                f'  <source media="(max-width: 600px) and (prefers-color-scheme: light)" srcset="assets/{name}-mobile-light.svg">\n')
    src += (f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n')
    return f'<picture>\n{src}  <img alt="{alt}" src="assets/{name}-light.svg" width="100%">\n</picture>'


def readme():
    return f"""{pic("hero", "Jonas Gabriel, estudante de Ciência da Computação em Palmas, TO. Desenvolvimento web, mobile e sistemas.")}

{pic("sec-sobre", "01 Sobre")}

Estudo Ciência da Computação no CEULP/ULBRA, em Palmas (TO), e desenvolvo software: aplicações web, aplicativos mobile, sistemas e projetos próprios. Hoje divido o tempo entre o **MedLocate**, um aplicativo para encontrar serviços de saúde na cidade, e o **SoluCode OS**, um sistema interno que coordena agentes de IA.

{pic("sec-projetos", "02 Projetos")}

{pic("plate-medlocate", "01 MedLocate. Aplicativo mobile.")}

`React Native` `Expo` `Node.js` `PostgreSQL` `GitHub Actions`

Aplicativo para encontrar unidades de saúde e farmácias de Palmas (UBS, USF, UPA, hospitais e farmácias). Mostra no mapa o que está por perto, permite buscar por região, avaliar, favoritar e avisar quando um dado está incorreto. Projeto acadêmico em equipe, com API própria e integração contínua. O repositório é privado.

{pic("plate-solucode", "02 SoluCode OS. Sistema interno.")}

`TypeScript` `Claude Code` `Codex`

Sistema interno da SoluCode, hoje em fase de pesquisa e arquitetura: Command Center, base de conhecimento, documentação viva e coordenação de agentes de IA, com decisões registradas em formato ADR. O repositório é privado.

**Outros trabalhos**

- **RegEx Elite**: aplicação web didática sobre linguagens regulares e expressões regulares, feita em grupo para Linguagens Formais. [Código](https://github.com/jonasssgabriel/ConjuntosRegularesSystem) | [Demo](https://jonasssgabriel.github.io/ConjuntosRegularesSystem/)
- **PDV Web**: ponto de venda executado no navegador, com impressão térmica em papel de 80 mm e dados no LocalStorage. [Código](https://github.com/jonasssgabriel/pdv-web) | [Demo](https://jonasssgabriel.github.io/pdv-web/)
- **Aplicação em três camadas com Docker**: frontend em Nginx, API interna e Redis atrás de proxy reverso, com rede isolada. [Código](https://github.com/jonasssgabriel/aplicacao-tres-camadas-docker)
- **Chat TCP multiusuário**: cliente e servidor em Java com sockets, pool de threads e protocolo em JSON. [Código](https://github.com/jonasssgabriel/chat-tcp-multiusuario)
- **Classificador de roupas com CNN**: rede neural convolucional com TensorFlow e Keras e interface em Gradio, feita em dupla. [Código](https://github.com/Luckleal/reconhecimento-roupas-cnn)

{pic("sec-stack", "03 Stack")}

- **Linguagens:** `TypeScript` `JavaScript` `Python` `Java` `PHP`
- **Web e mobile:** `React` `React Native` `Expo` `Vite` `HTML` `CSS`
- **Back-end e dados:** `Node.js` `PostgreSQL` `MongoDB` `Redis` `KNIME`
- **Infraestrutura:** `Docker` `Nginx` `GitHub Actions` `Git`
- **IA:** `Claude Code` `Codex` `TensorFlow` `Keras` `Gradio`

{pic("sec-atividade", "04 Atividade")}

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jonasssgabriel/jonasssgabriel/output/pacman-contribution-graph-dark.svg?v=6">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/jonasssgabriel/jonasssgabriel/output/pacman-contribution-graph.svg?v=6">
  <img alt="Pac-Man comendo os commits do último ano" src="https://raw.githubusercontent.com/jonasssgabriel/jonasssgabriel/output/pacman-contribution-graph.svg?v=6" width="100%">
</picture>

{pic("sec-contato", "05 Contato")}

[jonassgabriel433@gmail.com](mailto:jonassgabriel433@gmail.com)

{pic("footer", "Jonas Gabriel, Palmas, Tocantins")}
"""


def main(src_dir="."):
    os.makedirs("assets", exist_ok=True)
    jobs = {}
    for mode in ("dark", "light"):
        for mob in (False, True):
            sfx = f"-mobile-{mode}" if mob else f"-{mode}"
            jobs[f"hero{sfx}"] = hero(mode, mob)
            for key, num, title in (("sobre", "01", "Sobre"), ("projetos", "02", "Projetos"), ("stack", "03", "Stack"),
                                    ("atividade", "04", "Atividade"), ("contato", "05", "Contato")):
                jobs[f"sec-{key}{sfx}"] = strip(mode, num, title, mob)
            jobs[f"plate-medlocate{sfx}"] = plate(mode, "01", "MedLocate", "APP MOBILE / PROJETO ACADÊMICO", "pin", "REPOSITÓRIO PRIVADO", mob)
            jobs[f"plate-solucode{sfx}"] = plate(mode, "02", "SoluCode OS", "SISTEMA INTERNO / AGENTES DE IA", "agents", "REPOSITÓRIO PRIVADO", mob)
            jobs[f"footer{sfx}"] = footer(mode, mob)
    for name, content in jobs.items():
        open(f"assets/{name}.svg", "w", encoding="utf-8").write(content)
    open("README.md", "w", encoding="utf-8").write(readme())
    print("ok", len(jobs), "svgs")


if __name__ == "__main__":
    main()
