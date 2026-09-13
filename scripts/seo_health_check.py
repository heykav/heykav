#!/usr/bin/env python3
"""
Daily SEO/link health audit across every real (non-fork) heykav/* repo,
plus the personal domain.

Three things, all deterministic - same "no LLM call in the Action" rule
as scripts/update_profile.py, since this runs unattended with no review:

1. Health-checks every live page this portfolio actually has (each real
   repo's GitHub Pages site, if it has one, plus krishnaanubhav.com) and
   records the HTTP status. A page that's down, or a personal-domain page
   that's reverted to the Hostinger parked-page placeholder, makes this
   script exit non-zero - that's the one case worth an actual failed-run
   notification, not just a quiet log line.
2. Compares each repo's declared `homepage` field against its actual
   Pages URL and fixes a mismatch - but only when a cross-repo token
   (the SEO_PAT secret) is configured, since the workflow's own
   GITHUB_TOKEN is scoped to this repo and can't write to another repo's
   settings. Without SEO_PAT, a mismatch is recorded but not silently
   left unmentioned.
3. Flags any real repo with an empty description or empty topics list -
   this script never invents that copy itself, it just surfaces the gap
   so a human (or a future Claude session) fills it in deliberately.

Writes reports/seo-status.md and commits it if it changed - the same
"regenerate deterministically, commit only on real change" pattern
update_profile.py already uses.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "heykav"
OWN_REPO = "heykav"

PERSONAL_SITE = "https://krishnaanubhav.com"
# What the Hostinger "Default page" placeholder actually serves - used to
# tell "still parked" apart from "a real 200 you put content behind."
PARKED_SIGNATURE = "hostinger.com/favicons"


def gh_json(*args, token=None):
    env = {**os.environ, "GH_TOKEN": token} if token else os.environ
    out = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def fetch_real_repos():
    repos = gh_json("api", f"users/{USER}/repos", "--paginate") or []
    return [
        r
        for r in repos
        if not r["fork"] and not r["private"] and not r["archived"] and r["name"] != OWN_REPO
    ]


def check_url(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "seo-health-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(20_000).decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - network errors, report don't crash
        return None, str(e)


def get_pages_html_url(repo):
    info = gh_json("api", f"repos/{USER}/{repo}/pages")
    if info and info.get("status") != "errored":
        return info.get("html_url")
    return None


def try_fix_homepage(repo, correct_url, pat):
    result = subprocess.run(
        ["gh", "api", "--method", "PATCH", f"repos/{USER}/{repo}", "-f", f"homepage={correct_url}"],
        env={**os.environ, "GH_TOKEN": pat},
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pat = os.environ.get("SEO_PAT")
    repos = fetch_real_repos()

    page_checks = []
    homepage_mismatches = []
    metadata_gaps = []
    any_page_down = False

    status, body = check_url(PERSONAL_SITE)
    parked = status == 200 and PARKED_SIGNATURE in body
    ok = status == 200 and not parked
    if not ok:
        any_page_down = True
    page_checks.append(
        {
            "label": "personal site",
            "url": PERSONAL_SITE,
            "status": status,
            "ok": ok,
            "note": "still showing the Hostinger parked-domain placeholder" if parked else None,
        }
    )

    for r in repos:
        name = r["name"]
        pages_url = get_pages_html_url(name)

        if pages_url:
            status, _ = check_url(pages_url)
            ok = status == 200
            if not ok:
                any_page_down = True
            page_checks.append(
                {"label": name, "url": pages_url, "status": status, "ok": ok, "note": None}
            )

            declared = (r.get("homepage") or "").rstrip("/")
            actual = pages_url.rstrip("/")
            if declared != actual:
                fixed = try_fix_homepage(name, pages_url, pat) if pat else False
                homepage_mismatches.append(
                    {"repo": name, "declared": declared or "(none)", "actual": actual, "fixed": fixed}
                )

        if not r.get("description") or not r.get("topics"):
            metadata_gaps.append(
                {
                    "repo": name,
                    "missing_description": not r.get("description"),
                    "missing_topics": not r.get("topics"),
                }
            )

    lines = [
        "# SEO / link health",
        "",
        f"_Last checked: {now}, by `scripts/seo_health_check.py`. "
        "Regenerated daily; hand edits here will just be overwritten._",
        "",
        "## Live pages",
        "",
    ]
    for c in page_checks:
        mark = "OK" if c["ok"] else "DOWN"
        note = f" — {c['note']}" if c["note"] else ""
        lines.append(f"- **{mark}** ({c['status']}) [{c['label']}]({c['url']}){note}")

    lines += ["", "## Homepage URL vs. actual Pages URL", ""]
    if homepage_mismatches:
        for m in homepage_mismatches:
            fixed_note = "auto-fixed" if m["fixed"] else "**not fixed — SEO_PAT secret not set**"
            lines.append(
                f"- `{m['repo']}`: homepage was `{m['declared']}`, Pages serves `{m['actual']}` — {fixed_note}"
            )
    else:
        lines.append("Every repo's `homepage` field matches its live Pages URL.")

    lines += ["", "## Repos missing a description or topics", ""]
    if metadata_gaps:
        for g in metadata_gaps:
            missing = []
            if g["missing_description"]:
                missing.append("description")
            if g["missing_topics"]:
                missing.append("topics")
            lines.append(f"- `{g['repo']}`: missing {', '.join(missing)}")
    else:
        lines.append("None — every real repo has both set.")

    lines.append("")

    out_path = ROOT / "reports" / "seo-status.md"
    out_path.parent.mkdir(exist_ok=True)
    new_content = "\n".join(lines)
    out_path.write_text(new_content)

    if any_page_down:
        print("SEO health check: at least one monitored page is down or parked.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
