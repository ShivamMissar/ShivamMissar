"""data/contributions.json -> assets/contrib-heatmap-{dark,light}.svg

53x7 grid of rounded cells that drops in diagonally on load (CSS keyframes,
plays once and freezes), plus a Less->More legend and a streak/best-day footer.
"""
import json
import os
from datetime import date

from theme import THEMES, FONT, STATIC, ASSETS, ROOT, window

W = 860
LEFT, TOP_GRID = 46, 96
PITCH, CELL = 14.6, 11.6

data = json.load(open(os.path.join(ROOT, "data", "contributions.json")))
days = data["days"][-371:]

# lay days into Sunday-first week columns, like GitHub
first = date.fromisoformat(days[0]["date"])
offset = first.isoweekday() % 7
cells = []
for i, d in enumerate(days):
    k = i + offset
    cells.append((k // 7, k % 7, d))
weeks = cells[-1][0] + 1
H = int(TOP_GRID + 7 * PITCH + 62)


def fmt_day(iso):
    dt = date.fromisoformat(iso)
    return f"{dt.strftime('%b')} {dt.day}"


def build(theme):
    t = THEMES[theme]
    pal = t["heat"]
    out = [window(t, W, H, "~/contributions.sh")]
    out.append(f'<g font-family="{FONT}">')
    out.append(f'<text x="{LEFT}" y="60" font-size="14" fill="{t["text"]}"><tspan font-weight="700" fill="{t["accent"]}">'
               f'{data["total"]:,}</tspan> contributions in the last year</text>')
    out.append(f'<text x="{W - 20}" y="60" font-size="11" text-anchor="end" fill="{t["muted"]}">updated {data["generated"]}</text>')

    # month labels at the first week each month appears
    week_start = {}
    for w, dow, d in cells:
        week_start.setdefault(w, d["date"])
    prev, last_x = None, -99
    for w in sorted(week_start):
        m = week_start[w][:7]
        x = LEFT + w * PITCH
        if m != prev and x - last_x > 3 * PITCH and w < weeks - 2:
            out.append(f'<text x="{x:.1f}" y="{TOP_GRID - 8}" font-size="10" fill="{t["muted"]}">'
                       f'{date.fromisoformat(week_start[w]).strftime("%b")}</text>')
            last_x = x
        prev = m
    for dow, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{LEFT - 8}" y="{TOP_GRID + dow * PITCH + CELL - 2:.1f}" font-size="10" '
                   f'text-anchor="end" fill="{t["muted"]}">{name}</text>')

    for w, dow, d in cells:
        x, y = LEFT + w * PITCH, TOP_GRID + dow * PITCH
        lvl = max(0, min(4, d["level"]))
        anim = "" if STATIC else f' class="c" style="animation-delay:{0.3 + (w + dow) * 0.018:.3f}s"'
        out.append(f'<rect{anim} x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="2.5" fill="{pal[lvl]}">'
                   f'<title>{d["count"]} on {d["date"]}</title></rect>')

    fy = TOP_GRID + 7 * PITCH + 30
    stats = (f'<tspan fill="{t["muted"]}">streak </tspan><tspan fill="{t["text"]}" font-weight="700">{data["current_streak"]}d</tspan>'
             f'<tspan fill="{t["muted"]}">   ·   longest </tspan><tspan fill="{t["text"]}" font-weight="700">{data["longest_streak"]}d</tspan>'
             f'<tspan fill="{t["muted"]}">   ·   best day </tspan><tspan fill="{t["text"]}" font-weight="700">'
             f'{data["best_day"]["count"]}</tspan><tspan fill="{t["muted"]}"> on {fmt_day(data["best_day"]["date"])}</tspan>')
    out.append(f'<text x="{LEFT}" y="{fy}" font-size="11.5" xml:space="preserve">{stats}</text>')
    lx = W - 20 - 5 * PITCH - 34
    out.append(f'<text x="{lx - 8}" y="{fy}" font-size="10" text-anchor="end" fill="{t["muted"]}">Less</text>')
    for i, c in enumerate(pal):
        out.append(f'<rect x="{lx + i * PITCH:.1f}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    out.append(f'<text x="{lx + 5 * PITCH + 4:.1f}" y="{fy}" font-size="10" fill="{t["muted"]}">More</text>')
    out.append("</g>")

    style = "" if STATIC else (
        "<style>.c{opacity:0;transform-box:fill-box;transform-origin:center;animation:drop .4s ease-out forwards}"
        "@keyframes drop{from{opacity:0;transform:translateY(-7px) scale(.6)}to{opacity:1;transform:none}}</style>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'{style}{"".join(out)}</svg>')
    path = os.path.join(ASSETS, f"contrib-heatmap-{theme}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print("wrote", path)


os.makedirs(ASSETS, exist_ok=True)
for th in THEMES:
    build(th)
