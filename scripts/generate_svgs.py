#!/usr/bin/env python3
"""Generate light/dark profile SVGs with a Windows XP logo."""
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "assets" / "windows_xp.png"
COLS, ROWS = 34, 14
RAMP = "@%#*+"
LINE_STEP = 20
FIRST_Y = 30
TOTAL_ROWS = 25
ASCII_X = 33  # 15 + 2 columns (~9px each)
TEXT_X = 400
WIDTH, HEIGHT = 985, 498
RIGHT_WIDTH = 60
LUM_CUTOFF = 22

THEMES = {
    "light_mode.svg": {
        "bg": "#fdf6e3",
        "text": "#657b83",
        "key": "#cb4b16",
        "value": "#268bd2",
        "add": "#859900",
        "del": "#dc322f",
        "cc": "#93a1a1",
    },
    "dark_mode.svg": {
        "bg": "#161b22",
        "text": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "add": "#3fb950",
        "del": "#f85149",
        "cc": "#616e7f",
    },
}


def ascii_cells():
    im = Image.open(PHOTO).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    cells = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            r, g, b = im.getpixel((x, y))
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if lum < LUM_CUTOFF:
                row.append((" ", None))
            else:
                idx = min(len(RAMP) - 1, int((255 - lum) / 255 * len(RAMP)))
                row.append((RAMP[idx], f"#{r:02x}{g:02x}{b:02x}"))
        cells.append(row)
    return cells


def ascii_svg(cells) -> str:
    offset = (TOTAL_ROWS - ROWS) // 2
    lines = []
    for i, row in enumerate(cells):
        y = FIRST_Y + (offset + i) * LINE_STEP
        parts = []
        x = 0
        while x < len(row):
            color = row[x][1]
            j = x + 1
            while j < len(row) and row[j][1] == color:
                j += 1
            chunk = escape("".join(ch for ch, _ in row[x:j]))
            if x == 0:
                attrs = f' x="{ASCII_X}" y="{y}"'
            else:
                attrs = ""
            if color:
                attrs += f' fill="{color}"'
            parts.append(f"<tspan{attrs}>{chunk}</tspan>")
            x = j
        lines.append("".join(parts))
    return "\n".join(lines)


def t(x, y, body, cls=None):
    attrs = f' x="{x}" y="{y}"'
    if cls:
        attrs += f' class="{cls}"'
    return f"<tspan{attrs}>{body}</tspan>"


def kv(y, keys, value, dots=None, value_id=None, dots_id=None):
    parts = [t(TEXT_X, y, ". ", "cc")]
    for i, key in enumerate(keys):
        if i:
            parts.append(".")
        parts.append(f'<tspan class="key">{escape(key)}</tspan>')
    parts.append(":")
    if dots is None:
        prefix = 2 + sum(len(k) for k in keys) + (len(keys) - 1) + 1
        pad = RIGHT_WIDTH - prefix - len(value)
        if pad <= 0:
            dots = " "
        elif pad <= 2:
            dots = {1: " ", 2: ". "}[pad]
        else:
            dots = " " + ("." * (pad - 2)) + " "
    dots_attr = f' id="{dots_id}"' if dots_id else ""
    parts.append(f'<tspan class="cc"{dots_attr}>{escape(dots)}</tspan>')
    val_attr = f' id="{value_id}"' if value_id else ""
    parts.append(f'<tspan class="value"{val_attr}>{escape(value)}</tspan>')
    return "".join(parts)


def section(y, title):
    label = f"- {title}"
    fill = max(1, RIGHT_WIDTH - len(label) - 4)
    dashes = " -" + ("—" * fill) + "-—"
    return t(TEXT_X, y, escape(label)) + escape(dashes)


def loc_line(y):
    suffix = "0 ( 0++, 0-- )"
    prefix = len(". Lines of Code:")
    pad = RIGHT_WIDTH - prefix - len(suffix)
    dots = " " + ("." * (pad - 2)) + " " if pad > 2 else " "
    return (
        t(TEXT_X, y, ". ", "cc")
        + '<tspan class="key">Lines of Code</tspan>:'
        + f'<tspan class="cc" id="loc_data_dots">{escape(dots)}</tspan>'
        + '<tspan class="value" id="loc_data">0</tspan>'
        + ' ( <tspan class="addColor" id="loc_add">0</tspan><tspan class="addColor">++</tspan>, '
        + '<tspan class="delColor" id="loc_del">0</tspan><tspan class="delColor">--</tspan> )'
    )


def build(theme: dict, cells) -> str:
    right = [
        t(TEXT_X, 30, "przemyslaw@feliniak")
        + escape(" -" + ("—" * (RIGHT_WIDTH - len("przemyslaw@feliniak") - 4)) + "-—"),
        kv(50, ["University"], "Warsaw University of Technology"),
        kv(70, ["Major"], "Applied Computer Science"),
        kv(90, ["Uptime"], "10.2025 – Now"),
        t(TEXT_X, 110, ". ", "cc"),
        section(130, "Skills"),
        kv(150, ["Languages", "Programming"], "Go, Python, C, Java"),
        kv(170, ["Stack", "OS"], "Linux, Windows"),
        kv(190, ["Stack", "Cloud"], "Azure"),
        kv(210, ["Stack", "Containers"], "Docker, Kubernetes"),
        kv(230, ["Stack", "Data"], "PostgreSQL, SQLite"),
        kv(250, ["Stack", "DevOps"], "Grafana, Prometheus, GitHub Actions"),
        kv(270, ["Certifications"], "AZ-900"),
        t(TEXT_X, 290, ". ", "cc"),
        section(310, "Profiles"),
        kv(330, ["Email"], "feliniak.przemyslaw@gmail.com"),
        kv(350, ["LinkedIn"], "przemyslaw-felniak"),
        kv(370, ["Boot.dev"], "przem4l"),
        t(TEXT_X, 390, ". ", "cc"),
        section(410, "GitHub Stats"),
        kv(430, ["Repos"], "0", value_id="repo_data", dots_id="repo_data_dots"),
        kv(450, ["Commits"], "0", value_id="commit_data", dots_id="commit_data_dots"),
        loc_line(470),
    ]
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{WIDTH}px" height="{HEIGHT}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {theme["key"]};}}
.value {{fill: {theme["value"]};}}
.addColor {{fill: {theme["add"]};}}
.delColor {{fill: {theme["del"]};}}
.cc {{fill: {theme["cc"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{WIDTH}px" height="{HEIGHT}px" fill="{theme["bg"]}" rx="15"/>
<text x="15" y="30" fill="{theme["text"]}" class="ascii">
{ascii_svg(cells)}
</text>
<text x="{TEXT_X}" y="30" fill="{theme["text"]}">
{chr(10).join(right)}
</text>
</svg>
'''


def main():
    cells = ascii_cells()
    for name, theme in THEMES.items():
        (ROOT / name).write_text(build(theme, cells), encoding="utf-8")
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
