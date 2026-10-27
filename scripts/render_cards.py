#!/usr/bin/env python3
"""
Renders one linked project card per project (assets/cards/<name>.svg and <name>-light.svg) and
the animated "how I work" pipeline (assets/workflow.svg and workflow-light.svg).

Same rules as the banner: GitHub shows README SVGs through <img>, so only CSS and SMIL run, and
every element is fully visible in its base state. Animation only adds a start state ("both"
fill mode), so a viewer that ignores <style>, or asks for reduced motion, sees the finished card.
Text is static (no per-character positioning), which keeps it intact in Safari.

The small graphic on each card is decorative and carries no data; the card says so in its <desc>.

Run via:  python3 scripts/update_profile.py
"""
import html
import textwrap

MONO = 'ui-monospace,"SFMono-Regular","DM Mono",Menlo,Consolas,monospace'
SERIF = 'Georgia,"Times New Roman",serif'

DARK = dict(
    bg="#090A09", bar="#111211", bar_line="#2a2c29", bar_text="#9a9c96", grid="#1a1b1a",
    a="#00FF66", b="#B6FF2E", title="#F4F5F2", body="#c7c9c4", muted="#9a9c96", dim="#3d3f3b",
    chip_bg="#161715", chip_text="#9a9c96", glow_op="0.10", node="#090A09",
)
LIGHT = dict(
    bg="#F4F5F2", bar="#eceeea", bar_line="#c4c7c0", bar_text="#54564f", grid="#e2e3df",
    a="#00A84A", b="#5f9a00", title="#111211", body="#3d3f3b", muted="#54564f", dim="#aab0a3",
    chip_bg="#e6e8e3", chip_text="#3d3f3b", glow_op="0.08", node="#F4F5F2",
)

CW, CH = 640, 250          # card size
VX, VY, VW, VH = 396, 60, 220, 150   # box for the decorative graphic


def esc(s):
    return html.escape(s, quote=True)


# ---- decorative graphics (each fits VX..VX+VW, VY..VY+VH) ---------------------------------

def g_waterfall(p):
    """vanna: P&L split into terms, with a hatched residual."""
    vals = [34, -14, 22, -9, 16, -6]
    out, level, x = [], 96, VX + 6
    for i, v in enumerate(vals):
        h = abs(v) * 1.8
        top = VY + level - (h if v > 0 else 0)
        col = p["a"] if v > 0 else p["dim"]
        out.append(f'<rect class="rise" style="animation-delay:{0.15 * i:.2f}s" x="{x}" y="{top:.1f}" '
                   f'width="24" height="{h:.1f}" rx="2" fill="{col}"/>')
        level += -v * 1.8
        x += 34
    out.append(f'<rect x="{x}" y="{VY + level - 8:.1f}" width="24" height="16" rx="2" fill="none" '
               f'stroke="{p["b"]}" stroke-dasharray="3 3"/>')
    out.append(f'<line x1="{VX}" y1="{VY + 130}" x2="{VX + VW}" y2="{VY + 130}" stroke="{p["dim"]}"/>')
    return "".join(out)


def g_lbo(p):
    """pe-financial-calculator: equity value bridge."""
    steps = [(30, 0), (24, 1), (36, 1), (-18, 1), (60, 2)]
    out, base, x = [], 126, VX + 8
    for i, (v, kind) in enumerate(steps):
        h = abs(v) * 1.5
        top = 126 - h if kind != 1 else (base - h if v > 0 else base)
        col = p["b"] if kind == 2 else (p["a"] if v > 0 else p["dim"])
        out.append(f'<rect class="rise" style="animation-delay:{0.15 * i:.2f}s" x="{x}" y="{VY + top:.1f}" '
                   f'width="30" height="{h:.1f}" rx="2" fill="{col}"/>')
        if kind == 1:
            base = base - v * 1.5
        x += 42
    out.append(f'<line x1="{VX}" y1="{VY + 126}" x2="{VX + VW}" y2="{VY + 126}" stroke="{p["dim"]}"/>')
    return "".join(out)


