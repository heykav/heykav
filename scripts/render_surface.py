#!/usr/bin/env python3
"""
Renders assets/surface.svg (dark) and assets/surface-light.svg (light): a 3D implied-volatility
surface that sways in perspective.

How the 3D works without script (GitHub shows README SVGs through <img>, which runs SMIL but no JS):
- The surface is a grid of quads, each a <polygon>. Its corners are projected from 3D at KEYS
  rotation angles, and SMIL interpolates the `points` between them, so the motion is smooth at any
  frame rate in every browser.
- The rotation stays within +/-SWAY degrees of the front view, so a fixed back-to-front drawing
  order stays correct throughout.
- Each polygon's base `points` is the first key, so a viewer that draws one frame or ignores
  animation still sees a complete surface.

The surface is illustrative: sigma(k, T) comes from a simple parametric smile, not market data, and
the caption says so.

Run:  python3 scripts/render_surface.py
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MONO = 'ui-monospace,"SFMono-Regular","DM Mono",Menlo,Consolas,monospace'
SERIF = 'Georgia,"Times New Roman",serif'

W, H = 1200, 420
NK, NT = 15, 11          # grid points along moneyness and maturity
KEYS = 12                # projected key poses per cycle
SWAY = 32.0              # degrees either side of the front view
ELEV = 27.0              # camera elevation, degrees
DIST = 5.5               # perspective camera distance (in surface units)
# The surface is auto-fitted (over every pose of the animation) into this panel.
PANEL = (640.0, 70.0, 1150.0, 370.0)   # x0, y0, x1, y1
CYCLE = 11.0             # seconds per sway cycle
N_COLORS = 14

DARK = dict(
    bg="#090A09", bar="#111211", bar_line="#2a2c29", bar_text="#9a9c96", grid="#1a1b1a",
    eyebrow="#00FF66", title="#F4F5F2", body="#9a9c96", note="#8a8c87", edge="#090A09",
    edge_op="0.55", axis="#3d3f3b", label="#8a8c87",
    ramp=["#06361b", "#0a6b33", "#00b35a", "#00FF66", "#B6FF2E", "#efff9a"],
)
LIGHT = dict(
    bg="#F4F5F2", bar="#eceeea", bar_line="#c4c7c0", bar_text="#54564f", grid="#e2e3df",
    eyebrow="#006b2e", title="#111211", body="#3d3f3b", note="#6b6d68", edge="#F4F5F2",
    edge_op="0.7", axis="#aab0a3", label="#54564f",
    ramp=["#d7efdf", "#9fdcb3", "#3fbf73", "#00A84A", "#5f9a00", "#355c00"],
)


def sigma(k, t):
    """Illustrative smile: convex in moneyness, flattening with maturity, mild downside skew."""
    return 0.17 + 0.13 * k * k / math.sqrt(t + 0.25) - 0.055 * k / (1.0 + t) + 0.015 * t


def grid():
    ks = [-1 + 2 * i / (NK - 1) for i in range(NK)]
    ts = [0.1 + 1.9 * j / (NT - 1) for j in range(NT)]
    vols = [[sigma(k, t) for k in ks] for t in ts]
    lo = min(min(r) for r in vols)
    hi = max(max(r) for r in vols)
    pts = []
    for j, t in enumerate(ts):
        row = []
        for i, k in enumerate(ks):
            x = k
            y = -1 + 2 * j / (NT - 1)           # maturity runs away from the viewer
            z = (vols[j][i] - lo) / (hi - lo)    # 0..1
            row.append((x, y, z * 0.95 - 0.35))
        pts.append(row)
    return pts, vols, lo, hi


FIT = {"scale": 1.0, "cx": 0.0, "cy": 0.0}


def project_raw(p, theta):
    x, y, z = p
    c, s = math.cos(theta), math.sin(theta)
    xr, yr = x * c - y * s, x * s + y * c
    ce, se = math.cos(math.radians(ELEV)), math.sin(math.radians(ELEV))
    depth = yr * ce - z * se
    up = z * ce + yr * se
    f = DIST / (DIST + depth)
    return xr * f, -up * f, depth


def project(p, theta):
    u, v, depth = project_raw(p, theta)
    return FIT["cx"] + FIT["scale"] * u, FIT["cy"] + FIT["scale"] * v, depth


def fit(points, angles):
    """Scale and centre so every pose of the surface fits inside PANEL."""
    us, vs = [], []
    for a in angles:
        for q in points:
            u, v, _ = project_raw(q, a)
            us.append(u)
            vs.append(v)
    x0, y0, x1, y1 = PANEL
    scale = min((x1 - x0) / (max(us) - min(us)), (y1 - y0) / (max(vs) - min(vs)))
    FIT["scale"] = scale
    FIT["cx"] = (x0 + x1) / 2 - scale * (max(us) + min(us)) / 2
    FIT["cy"] = (y0 + y1) / 2 - scale * (max(vs) + min(vs)) / 2


def ramp_color(stops, u):
    u = min(max(u, 0.0), 1.0) * (len(stops) - 1)
    i = min(int(u), len(stops) - 2)
    a, b = stops[i], stops[i + 1]
    t = u - i
    ca = [int(a[n:n + 2], 16) for n in (1, 3, 5)]
    cb = [int(b[n:n + 2], 16) for n in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(ca[n] + (cb[n] - ca[n]) * t) for n in range(3))


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def render(p):
    pts, vols, lo, hi = grid()
    angles = [math.radians(SWAY * math.sin(2 * math.pi * n / KEYS)) for n in range(KEYS)] + [0.0]
    floor = -0.35
    box = [(-1, -1, floor), (1, -1, floor), (1, 1, floor), (-1, 1, floor)]
    fit([q for row in pts for q in row] + box, angles)
    proj = [[[project(q, a) for q in row] for row in pts] for a in angles]

    quads = []
    for j in range(NT - 1):
        for i in range(NK - 1):
            corners = [(j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i)]
            depth = sum(proj[0][a][b][2] for a, b in corners) / 4
            v = sum(vols[a][b] for a, b in corners) / 4
            cls = min(int((v - lo) / (hi - lo) * N_COLORS), N_COLORS - 1)
            keys = [" ".join(f"{fmt(proj[n][a][b][0])},{fmt(proj[n][a][b][1])}" for a, b in corners)
                    for n in range(len(angles))]
            quads.append((depth, cls, keys))
    quads.sort(key=lambda q: -q[0])  # far first

    classes = "\n".join(
        f".c{n}{{fill:{ramp_color(p['ramp'], (n + 0.5) / N_COLORS)}}}" for n in range(N_COLORS))
    polys = "\n".join(
        f'<polygon class="c{cls}" points="{keys[0]}"><animate attributeName="points" '
        f'dur="{CYCLE}s" repeatCount="indefinite" values="{";".join(keys)}"/></polygon>'
        for _, cls, keys in quads)

    # Base frame of the box under the surface, animated the same way.
    box_keys = [" ".join(f"{fmt(project(c, a)[0])},{fmt(project(c, a)[1])}" for c in box) for a in angles]
    floor_poly = (f'<polygon points="{box_keys[0]}" fill="none" stroke="{p["axis"]}" stroke-width="1" '
                  f'stroke-dasharray="4 4"><animate attributeName="points" dur="{CYCLE}s" '
                  f'repeatCount="indefinite" values="{";".join(box_keys)}"/></polygon>')

    def moving_label(point, text, anchor):
        xs = ";".join(fmt(project(point, a)[0]) for a in angles)
        ys = ";".join(fmt(project(point, a)[1]) for a in angles)
        x0, y0, _ = project(point, angles[0])
        return (f'<text x="{fmt(x0)}" y="{fmt(y0)}" text-anchor="{anchor}" font-family=\'{MONO}\' '
                f'font-size="15" fill="{p["label"]}" letter-spacing="1">{text}'
                f'<animate attributeName="x" dur="{CYCLE}s" repeatCount="indefinite" values="{xs}"/>'
                f'<animate attributeName="y" dur="{CYCLE}s" repeatCount="indefinite" values="{ys}"/></text>')

    labels = "\n".join([
        moving_label((0, -1.25, floor - 0.08), "MONEYNESS", "middle"),
        moving_label((1.12, 0.35, floor - 0.08), "MATURITY", "start"),
    ])

    legend = "".join(
        f'<rect x="{56 + n * 14}" y="318" width="14" height="8" fill="{ramp_color(p["ramp"], (n + 0.5) / N_COLORS)}"/>'
        for n in range(N_COLORS))

    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="vs-t vs-d">
<title id="vs-t">Implied volatility surface, rendered in 3D</title>
<desc id="vs-d">An animated 3D implied-volatility surface that sways in perspective: volatility across moneyness and maturity, with a smile that flattens as maturity grows. Illustrative, generated from a simple parametric smile, not market data.</desc>
<defs>
<pattern id="vs-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
<clipPath id="vs-clip"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<radialGradient id="vs-glow" cx="0.5" cy="0.55" r="0.5"><stop offset="0%" stop-color="{p["ramp"][3]}" stop-opacity="0.10"/><stop offset="100%" stop-color="{p["ramp"][3]}" stop-opacity="0"/></radialGradient>
</defs>
<style>
{classes}
polygon[class]{{stroke:{p["edge"]};stroke-opacity:{p["edge_op"]};stroke-width:0.8;stroke-linejoin:round}}
</style>
<g clip-path="url(#vs-clip)">
<rect width="{W}" height="{H}" fill="{p["bg"]}"/>
<rect y="32" width="{W}" height="{H - 32}" fill="url(#vs-grid)"/>
<rect width="{W}" height="32" fill="{p["bar"]}"/>
<circle cx="24" cy="16" r="6" fill="#FF5F57"/><circle cx="44" cy="16" r="6" fill="#FEBC2E"/><circle cx="64" cy="16" r="6" fill="#28C840"/>
<text x="600" y="21" text-anchor="middle" font-family='{MONO}' font-size="13" fill="{p["bar_text"]}" letter-spacing="0.5">vol_surface.py</text>
<rect y="32" width="{W}" height="1" fill="{p["bar_line"]}"/>
<ellipse cx="{(PANEL[0] + PANEL[2]) / 2}" cy="{(PANEL[1] + PANEL[3]) / 2 + 20}" rx="330" ry="170" fill="url(#vs-glow)"/>
{floor_poly}
{polys}
{labels}
<text x="56" y="96" font-family='{MONO}' font-size="16" fill="{p["eyebrow"]}" letter-spacing="2.4">OPTIONS × VOLATILITY</text>
<text x="56" y="152" font-family='{SERIF}' font-size="46" font-weight="700" fill="{p["title"]}">The smile,</text>
<text x="56" y="204" font-family='{SERIF}' font-size="46" font-weight="700" fill="{p["title"]}">in three dimensions</text>
<text x="56" y="252" font-family='{MONO}' font-size="17" fill="{p["body"]}">σ(k, T): volatility across strike and expiry.</text>
{legend}
<text x="56" y="350" font-family='{MONO}' font-size="14" fill="{p["note"]}">lower σ</text>
<text x="{56 + N_COLORS * 14}" y="346" text-anchor="end" font-family='{MONO}' font-size="14" fill="{p["note"]}">higher σ</text>
<text x="56" y="394" font-family='{MONO}' font-size="14" fill="{p["note"]}">Illustrative: a parametric smile, not market data.</text>
</g>
</svg>
'''


def main():
    for name, palette in (("surface.svg", DARK), ("surface-light.svg", LIGHT)):
        (ROOT / "assets" / name).write_text(render(palette), encoding="utf-8")
        print("wrote assets/" + name)


if __name__ == "__main__":
    main()
