#!/usr/bin/env bash
# Trusted publish step for .github/workflows/daily-oss-scout.yml.
#
# Inputs (environment only - nothing is interpolated into this script):
#   RUN_ID        numeric workflow run id (github.run_id)
#   ARTIFACT_DIR  directory the findings artifact was downloaded into
#   GH_TOKEN      token for git push + gh pr create (github.token)
#   BASE_BRANCH   optional, defaults to main
#
# The findings file is model output and is only ever handled as file DATA:
# it is validated and copied by scripts/validate_findings_artifact.py and
# committed as-is. The PR body is fixed text passed via --body-file. The
# findings contents never reach a shell word, a commit message, a branch
# name, the PR title or the PR body.
set -euo pipefail

: "${RUN_ID:?RUN_ID is required}"
: "${ARTIFACT_DIR:?ARTIFACT_DIR is required}"
: "${GH_TOKEN:?GH_TOKEN is required}"
BASE_BRANCH="${BASE_BRANCH:-main}"

if [[ ! "$RUN_ID" =~ ^[0-9]{1,20}$ ]]; then
  echo "RUN_ID is not numeric" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

rel="$(python3 scripts/validate_findings_artifact.py \
  --artifact-dir "$ARTIFACT_DIR" --run-id "$RUN_ID" --dest-root "$repo_root")"
expected="findings/${RUN_ID}.md"
if [ "$rel" != "$expected" ]; then
  echo "validator returned unexpected path" >&2
  exit 1
fi

day="$(date -u +%Y-%m-%d)"
branch="oss-scout/${day}-${RUN_ID}"

git switch -c "$branch"
git add -- "$expected"
staged="$(git diff --cached --name-only)"
if [ "$staged" != "$expected" ]; then
  echo "unexpected staged changes; refusing to commit" >&2
  exit 1
fi

git -c user.name="oss-scout-bot" \
    -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
    commit -q \
    -m "Daily OSS scout findings: ${day} (run ${RUN_ID})" \
    -m "Model-generated findings file; review before acting on it."

# Credentials come from GH_TOKEN via gh's git credential helper, so no token
# is written into .git/config or placed on a command line.
gh auth setup-git
git push origin "refs/heads/${branch}:refs/heads/${branch}"

body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT
cat > "$body_file" <<EOF
Automated daily scan of 3 external repos (workflow run ${RUN_ID}).

Review \`${expected}\`. It is **model-generated output from an untrusted
analysis job** that read third-party code: treat claims, links and diffs in it
as unverified until you reproduce them yourself. Nothing is forked, pushed or
opened upstream by this workflow; any upstream PR is a manual human action.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF

gh pr create \
  --draft \
  --base "$BASE_BRANCH" \
  --head "$branch" \
  --title "OSS scout findings: ${day} (run ${RUN_ID})" \
  --body-file "$body_file"
