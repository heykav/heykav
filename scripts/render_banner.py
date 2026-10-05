#!/usr/bin/env python3
"""
Renders assets/banner.svg (dark) and assets/banner-light.svg (light) from one
template, so the two never drift apart.

The banner is static content with CSS animation layered on top:
- Every element is fully visible in its base state. Animation only adds a
  starting state ("both" fill mode), so a viewer that ignores <style>, or one
  that asks for reduced motion, sees the finished banner.
- GitHub shows README SVGs through <img>, which runs CSS and SMIL animation
  but no script. Nothing here needs script.
- The line and the bars on the right are decorative and carry no data.

Run:  python3 scripts/render_banner.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MONO = 'ui-monospace,"SFMono-Regular","DM Mono",Menlo,Consolas,monospace'
SERIF = 'Georgia,"Times New Roman",serif'
SANS = 'system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif'

DARK = dict(
    bg="#090A09", bar="#111211", bar_line="#2a2c29", bar_text="#9a9c96", grid="#1a1b1a",
    sig_a="#00FF66", sig_b="#B6FF2E", fade_op="0.12", node_fill="#090A09", node_stroke="#00FF66",
    end_node="#B6FF2E", eyebrow="#00FF66", name="#F4F5F2", role="#c7c9c4", arrow="#B6FF2E",
    tagline="#9a9c96", cursor="#B6FF2E", candle="#00FF66", candle_op="0.13",
)
LIGHT = dict(
    bg="#F4F5F2", bar="#eceeea", bar_line="#c4c7c0", bar_text="#54564f", grid="#e2e3df",
    sig_a="#00A84A", sig_b="#5f9a00", fade_op="0.10", node_fill="#F4F5F2", node_stroke="#00A84A",
    end_node="#5f9a00", eyebrow="#006b2e", name="#111211", role="#3d3f3b", arrow="#5f9a00",
    tagline="#54564f", cursor="#5f9a00", candle="#00A84A", candle_op="0.14",
)

TAGLINE = "I spent years building businesses. Now I'm learning how investors value them."
CHAR_W = 0.6  # monospace advance as a fraction of font size
TAG_SIZE = 15
TYPE_W = round(len(TAGLINE) * TAG_SIZE * CHAR_W) + 6  # clip width that reveals the whole line
TYPE_STEPS = len(TAGLINE)

# Decorative candle heights (px), fixed so the output is deterministic.
CANDLES = [28, 46, 34, 62, 52, 78, 60, 92, 74, 70, 104, 88, 118, 96, 132, 110, 124, 146]
CANDLE_X0, CANDLE_STEP, CANDLE_BASE = 786, 22, 272


CYCLE = 16.0  # seconds; the whole intro replays on this loop
INTRO0 = 1.8  # the finished banner shows first, fades, then the intro replays from here
RESET_AT = 1.65  # while the group is invisible, every element jumps to its start state
KEYS = {}     # keyframe name -> css, filled by anim()


def _pct(t):
    return f"{t / CYCLE * 100:.3f}".rstrip("0").rstrip(".")


def anim(kind, start, dur):
    """Register keyframes for one element and return its style attribute.

    Frame 0 is the finished banner (so a viewer that only draws the first frame,
    or ignores animation, sees it complete). The group then fades out, each element
    jumps to its start state, and the intro plays to the same finished state.
    """
    states = {
        "up": ("opacity:0;transform:translateY(12px)", "opacity:1;transform:none"),
        "grow": ("transform:scaleX(0)", "transform:scaleX(1)"),
        "draw": ("stroke-dashoffset:1", "stroke-dashoffset:0"),
        "pop": ("opacity:0;transform:scale(0)", "opacity:1;transform:scale(1)"),
        "rise": ("opacity:0;transform:scaleY(0)", "opacity:1;transform:scaleY(1)"),
        "fade": ("opacity:0", "opacity:1"),
        "type": ("width:0", f"width:{TYPE_W}px"),
        "walk": ("transform:translateX(0)", f"transform:translateX({TYPE_W - 6}px)"),
    }
    frm, to = states[kind]
    name = f"k{len(KEYS)}"
    start += INTRO0
    KEYS[name] = (
        f"@keyframes {name}{{0%,{_pct(RESET_AT)}%{{{to}}}"
        f"{_pct(RESET_AT + 0.05)}%,{_pct(start)}%{{{frm}}}{_pct(start + dur)}%,100%{{{to}}}}}"
    )
    ease = f"steps({TYPE_STEPS},end)" if kind in ("type", "walk") else (
        "ease-in-out" if kind == "draw" else "cubic-bezier(.2,.7,.2,1)")
    return f"animation:{name} {CYCLE}s {ease} infinite"


def render(p, light):
    KEYS.clear()
    candles = []
    for i, h in enumerate(CANDLES):
        x = CANDLE_X0 + i * CANDLE_STEP
        intro = anim("rise", 0.45 + i * 0.05, 0.7)
        breath = f"animation:breath {3.2 + (i % 5) * 0.35:.2f}s ease-in-out {i * 0.21:.2f}s infinite alternate"
        candles.append(
            f'<g class="a breath" style="{breath}"><rect class="a candle" style="{intro}" '
            f'x="{CANDLE_X0 + i * CANDLE_STEP}" y="{CANDLE_BASE - h}" width="10" height="{h}" rx="2"/></g>'
        )
    candles = "\n".join(candles)

    a_eyebrow = anim("up", 0.10, 0.7)
    a_name = anim("up", 0.28, 0.8)
    a_role = anim("up", 0.55, 0.8)
    a_rule = anim("grow", 0.85, 0.6)
    a_line = anim("draw", 0.60, 1.9)
    a_area = anim("fade", 1.20, 1.4)
    a_n1, a_n2, a_n3 = anim("pop", 1.45, 0.45), anim("pop", 1.95, 0.45), anim("pop", 2.40, 0.45)
    a_type = anim("type", 1.35, 3.1)
    a_walk = anim("walk", 1.35, 3.1)
    a_dot = anim("fade", 2.6, 0.5)
    keys = "\n".join(KEYS.values())
    path = "M 800 246 C 850 242, 890 230, 930 218 S 1000 190, 1050 164 S 1110 114, 1160 84"

    return f'''<svg width="1200" height="300" viewBox="0 0 1200 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="bn-t bn-d">
<title id="bn-t">Krishna Anubhav: finance, engineering and quantitative systems</title>
<desc id="bn-d">Animated profile banner for Krishna Anubhav (Kavy). Engineer, then SaaS founder and operator, then MBA, now investment banking. I spent years building businesses; now I am learning how investors value them. The rising line and bars on the right are decorative and carry no data.</desc>
<defs>
<linearGradient id="bn-signal" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="{p["sig_a"]}"/><stop offset="100%" stop-color="{p["sig_b"]}"/></linearGradient>
<linearGradient id="bn-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{p["sig_a"]}" stop-opacity="{p["fade_op"]}"/><stop offset="100%" stop-color="{p["sig_a"]}" stop-opacity="0"/></linearGradient>
<pattern id="bn-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
<clipPath id="bn-clip"><rect width="1200" height="300" rx="14"/></clipPath>
<clipPath id="bn-type"><rect class="a" style="{a_type}" x="56" y="226" width="{TYPE_W}" height="26"/></clipPath>
<path id="bn-route" d="{path}"/>
</defs>
<style>
{keys}
@keyframes cyc{{0%,{_pct(1.2)}%{{opacity:1}}{_pct(1.6)}%,{_pct(INTRO0 - 0.02)}%{{opacity:0}}{_pct(INTRO0)}%,100%{{opacity:1}}}}
.cycle{{animation:cyc {CYCLE}s linear infinite}}
.rule,.pop,.candle,.breath{{transform-box:fill-box}}
.rule{{transform-origin:0 50%}}
.pop{{transform-origin:center}}
.candle,.breath{{transform-origin:50% 100%}}
@keyframes breath{{from{{transform:scaleY(1)}}to{{transform:scaleY(.82)}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.ring{{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 2.8s ease-out 2.7s infinite}}
@keyframes ring{{0%{{opacity:.75;transform:scale(1)}}100%{{opacity:0;transform:scale(4.2)}}}}
.drift{{animation:drift 10s linear infinite}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-40px)}}}}
@media (prefers-reduced-motion:reduce){{.a,.cycle,.blink,.ring,.drift,.breath{{animation:none!important}}.ring{{opacity:0}}.dot{{display:none}}}}
</style>
<g clip-path="url(#bn-clip)">
<rect width="1200" height="300" fill="{p["bg"]}"/>
<rect width="1200" height="32" fill="{p["bar"]}"/>
<circle cx="24" cy="16" r="6" fill="#FF5F57"/><circle cx="44" cy="16" r="6" fill="#FEBC2E"/><circle cx="64" cy="16" r="6" fill="#28C840"/>
<text x="600" y="21" text-anchor="middle" font-family='{MONO}' font-size="13" fill="{p["bar_text"]}" letter-spacing="0.5">kavy@github</text>
<rect y="32" width="1200" height="1" fill="{p["bar_line"]}"/>
<rect class="drift" y="33" width="1240" height="267" fill="url(#bn-grid)"/>
<g class="cycle">
<rect class="a" style="{a_area}" x="760" y="33" width="440" height="267" fill="url(#bn-fade)"/>
<g fill="{p["candle"]}" fill-opacity="{p["candle_op"]}">
{candles}
</g>
<path class="a" style="{a_line}" pathLength="1" stroke-dasharray="1" d="{path}" fill="none" stroke="url(#bn-signal)" stroke-width="2.4" stroke-linecap="round"/>
<circle class="a pop" style="{a_n1}" cx="930" cy="218" r="4" fill="{p["node_fill"]}" stroke="{p["node_stroke"]}" stroke-width="1.8"/>
<circle class="a pop" style="{a_n2}" cx="1050" cy="164" r="4" fill="{p["node_fill"]}" stroke="{p["node_stroke"]}" stroke-width="1.8"/>
<circle class="a pop" style="{a_n3}" cx="1160" cy="84" r="4.5" fill="{p["end_node"]}"/>
<circle class="ring" cx="1160" cy="84" r="4.5" fill="none" stroke="{p["end_node"]}" stroke-width="1.6"/>
<g class="a dot" style="{a_dot}"><circle r="9" fill="{p["end_node"]}" fill-opacity="0.18"/><circle r="3.6" fill="{p["end_node"]}"/><animateMotion dur="4.5s" begin="0s" repeatCount="indefinite" rotate="0"><mpath href="#bn-route"/></animateMotion></g>
<text class="a" style="{a_eyebrow}" x="56" y="84" font-family='{MONO}' font-size="13" fill="{p["eyebrow"]}" letter-spacing="2.4">FINANCE × ENGINEERING × QUANTITATIVE SYSTEMS</text>
<text class="a" style="{a_name}" x="56" y="144" font-family='{SERIF}' font-size="50" font-weight="700" fill="{p["name"]}">Krishna Anubhav</text>
<text class="a" style="{a_role}" x="56" y="184" font-family='{SANS}' font-size="19" fill="{p["role"]}">Engineer <tspan fill="{p["arrow"]}">→</tspan> SaaS founder/operator <tspan fill="{p["arrow"]}">→</tspan> MBA <tspan fill="{p["arrow"]}">→</tspan> Investment banking</text>
<rect class="a rule" style="{a_rule}" x="56" y="206" width="48" height="2" fill="url(#bn-signal)"/>
<g clip-path="url(#bn-type)"><text x="56" y="244" font-family='{MONO}' font-size="{TAG_SIZE}" fill="{p["tagline"]}">{TAGLINE.replace("'", "&#39;")}</text></g>
<g class="a" style="{a_walk};transform:translateX({TYPE_W - 6}px)"><rect class="blink" x="58" y="231" width="8" height="17" fill="{p["cursor"]}"/></g>
</g>
</g>
</svg>
'''


def main():
    for name, palette, light in (("banner.svg", DARK, False), ("banner-light.svg", LIGHT, True)):
        (ROOT / "assets" / name).write_text(render(palette, light), encoding="utf-8")
        print("wrote assets/" + name)


if __name__ == "__main__":
    main()
