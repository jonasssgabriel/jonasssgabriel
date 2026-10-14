"""Gera assets/perfil.svg com a paleta tirada da propria foto de perfil.

Uso: python scripts/generate.py   (le scripts/avatar.jpg)
"""
import base64
import io

from PIL import Image

BG = "#231a12"
CREAM = "#f4ebbd"
SAND = "#d9c9a3"
GRASS = "#cbc156"
LINE = "#3a2c1e"
SERIF = "Georgia,'Times New Roman',serif"
SANS = "'Segoe UI',Helvetica,Arial,sans-serif"


def photo_uri(path, size=340):
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def banner():
    W, H, PX = 900, 300, 560
    uri = photo_uri("scripts/avatar.jpg")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Jonas Gabriel. Estudante de Ciência da Computação em Palmas, TO. IA, agentes, experiência e design.">
<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<image x="{PX}" y="0" width="340" height="340" preserveAspectRatio="xMidYMin slice" xlink:href="{uri}" href="{uri}"/>
<rect x="{PX}" y="0" width="170" height="{H}" fill="url(#fade)"/>
<text x="64" y="92" font-family="{SANS}" font-size="13" font-weight="600" letter-spacing="3" fill="{GRASS}">ESTUDANTE DE CIÊNCIA DA COMPUTAÇÃO</text>
<text x="62" y="170" font-family="{SERIF}" font-size="62" font-weight="700" fill="{CREAM}" textLength="440" lengthAdjust="spacingAndGlyphs">Jonas Gabriel</text>
<rect x="64" y="192" width="56" height="4" rx="2" fill="{GRASS}"/>
<text x="64" y="236" font-family="{SANS}" font-size="18" fill="{SAND}">Palmas, Tocantins</text>
<text x="64" y="264" font-family="{SANS}" font-size="18" fill="{SAND}">IA, agentes, experiência e design</text>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="none" stroke="{LINE}"/>
</svg>'''


if __name__ == "__main__":
    open("assets/perfil.svg", "w", encoding="utf-8").write(banner())
    print("ok")
