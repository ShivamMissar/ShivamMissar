"""Neofetch-style info card -> assets/info-card-{dark,light}.svg

Edit LINES below when your details change, then re-run (or push and let the
workflow do it). Each line fades/slides in on a short stagger; STATIC=1 freezes it.
"""
import os

from theme import THEMES, FONT, STATIC, ASSETS, esc, window

W, H = 490, 400
X, Y0, LH, FS = 20, 58, 20, 12.5
CW = FS * 0.6
KEYW = 10  # key column width in characters

LINES = [
    ("Role", "Technical Consultant @ XMA"),
    ("Focus", "HaloPSA · SQL automation · Outlook-safe HTML"),
    ("Stack", "C# · ASP.NET Core · React · SQL"),
    ("Also", "JavaScript · Python · Node.js · Tailwind"),
    ("Degrees", "BSc SE (First) · MSc Software Dev (Merit)"),
    ("Building", "Ticketmail Builder"),
    ("Shipped", "Locana · NHS ED Sim · Book Club"),
    ("Ways", "ITIL 4 · Scrum · REST API design"),
    ("Hobby", "Photography → @framedbysm"),
    ("Web", "shivammissar.app"),
]


def build(theme):
    t = THEMES[theme]
    els = []

    def line(i, inner):
        y = Y0 + i * LH
        if STATIC:
            return f'<g transform="translate(0 {y})">{inner}</g>'
        return (f'<g transform="translate(0 {y})"><g class="l" style="animation-delay:{0.5 + i * 0.12:.2f}s">'
                f'{inner}</g></g>')

    els.append(line(0, f'<text x="{X}" y="0"><tspan fill="{t["user"]}" font-weight="700">shivam</tspan>'
                       f'<tspan fill="{t["text"]}">@</tspan><tspan fill="{t["host"]}" font-weight="700">github</tspan></text>'))
    els.append(line(1, f'<text x="{X}" y="0" fill="{t["muted"]}">{"-" * 13}</text>'))
    for n, (k, v) in enumerate(LINES, start=2):
        els.append(line(n, f'<text x="{X}" y="0" fill="{t["key"]}" font-weight="700">{esc(k)}</text>'
                           f'<text x="{X + KEYW * CW}" y="0" fill="{t["text"]}">{esc(v)}</text>'))
    n = len(LINES) + 3
    blocks = "".join(f'<rect x="{X + j * 26}" y="-11" width="22" height="14" rx="2" fill="{c}"/>'
                     for j, c in enumerate(t["blocks"]))
    els.append(line(n, blocks))
    n += 2
    cursor = (f'<rect x="{X + 18 * CW:.1f}" y="-11" width="{CW:.1f}" height="15" fill="{t["accent"]}">'
              + ("" if STATIC else '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>')
              + '</rect>')
    els.append(line(n, f'<text x="{X}" y="0"><tspan fill="{t["user"]}">shivam@github</tspan>'
                       f'<tspan fill="{t["key"]}"> ~ </tspan><tspan fill="{t["text"]}">$</tspan></text>{cursor}'))

    style = "" if STATIC else (
        "<style>.l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}</style>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{style}'
           f'{window(t, W, H, "neofetch")}'
           f'<g font-family="{FONT}" font-size="{FS}">{"".join(els)}</g></svg>')
    path = os.path.join(ASSETS, f"info-card-{theme}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print("wrote", path)


os.makedirs(ASSETS, exist_ok=True)
for th in THEMES:
    build(th)
