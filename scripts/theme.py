"""Shared colours for every generated SVG. Each asset is rendered twice
(dark + light) and the README picks one with <picture> + prefers-color-scheme."""
import os

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "bar": "#21262d",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "ascii": "#d0d7de",
        "accent": "#39d353",
        "key": "#58a6ff",
        "user": "#3fb950",
        "host": "#d2a8ff",
        "warn": "#f0883e",
        "heat": ["#262c36", "#0e4429", "#006d32", "#26a641", "#39d353"],
        "dots": ["#ff5f56", "#ffbd2e", "#27c93f"],
        "blocks": ["#f85149", "#f0883e", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"],
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "bar": "#eaeef2",
        "text": "#24292f",
        "muted": "#57606a",
        "ascii": "#24292f",
        "accent": "#1a7f37",
        "key": "#0969da",
        "user": "#1a7f37",
        "host": "#8250df",
        "warn": "#bc4c00",
        "heat": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "dots": ["#ff5f56", "#ffbd2e", "#27c93f"],
        "blocks": ["#cf222e", "#bc4c00", "#9a6700", "#1a7f37", "#0969da", "#8250df", "#1b7c83", "#24292f"],
    },
}

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
STATIC = os.environ.get("STATIC") == "1"  # STATIC=1 -> frozen final frame, for local previews

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def window(t, width, height, title):
    """Terminal-style window chrome: rounded panel, title bar, traffic-light dots."""
    d = t["dots"]
    return f"""<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{t['panel']}" stroke="{t['border']}"/>
<path d="M0.5 30 V10.5 a10 10 0 0 1 10 -10 H{width-10.5} a10 10 0 0 1 10 10 V30 Z" fill="{t['bar']}"/>
<line x1="0.5" y1="30" x2="{width-0.5}" y2="30" stroke="{t['border']}"/>
<circle cx="18" cy="15.5" r="5.5" fill="{d[0]}"/><circle cx="36" cy="15.5" r="5.5" fill="{d[1]}"/><circle cx="54" cy="15.5" r="5.5" fill="{d[2]}"/>
<text x="{width/2}" y="20" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{t['muted']}">{esc(title)}</text>"""
