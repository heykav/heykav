#!/usr/bin/env python3
"""
Regenerates the auto-managed parts of README.md and assets/stats*.svg from
real GitHub data: project count, "on GitHub since" year, location, language
mix, the "What I've actually shipped" table, and the "Patches upstream"
list.

Design rule that keeps this safe to run unattended, daily, with no review:
hand-written prose lives in data/projects.json and data/patches.json,
keyed by repo name / PR url. This script never invents narrative voice for
an entry that already has an override - it only fills in a plain, honest,
factual placeholder (the repo's own GitHub description, or a PR title) for
something genuinely new that has no override yet. A human (or a future
Claude session) upgrades a placeholder by adding it to the JSON file, not
by hand-editing the generated README block, since the next run would just
regenerate over a hand-edit inside the markers.

Everything outside the AUTO:*:start/end markers is left untouched.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "heykav"
OWN_REPO = "heykav"  # this profile repo itself is never a "shipped project"

DARK = {
    "bg": "#090A09", "grid": "#1a1b1a", "label": "#6b6d68", "muted": "#8a8c87",
    "text": "#F4F5F2", "accent": "#00FF66", "accent2": "#B6FF2E", "track": "#1a1b1a",
    "bar2": "#6fd94f", "bar3": "#3d3f3b", "bar4": "#54564f",
}
LIGHT = {
    "bg": "#F4F5F2", "grid": "#e2e3df", "label": "#7a7c74", "muted": "#54564f",
    "text": "#111211", "accent": "#00FF66", "accent2": "#B6FF2E", "track": "#e2e3df",
    "bar2": "#6fd94f", "bar3": "#3d3f3b", "bar4": "#54564f",
}

# Rough country-name -> short tag map for the stats panel's "based in" slot.
# Falls back to the first two letters of whatever GitHub reports.
COUNTRY_TAGS = {"india": "IN", "united states": "US", "united kingdom": "UK"}


def gh_json(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def load_overrides(name):
    path = ROOT / "data" / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def fetch_projects():
    repos = gh_json("api", f"users/{USER}/repos", "--paginate")
    repos = [r for r in repos if not r["fork"] and r["name"] != OWN_REPO and not r["private"]]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)

    overrides = load_overrides("projects")
    projects = []
    seen = set()

    # Overridden repos first, in the order they're written in the JSON file,
    # but only if the repo still actually exists / is still public.
    by_name = {r["name"]: r for r in repos}
    for name, ov in overrides.items():
        if name in by_name:
            projects.append({"name": name, "url": by_name[name]["html_url"],
                              "description": ov["description"], "tags": ov["tags"]})
            seen.add(name)

    for r in repos:
        if r["name"] in seen:
            continue
        langs = gh_json("api", f"repos/{USER}/{r['name']}/languages")
        top_tags = sorted(langs, key=langs.get, reverse=True)[:3] or ["Code"]
        projects.append({
            "name": r["name"], "url": r["html_url"],
            "description": r["description"] or "No description yet.",
            "tags": top_tags,
        })
    return projects, repos


def fetch_patches():
    prs = gh_json("search", "prs", "--author", USER, "--json",
                   "url,title,repository,state,isDraft", "--limit", "100")
    external = [p for p in prs if not p["repository"]["nameWithOwner"].startswith(f"{USER}/")]

    overrides = load_overrides("patches")
    patches = []
    seen = set()

    for url, ov in overrides.items():
        if any(p["url"] == url for p in external):
            patches.append({"url": url, "label": ov["label"], "body": ov["body"]})
            seen.add(url)

    for p in external:
        if p["url"] in seen:
            continue
        state = "open" if p["state"] == "OPEN" else p["state"].lower()
        patches.append({
            "url": p["url"], "label": p["repository"]["nameWithOwner"],
            "body": f"{p['title']} ({state}).",
        })
    return patches


def render_projects_table(projects):
    cards = []
    for p in projects:
        tags = " ".join(f"`{t}`" for t in p["tags"])
        cards.append(
            f'<td width="33%" valign="top">\n\n'
            f'**[{p["name"]}]({p["url"]})**\n\n'
            f'{p["description"]}\n\n'
            f'{tags}\n\n'
            f'</td>'
        )
    rows = []
    for i in range(0, len(cards), 3):
        rows.append("<tr>\n" + "\n".join(cards[i:i + 3]) + "\n</tr>")
    return '<table width="100%">\n' + "\n".join(rows) + "\n</table>"


def render_patches_block(patches):
    parts = []
    for p in patches:
        parts.append(f'[**{p["label"]}**]({p["url"]}) — {p["body"]}')
    return "\n\n".join(parts)


def replace_marker_block(text, marker, new_body):
    pattern = re.compile(
        rf"(<!-- AUTO:{marker}:start -->\n).*?(\n<!-- AUTO:{marker}:end -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise SystemExit(f"marker AUTO:{marker} not found in README.md")
    return pattern.sub(lambda m: m.group(1) + new_body + m.group(2), text)


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def render_stats_svg(palette, project_count, since_year, location_tag,
                      location_label, patches, lang_mix):
    if len(patches) == 1:
        patch_label = f"patches: {patches[0]['label']}"
    elif len(patches) > 1:
        patch_label = f"patches: {patches[0]['label']} & {len(patches) - 1} more"
    else:
        patch_label = "patches: none yet"

    top = lang_mix[:4]
    bar_total = sum(pct for _, pct in top) or 1
    bar_colors = [palette["accent"], palette["bar2"], palette["bar3"], palette["bar4"]]
    bar_x = 56
    bars = []
    for (lang, pct), color in zip(top, bar_colors):
        w = round(1088 * (pct / bar_total))
        bars.append(f'<rect x="{bar_x}" y="168" width="{w}" height="10" fill="{color}"/>')
        bar_x += w

    legend = []
    lx = 60
    for (lang, pct), color in zip(top, bar_colors):
        label = f"{lang} {round(pct)}%"
        legend.append(f'<circle cx="{lx}" cy="200" r="4" fill="{color}"/>')
        legend.append(f'<text x="{lx + 10}" y="204" fill="{palette["muted"]}">{esc(label)}</text>')
        lx += 20 + len(label) * 7 + 24

    alt_langs = ", ".join(f"{lang} {round(pct)}%" for lang, pct in top)
    alt = (f"Krishna Anubhav GitHub signal: {project_count} projects shipped, "
           f"on GitHub since {since_year}, based in {location_label}, "
           f"open-source {patch_label}; language mix across own repos is {alt_langs}")

    return f'''<svg width="1200" height="220" viewBox="0 0 1200 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(alt)}">
  <defs>
    <pattern id="grid2" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{palette["grid"]}" stroke-width="1"/>
    </pattern>
    <clipPath id="clip2"><rect width="1200" height="220" rx="14"/></clipPath>
  </defs>
  <style>
    .mono {{ font-family: ui-monospace, "SFMono-Regular", "DM Mono", Menlo, Consolas, monospace; }}
  </style>

  <g clip-path="url(#clip2)">
    <rect width="1200" height="220" fill="{palette["bg"]}"/>
    <rect width="1200" height="220" fill="url(#grid2)"/>

    <g class="mono">
      <text x="56" y="50" font-size="13" fill="{palette["label"]}" letter-spacing="1.5">SIGNAL</text>

      <text x="56" y="94" font-size="30" font-weight="700" fill="{palette["text"]}">{project_count}</text>
      <text x="56" y="114" font-size="12" fill="{palette["muted"]}">projects shipped</text>

      <text x="230" y="94" font-size="30" font-weight="700" fill="{palette["text"]}">{since_year}</text>
      <text x="230" y="114" font-size="12" fill="{palette["muted"]}">on GitHub since</text>

      <text x="430" y="94" font-size="30" font-weight="700" fill="{palette["text"]}">{esc(location_tag)}</text>
      <text x="430" y="114" font-size="12" fill="{palette["muted"]}">based in {esc(location_label)}</text>

      <text x="630" y="94" font-size="30" font-weight="700" fill="{palette["accent2"]}">OSS</text>
      <text x="630" y="114" font-size="12" fill="{palette["muted"]}">{esc(patch_label)}</text>
    </g>

    <text x="56" y="156" font-size="12" class="mono" fill="{palette["label"]}" letter-spacing="1">LANGUAGE MIX (BY BYTES, OWN REPOS)</text>
    <g>
      <rect x="56" y="168" width="1088" height="10" rx="5" fill="{palette["track"]}"/>
      {chr(10).join(bars)}
    </g>
    <g class="mono" font-size="12">
      {chr(10).join(legend)}
    </g>
  </g>
</svg>
'''


def main():
    projects, all_own_repos = fetch_projects()
    patches = fetch_patches()

    account = gh_json("api", f"users/{USER}")
    since_year = account["created_at"][:4]
    location = account.get("location") or "India"
    location_tag = COUNTRY_TAGS.get(location.strip().lower(), location[:2].upper())

    lang_bytes = {}
    for p in projects:
        langs = gh_json("api", f"repos/{USER}/{p['name']}/languages")
        for lang, n in langs.items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n
    total = sum(lang_bytes.values()) or 1
    lang_mix = sorted(((lang, 100 * n / total) for lang, n in lang_bytes.items()),
                       key=lambda x: x[1], reverse=True)

    readme_path = ROOT / "README.md"
    text = readme_path.read_text()
    text = replace_marker_block(text, "projects", render_projects_table(projects))
    text = replace_marker_block(text, "patches", render_patches_block(patches))

    stats_alt = render_stats_svg(DARK, len(projects), since_year, location_tag,
                                  location, patches, lang_mix)
    # only the <picture> block's alt text needs refreshing in the README;
    # the img alt is derived the same way inside render_stats_svg's aria-label.
    alt_match = re.search(r'aria-label="([^"]*)"', stats_alt)
    picture_block = (
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/stats.svg" />\n'
        '  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg" />\n'
        f'  <img src="assets/stats.svg" width="100%" alt="{alt_match.group(1)}" />\n'
        '</picture>'
    )
    text = replace_marker_block(text, "statsalt", picture_block)
    readme_path.write_text(text)

    (ROOT / "assets" / "stats.svg").write_text(
        render_stats_svg(DARK, len(projects), since_year, location_tag, location, patches, lang_mix))
    (ROOT / "assets" / "stats-light.svg").write_text(
        render_stats_svg(LIGHT, len(projects), since_year, location_tag, location, patches, lang_mix))

    print(f"projects: {len(projects)}, patches: {len(patches)}, "
          f"since: {since_year}, location: {location}, top languages: {lang_mix[:4]}")


if __name__ == "__main__":
    main()