def g_book(p):
    """microprice-rust: bid and ask queues around a mid-price, with a micro-price marker."""
    bids = [26, 44, 68, 92, 118]
    asks = [20, 34, 50, 66, 82]
    out, cx = [], VX + VW / 2
    for i, h in enumerate(bids):
        out.append(f'<rect class="grow" style="animation-delay:{0.12 * i:.2f}s" x="{cx - 14 - (i + 1) * 20:.0f}" '
                   f'y="{VY + 130 - h}" width="16" height="{h}" rx="2" fill="{p["a"]}" fill-opacity="{0.95 - i * 0.12:.2f}"/>')
    for i, h in enumerate(asks):
        out.append(f'<rect class="grow" style="animation-delay:{0.12 * i:.2f}s" x="{cx + 14 + i * 20:.0f}" '
                   f'y="{VY + 130 - h}" width="16" height="{h}" rx="2" fill="{p["dim"]}"/>')
    out.append(f'<line x1="{cx}" y1="{VY + 8}" x2="{cx}" y2="{VY + 134}" stroke="{p["muted"]}" stroke-dasharray="3 3"/>')
    out.append(f'<circle class="drift" cx="{cx - 9}" cy="{VY + 12}" r="5" fill="{p["b"]}"/>')
    out.append(f'<line x1="{VX}" y1="{VY + 130}" x2="{VX + VW}" y2="{VY + 130}" stroke="{p["dim"]}"/>')
    return "".join(out)


def g_curve(p):
    """quantdeck: equity curve with a drawdown dip."""
    pts = [(0, 108), (24, 100), (46, 104), (70, 84), (94, 90), (118, 62), (142, 74), (166, 44), (190, 38), (214, 22)]
    d = " ".join(f"{'M' if i == 0 else 'L'}{VX + x},{VY + y}" for i, (x, y) in enumerate(pts))
    area = d + f" L{VX + 214},{VY + 130} L{VX},{VY + 130} Z"
    return (f'<path d="{area}" fill="{p["a"]}" fill-opacity="0.08"/>'
            f'<path class="draw" pathLength="1" d="{d}" fill="none" stroke="{p["a"]}" stroke-width="2.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            f'<line x1="{VX}" y1="{VY + 130}" x2="{VX + VW}" y2="{VY + 130}" stroke="{p["dim"]}"/>'
            f'<circle class="blink" cx="{VX + 214}" cy="{VY + 22}" r="4.5" fill="{p["b"]}"/>')


def g_pipe(p):
    """fpga-sim-core: a packet moving through pipeline stages."""
    out, x = [], VX
    labels = ["PCS", "MAC", "ITCH", "BOOK", "DMA"]
    for i, lab in enumerate(labels):
        out.append(f'<rect x="{x}" y="{VY + 44}" width="36" height="46" rx="4" fill="none" stroke="{p["dim"]}"/>'
                   f'<text x="{x + 18}" y="{VY + 72}" text-anchor="middle" font-family=\'{MONO}\' font-size="10" '
                   f'fill="{p["muted"]}">{lab}</text>')
        if i < 4:
            out.append(f'<line x1="{x + 36}" y1="{VY + 67}" x2="{x + 46}" y2="{VY + 67}" stroke="{p["dim"]}"/>')
        x += 46
    out.append(f'<rect class="packet" x="{VX - 2}" y="{VY + 58}" width="12" height="18" rx="3" fill="{p["a"]}"/>')
    out.append(f'<text x="{VX}" y="{VY + 118}" font-family=\'{MONO}\' font-size="11" fill="{p["muted"]}">cycle model, not hardware</text>')
    return "".join(out)


def g_faces(p):
    """photoface: points clustering into groups."""
    centres = [(VX + 52, VY + 46, p["a"]), (VX + 150, VY + 40, p["b"]), (VX + 100, VY + 106, p["muted"])]
    offs = [(-14, -6), (8, -12), (16, 6), (-6, 14), (0, 0), (-18, 8), (12, 16)]
    out = []
    for ci, (cx, cy, col) in enumerate(centres):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{col}" stroke-opacity="0.35" stroke-dasharray="3 4"/>')
        for k, (dx, dy) in enumerate(offs):
            out.append(f'<circle class="pop" style="animation-delay:{0.06 * (ci * 7 + k):.2f}s" cx="{cx + dx}" cy="{cy + dy}" r="4" fill="{col}"/>')
    return "".join(out)


