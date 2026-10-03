#!/usr/bin/env python3
"""
Regenerates the auto-managed parts of README.md and assets/stats*.svg from
real GitHub data: project count, "on GitHub since" year, language mix, the
"Selected work" table, the upstream-patch counts and the "Patches upstream"
list.

Design rule that keeps this safe to run unattended, daily, with no review:
hand-written prose lives in data/projects.json and data/patches.json,
keyed by repo name / PR url. This script never invents narrative voice for
an entry that already has an override - it only fills in a plain, honest,
factual placeholder (the repo's own GitHub description, or a PR title) for
something genuinely new that has no override yet. A human upgrades a placeholder by adding it to the JSON file, not
by hand-editing the generated README block, since the next run would just
regenerate over a hand-edit inside the markers.

Pull-request status (merged / open / closed) is never written by hand: it
comes from GitHub on every run, and the README list is grouped by it.

Output is deterministic for a given set of GitHub responses, and a second
run with unchanged data changes nothing (the "as of" date in the patch
summary only moves when the counts do).

Everything outside the AUTO:*:start/end markers is left untouched.
"""
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "heykav"
OWN_REPO = "heykav"  # this profile repo itself is never a "shipped project"
PR_SEARCH_LIMIT = 1000  # gh search caps at 1000; hitting it means results were cut off
TODAY_OVERRIDE = None  # tests may set an ISO date here

# Text colours meet WCAG AA (>= 4.5:1) on their background; bar and legend
# colours meet 3:1 as non-text graphics.
DARK = {
    "bg": "#090A09", "grid": "#1a1b1a", "label": "#8a8c87", "muted": "#9a9c96",
    "text": "#F4F5F2", "accent": "#B6FF2E", "track": "#1a1b1a",
    "bars": ["#00FF66", "#B6FF2E", "#8a8c87", "#5d605a"],
}
LIGHT = {
    "bg": "#F4F5F2", "grid": "#e2e3df", "label": "#5d605a", "muted": "#54564f",
    "text": "#111211", "accent": "#3f6f00", "track": "#e2e3df",
    "bars": ["#006b2e", "#5f9a00", "#3d3f3b", "#8a8c87"],
}

STATE_ORDER = ["merged", "open", "closed"]
STATE_HEADINGS = {
    "merged": "Merged",
    "open": "Open, awaiting review",
    "closed": "Closed without merging",
}

_lang_cache = {}


def fail(msg):
    raise SystemExit(f"update_profile: {msg}")


def gh_json(*args):
    try:
        out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        fail("the GitHub CLI `gh` is not installed or not on PATH")
    except subprocess.CalledProcessError as e:
        fail(f"`gh {' '.join(args)}` failed (exit {e.returncode}): {e.stderr.strip()}")
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as e:
        fail(f"`gh {' '.join(args)}` did not return JSON: {e}")


def repo_languages(name):
    if name not in _lang_cache:
        _lang_cache[name] = gh_json("api", f"repos/{USER}/{name}/languages")
    return _lang_cache[name]


def load_overrides(name):
    path = ROOT / "data" / f"{name}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {e}")


def require_keys(source, key, entry, keys):
    missing = [k for k in keys if k not in entry]
    if missing:
        fail(f"data/{source}.json entry {key!r} is missing {', '.join(missing)}")


def fetch_projects():
    repos = gh_json("api", f"users/{USER}/repos", "--paginate")
    repos = [r for r in repos if not r["fork"] and r["name"] != OWN_REPO and not r["private"]]
    repos.sort(key=lambda r: (r["pushed_at"], r["name"]), reverse=True)

    overrides = load_overrides("projects")
    projects = []
    seen = set()

    # Overridden repos first, in the order they're written in the JSON file,
    # but only if the repo still actually exists / is still public.
    by_name = {r["name"]: r for r in repos}
    for name, ov in overrides.items():
        require_keys("projects", name, ov, ["description", "tags"])
        if name in by_name:
            projects.append({"name": name, "url": by_name[name]["html_url"],
                             "description": ov["description"], "tags": ov["tags"]})
            seen.add(name)

    for r in repos:
        if r["name"] in seen:
            continue
        langs = repo_languages(r["name"])
        top_tags = sorted(langs, key=lambda k: (-langs[k], k))[:3] or ["Code"]
        projects.append({
            "name": r["name"], "url": r["html_url"],
            "description": r["description"] or "No description yet.",
            "tags": top_tags,
        })
    return projects


def normalize_state(pr):
    # `gh search prs` reports merged pull requests as "merged".
    state = str(pr.get("state", "")).lower()
    if state not in STATE_ORDER:
        fail(f"unexpected state {pr.get('state')!r} for {pr.get('url')}")
    return state


def fetch_patches():
    prs = gh_json("search", "prs", "--author", USER, "--json",
                  "url,title,repository,state,isDraft,createdAt",
                  "--limit", str(PR_SEARCH_LIMIT))
    if len(prs) >= PR_SEARCH_LIMIT:
        fail(f"PR search returned {len(prs)} results, the limit; the list would be truncated")
    external = [p for p in prs if not p["repository"]["nameWithOwner"].startswith(f"{USER}/")]
    # Search order is "best match", which can shift between runs: pin it.
    external.sort(key=lambda p: (p["createdAt"], p["url"]), reverse=True)
    by_url = {p["url"]: p for p in external}

    overrides = load_overrides("patches")
    patches = []
    seen = set()

    for url, ov in overrides.items():
        require_keys("patches", url, ov, ["label", "body"])
        if url in by_url:
            patches.append({"url": url, "label": ov["label"], "body": ov["body"],
                            "state": normalize_state(by_url[url])})
            seen.add(url)

    for p in external:
        if p["url"] in seen:
            continue
        patches.append({
            "url": p["url"], "label": p["repository"]["nameWithOwner"],
            "body": f"{p['title']}.", "state": normalize_state(p),
        })
    return patches


def count_states(patches):
    return {s: sum(1 for p in patches if p["state"] == s) for s in STATE_ORDER}


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
    sections = []
    for state in STATE_ORDER:
        group = [p for p in patches if p["state"] == state]
        if not group:
            continue
        lines = [f"#### {STATE_HEADINGS[state]} ({len(group)})"]
        lines += [f'[**{p["label"]}**]({p["url"]}) — {p["body"]}' for p in group]
        sections.append("\n\n".join(lines))
    return "\n\n".join(sections)


def render_patch_summary(counts, as_of):
    total = sum(counts.values())
    return (f"As of {as_of} there are {total}: {counts['merged']} merged, "
            f"{counts['open']} open and {counts['closed']} closed without merging.")


def marker_pattern(marker):
    return re.compile(
        rf"(<!-- AUTO:{marker}:start -->\n)(.*?)(\n<!-- AUTO:{marker}:end -->)",
        re.DOTALL,
    )


def read_marker_block(text, marker):
    m = marker_pattern(marker).search(text)
    return m.group(2) if m else None


def replace_marker_block(text, marker, new_body):
    pattern = marker_pattern(marker)
    n = len(pattern.findall(text))
    if n != 1:
        fail(f"expected exactly one AUTO:{marker} block in README.md, found {n}")
    return pattern.sub(lambda m: m.group(1) + new_body + m.group(3), text)


def today():
    return TODAY_OVERRIDE or datetime.datetime.now(datetime.timezone.utc).date().isoformat()


def patch_summary(text, counts):
    """Keep the existing "as of" date when the counts have not changed."""
    existing = read_marker_block(text, "patchsummary") or ""
    m = re.search(r"As of (\d{4}-\d{2}-\d{2})", existing)
    if m and render_patch_summary(counts, m.group(1)) == existing:
        return existing
    return render_patch_summary(counts, today())