GRAPHICS = {
    "vanna": g_waterfall, "pe-financial-calculator": g_lbo, "microprice-rust": g_book,
    "quantdeck": g_curve, "fpga-sim-core": g_pipe, "photoface": g_faces,
}
FILES = {  # display filename in the window bar
    "vanna": "vanna.py", "pe-financial-calculator": "rivet.js", "microprice-rust": "microprice.rs",
    "quantdeck": "quantdeck.py", "fpga-sim-core": "datapath.cpp", "photoface": "photoface.py",
}

CSS = """
.rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise 8s cubic-bezier(.2,.8,.2,1) infinite}
.grow{transform-box:fill-box;transform-origin:50% 100%;animation:rise 8s cubic-bezier(.2,.8,.2,1) infinite}
.pop{transform-box:fill-box;transform-origin:50% 50%;animation:pop 8s cubic-bezier(.2,.9,.3,1.4) infinite}
.draw{stroke-dasharray:1;stroke-dashoffset:0;animation:draw 8s ease-out infinite}
.blink{animation:blink 2.4s ease-in-out infinite}
.drift{animation:drift 5s ease-in-out infinite alternate}
.packet{animation:packet 3.2s linear infinite}
.sweep{animation:sweep 6s linear infinite}
@keyframes rise{0%,86%{transform:scaleY(1)}87%{transform:scaleY(0)}100%{transform:scaleY(1)}}
@keyframes pop{0%,86%{transform:scale(1)}87%{transform:scale(0)}100%{transform:scale(1)}}
@keyframes draw{0%,86%{stroke-dashoffset:0}87%{stroke-dashoffset:1}100%{stroke-dashoffset:0}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(22px)}}
@keyframes packet{0%{transform:translateX(0);opacity:1}92%{opacity:1}100%{transform:translateX(212px);opacity:0}}
@keyframes sweep{from{transform:translateX(-40px)}to{transform:translateX(680px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def wrap(text, width):
    return textwrap.wrap(text, width=width, break_long_words=False)


def card(project, p):
    name = project["name"]
    lines = wrap(project["summary"], 40)
    assert len(lines) <= 5, (name, len(lines))
    body = "".join(
        f'<text x="28" y="{98 + 20 * i}" font-family=\'{MONO}\' font-size="13" fill="{p["body"]}">{esc(l)}</text>'
        for i, l in enumerate(lines))
    chips, x = "", 28
    for t in project["tags"][:3]:
        w = 14 + 7.4 * len(t)
        chips += (f'<rect x="{x:.0f}" y="{CH - 40}" width="{w:.0f}" height="22" rx="11" fill="{p["chip_bg"]}"/>'
                  f'<text x="{x + w / 2:.0f}" y="{CH - 25}" text-anchor="middle" font-family=\'{MONO}\' '
                  f'font-size="11" fill="{p["chip_text"]}">{esc(t)}</text>')
        x += w + 8
    graphic = GRAPHICS[name](p)
    desc = (f'{project["summary"]} Decorative graphic, no data.')
    return f'''<svg width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
<title id="t">{esc(name)}</title>
<desc id="d">{esc(desc)}</desc>
<defs>
<pattern id="g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
<clipPath id="c"><rect width="{CW}" height="{CH}" rx="14"/></clipPath>
<radialGradient id="o" cx="0.78" cy="0.55" r="0.5"><stop offset="0%" stop-color="{p["a"]}" stop-opacity="{p["glow_op"]}"/><stop offset="100%" stop-color="{p["a"]}" stop-opacity="0"/></radialGradient>
</defs>
<style>{CSS}</style>
<g clip-path="url(#c)">
<rect width="{CW}" height="{CH}" fill="{p["bg"]}"/>
<rect y="30" width="{CW}" height="{CH - 30}" fill="url(#g)"/>
<rect x="340" y="30" width="300" height="{CH - 30}" fill="url(#o)"/>
<rect width="{CW}" height="30" fill="{p["bar"]}"/>
<circle cx="20" cy="15" r="5" fill="#FF5F57"/><circle cx="38" cy="15" r="5" fill="#FEBC2E"/><circle cx="56" cy="15" r="5" fill="#28C840"/>
<text x="{CW // 2}" y="19" text-anchor="middle" font-family='{MONO}' font-size="12" fill="{p["bar_text"]}">{esc(FILES[name])}</text>
<rect y="30" width="{CW}" height="1" fill="{p["bar_line"]}"/>
<text x="28" y="66" font-family='{SERIF}' font-size="26" font-weight="700" fill="{p["title"]}">{esc(name)}</text>
{body}
{chips}
{graphic}
<rect class="sweep" x="0" y="31" width="40" height="{CH - 31}" fill="{p["a"]}" fill-opacity="0.035"/>
<rect x="0.5" y="0.5" width="{CW - 1}" height="{CH - 1}" rx="14" fill="none" stroke="{p["bar_line"]}"/>
</g>
</svg>
'''


STEPS = [
    ("1", "REPRODUCE", "Make the bug fail"),
    ("2", "FIX", "Smallest change"),
    ("3", "TEST", "Fails before, passes after"),
    ("4", "PULL REQUEST", "Plain words, honest scope"),
    ("5", "REVIEW", "Maintainer decides"),
]


def workflow(p):
    W, H = 1200, 220
    step_w, gap, x0 = 196, 38, 36
    out = []
    for i, (n, head, sub) in enumerate(STEPS):
        x = x0 + i * (step_w + gap)
        out.append(
            f'<rect x="{x}" y="64" width="{step_w}" height="104" rx="10" fill="{p["bar"]}" stroke="{p["bar_line"]}"/>'
            f'<text x="{x + 16}" y="92" font-family=\'{MONO}\' font-size="13" fill="{p["a"]}">{n}</text>'
            f'<text x="{x + 16}" y="118" font-family=\'{MONO}\' font-size="15" font-weight="700" fill="{p["title"]}" letter-spacing="1">{head}</text>'
            f'<text x="{x + 16}" y="144" font-family=\'{MONO}\' font-size="12" fill="{p["muted"]}">{esc(sub)}</text>')
        if i < len(STEPS) - 1:
            ax = x + step_w
            out.append(f'<path d="M{ax + 6} 116 L{ax + gap - 6} 116" stroke="{p["dim"]}" stroke-width="2"/>'
                       f'<path d="M{ax + gap - 12} 110 L{ax + gap - 6} 116 L{ax + gap - 12} 122" fill="none" stroke="{p["dim"]}" stroke-width="2"/>')
    end = x0 + 4 * (step_w + gap)
    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="wt wd">
<title id="wt">How I work</title>
<desc id="wd">Five steps for every upstream fix: reproduce the bug, make the smallest fix, add a test that fails before and passes after, open a pull request in plain words, and leave the decision to the maintainer.</desc>
<defs>
<pattern id="wg" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
<clipPath id="wc"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<style>
.pk{{animation:pk 9s linear infinite}}
.hl{{animation:hl 9s linear infinite}}
@keyframes pk{{0%{{transform:translateX(0);opacity:1}}94%{{opacity:1}}100%{{transform:translateX({end - x0 + step_w - 12}px);opacity:0}}}}
@keyframes hl{{0%,100%{{opacity:.0}}50%{{opacity:.5}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<g clip-path="url(#wc)">
<rect width="{W}" height="{H}" fill="{p["bg"]}"/>
<rect width="{W}" height="{H}" fill="url(#wg)"/>
<text x="36" y="40" font-family='{MONO}' font-size="14" fill="{p["a"]}" letter-spacing="2.4">EVERY UPSTREAM FIX</text>
{"".join(out)}
<rect class="pk" x="{x0 + 8}" y="184" width="12" height="12" rx="3" fill="{p["b"]}"/>
<line x1="{x0}" y1="190" x2="{end + step_w}" y2="190" stroke="{p["dim"]}" stroke-dasharray="4 5"/>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{p["bar_line"]}"/>
</g>
</svg>
'''


def cards_markup(projects):
    cells = []
    for pr in projects:
        n = pr["name"]
        cells.append(
            f'<a href="{pr["url"]}"><picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/cards/{n}.svg" />'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/cards/{n}-light.svg" />'
            f'<img src="assets/cards/{n}.svg" width="49%" alt="{esc(n)}: {esc(pr["summary"])}" /></picture></a>')
    return '<p align="center">\n' + "\n".join(cells) + "\n</p>"