def esc(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def stats_alt(project_count, since_year, counts, lang_mix):
    total = sum(counts.values())
    alt_langs = ", ".join(f"{lang} {round(pct)}%" for lang, pct in lang_mix[:4])
    return (f"Krishna Anubhav on GitHub: {project_count} original public repos; "
            f"{total} pull requests opened on other projects, {counts['merged']} merged, "
            f"{counts['open']} open and {counts['closed']} closed without merging; "
            f"on GitHub since {since_year}; language mix across own repos by bytes: {alt_langs}")


MONO = 'ui-monospace, "SFMono-Regular", "DM Mono", Menlo, Consolas, monospace'
NL4 = "\n    "
NL6 = "\n      "
CHAR_W = 0.61  # advance width of a monospace glyph, as a fraction of font size


def render_stats_svg(palette, project_count, since_year, counts, lang_mix):
    total = sum(counts.values())
    alt = stats_alt(project_count, since_year, counts, lang_mix)

    blocks = [
        (56, str(project_count), palette["text"], "original public repos"),
        (316, str(total), palette["text"], "pull requests to other projects"),
        (646, str(counts["merged"]), palette["accent"],
         f"merged, {counts['open']} open, {counts['closed']} closed"),
        (936, str(since_year), palette["text"], "on GitHub since"),
    ]
    stat_lines = []
    for x, value, color, label in blocks:
        stat_lines.append(f'<text x="{x}" y="102" font-size="34" font-weight="700" fill="{color}">{esc(value)}</text>')
        stat_lines.append(f'<text x="{x}" y="126" font-size="14" fill="{palette["muted"]}">{esc(label)}</text>')

    top = lang_mix[:4]
    bar_total = sum(pct for _, pct in top) or 1
    bar_x = 56
    bars = []
    for i, ((lang, pct), color) in enumerate(zip(top, palette["bars"])):
        w = round(1088 * (pct / bar_total))
        gap = 2 if i < len(top) - 1 else 0  # a background-coloured seam between segments
        bars.append(f'<rect x="{bar_x}" y="178" width="{max(w - gap, 1)}" height="10" fill="{color}"/>')
        bar_x += w

    legend = []
    lx = 60
    for (lang, pct), color in zip(top, palette["bars"]):
        label = f"{lang} {round(pct)}%"
        legend.append(f'<circle cx="{lx}" cy="209" r="5" fill="{color}"/>')
        legend.append(f'<text x="{lx + 12}" y="214" fill="{palette["muted"]}">{esc(label)}</text>')
        lx += 12 + round(len(label) * 14 * CHAR_W) + 28

    return f'''<svg width="1200" height="236" viewBox="0 0 1200 236" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(alt)}">
  <defs>
    <pattern id="grid2" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{palette["grid"]}" stroke-width="1"/>
    </pattern>
    <clipPath id="clip2"><rect width="1200" height="236" rx="14"/></clipPath>
  </defs>
  <g clip-path="url(#clip2)" font-family='{MONO}'>
    <rect width="1200" height="236" fill="{palette["bg"]}"/>
    <rect width="1200" height="236" fill="url(#grid2)"/>
    <text x="56" y="50" font-size="13" fill="{palette["label"]}" letter-spacing="1.5">GITHUB DATA, REGENERATED BY scripts/update_profile.py</text>
    {NL4.join(stat_lines)}
    <text x="56" y="164" font-size="13" fill="{palette["label"]}" letter-spacing="1">LANGUAGE MIX BY BYTES, OWN REPOS</text>
    <rect x="56" y="178" width="1088" height="10" rx="5" fill="{palette["track"]}"/>
    {NL4.join(bars)}
    <g font-size="14">
      {NL6.join(legend)}
    </g>
  </g>
</svg>
'''


def write_if_changed(path, content):
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    projects = fetch_projects()
    patches = fetch_patches()
    counts = count_states(patches)

    account = gh_json("api", f"users/{USER}")
    since_year = account["created_at"][:4]

    lang_bytes = {}
    for p in projects:
        for lang, n in repo_languages(p["name"]).items():
            lang_bytes[lang] = lang_bytes.get(lang, 0) + n
    total = sum(lang_bytes.values()) or 1
    lang_mix = sorted(((lang, 100 * n / total) for lang, n in lang_bytes.items()),
                      key=lambda x: (-x[1], x[0]))

    readme_path = ROOT / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    text = replace_marker_block(text, "projects", render_projects_table(projects))
    text = replace_marker_block(text, "patchsummary", patch_summary(text, counts))
    text = replace_marker_block(text, "patches", render_patches_block(patches))

    picture_block = (
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/stats.svg" />\n'
        '  <source media="(prefers-color-scheme: light)" srcset="assets/stats-light.svg" />\n'
        f'  <img src="assets/stats.svg" width="100%" alt="{esc(stats_alt(len(projects), since_year, counts, lang_mix))}" />\n'
        '</picture>'
    )
    text = replace_marker_block(text, "statsalt", picture_block)

    changed = [name for name, path, content in [
        ("README.md", readme_path, text),
        ("assets/stats.svg", ROOT / "assets" / "stats.svg",
         render_stats_svg(DARK, len(projects), since_year, counts, lang_mix)),
        ("assets/stats-light.svg", ROOT / "assets" / "stats-light.svg",
         render_stats_svg(LIGHT, len(projects), since_year, counts, lang_mix)),
    ] if write_if_changed(path, content)]

    print(f"projects: {len(projects)}, patches: {len(patches)} "
          f"({counts['merged']} merged, {counts['open']} open, {counts['closed']} closed), "
          f"since: {since_year}, top languages: {[(l, round(p, 2)) for l, p in lang_mix[:4]]}; "
          f"changed: {', '.join(changed) or 'nothing'}")


if __name__ == "__main__":
    main()
