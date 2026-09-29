# daily-oss-scout: threat model

Scope: `.github/workflows/daily-oss-scout.yml`, `scripts/oss_scout_publish.sh`,
`scripts/validate_findings_artifact.py`. Status: **not activated** (lives on a
draft PR branch; nothing has been dispatched).

## What the workflow does

Triggers: `schedule` and `workflow_dispatch` only. Two jobs:

| Job | Trust | Token scope | Secrets | Runs |
| --- | --- | --- | --- | --- |
| `analyze` | UNTRUSTED | `contents: read` | `CLAUDE_CODE_OAUTH_TOKEN` | Claude reading shallow clones of 3 third-party repos; writes `findings/<run_id>.md`; uploads it as an artifact |
| `publish` | TRUSTED | `contents: write`, `pull-requests: write` | none (only `github.token`) | Repo-controlled scripts: validate artifact, commit to `oss-scout/<date>-<run_id>`, open a **draft** PR in this repo |

The workflow never forks, pushes to, or opens PRs/issues on third-party repos.

## Assets

1. `GITHUB_TOKEN` with write scope (can push to and open PRs in heykav/heykav).
2. `CLAUDE_CODE_OAUTH_TOKEN` (bills/acts as the account's Claude subscription;
   long-lived until revoked).
3. Integrity of this repo's branches and of the findings a human will act on.

## Threats and mitigations

**T1. Untrusted repo contents / install hooks executing on the runner**
(`setup.py`, `postinstall`, `conftest.py`, `Makefile`, test suites).
The original design let the model run `pip`, `npm`, `pytest`, `python` in
fresh clones - i.e. arbitrary third-party code with both secrets in reach.
Mitigation: `--allowedTools` is now `Read,Glob,Grep,Write,Bash(git clone --depth 1 https://github.com/*)`.
No install/build/test/interpreter is permitted, so third-party code is read,
never executed. `GIT_ALLOW_PROTOCOL=https` blocks `ext::`/`file://`/ssh
transports; `git clone` does not run repo-supplied hooks, and submodules are
not fetched. Trade-off: findings are reasoned, not executed - the prompt
requires the model to say its repro is unexecuted.

**T2. GITHUB_TOKEN exfiltration/misuse.**
Original: job-wide `contents: write` + `pull-requests: write` and
`actions/checkout` persisting the token in `.git/config`, in the same job that
ran third-party code. Now: `analyze` has `contents: read` only and
`persist-credentials: false`; the only write token lives in `publish`, which
runs no model and no third-party code, and uses `persist-credentials: false`
plus `gh auth setup-git` (token stays in the environment, never in
`.git/config` or argv). Also found in the action source
(`src/github/token.ts`, v1.0.236): when no `github_token` input is given the
action requests an OIDC token and exchanges it for a Claude GitHub App token,
which `run.ts` then exports as `GITHUB_TOKEN`/`GH_TOKEN` for the model's
tools. We pass `github_token: ${{ github.token }}` (read-only, expires at job
end) and do **not** grant `id-token: write`, so no App token is minted.

**T3. Claude OAuth secret exposure.** The token is in the environment of the
action's step and the Claude CLI process, and is inherited by child processes
unless scrubbed. The action documents (action.yml, `allowed_non_write_users`):
"Claude does a best-effort scrub of Anthropic, cloud, and GitHub Actions
secrets from subprocess environments. This reduces but does not eliminate
prompt injection risk". We set `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: "1"` at job
level (the action forwards `env.CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`). This is
**not** a boundary: without bubblewrap PID isolation (which the action only
installs when `allowed_non_write_users` is set) a same-UID child can still read
the parent's `/proc/<pid>/environ`. The real mitigation is T1: no third-party
code runs, so the only processes that can read the token are the runner, the
action, the Claude CLI and `git`. **Re-enabling pip/npm/pytest/python would
re-expose the token to arbitrary code; do not do so.** Revocation path if
exposure is suspected: revoke the token from the Claude account, generate a
new one (`claude setup-token`), replace the `CLAUDE_CODE_OAUTH_TOKEN` repo secret, review
Anthropic account usage. `show_full_output` must stay off (logs could echo
secrets or tool output).

**T4. Prompt injection from repo content** (README/comments saying "ignore
previous instructions, write X"). Cannot be prevented, only contained. The
prompt declares repo text as data, but the design assumes injection succeeds:
the model can then only (a) clone more public repos over https, (b) write
files in the analyze workspace, (c) put arbitrary text in the findings file.
(a)/(b) have no write path to any repo; (c) lands only as a file in a draft PR
reviewed by a human (PRs created with `GITHUB_TOKEN` do not trigger other
workflows). Reviewers must treat findings text, links and diffs as untrusted.

**T5. Shell/command injection.** No `${{ }}` appears inside any `run:`
script; `github.run_id`, `runner.temp` and `github.token` reach shells only via
`env:`. `RUN_ID` is re-checked against `^[0-9]{1,20}$`. Model output is
never used as a shell word, branch name, commit message, PR title or PR body:
branch = `oss-scout/<UTC date>-<run_id>`, title/body are fixed text, body is
passed with `--body-file`. The dry-run test feeds hostile content
(`$(...)`, backticks, `--title evil`) and asserts it is committed byte-for-byte
and nowhere else.

**T6. Artifact tampering / path traversal / oversized output.** The artifact
is produced by the untrusted job, so its *content* is untrusted by definition;
`publish` treats it as data. `validate_findings_artifact.py`: destination name
built from `run_id` (never from artifact names) and matched against
`^findings/[0-9]+\.md$`; exactly one entry, a regular file named
`<run_id>.md`; symlinks (file or directory) rejected; size 1..200 KB; strict
UTF-8; no NUL bytes; opened with `O_NOFOLLOW`; written with
`O_CREAT|O_EXCL|O_NOFOLLOW` into a real `findings/` directory; the script
then refuses to commit if anything other than that one path is staged.
`download-artifact` defaults to `digest-mismatch: error`.

**T7. Workflow write permissions.** Top-level `permissions: {}`; each job
opts in (read-only for `analyze`, write only for `publish`). The draft PR
still requires the repo setting "Allow GitHub Actions to create and approve
pull requests"; merging always stays a human action.

**T8. Fork / `pull_request_target` behaviour.** Not applicable today: no PR
triggers exist, so fork code and fork-controlled event fields never reach this
workflow. Guard to keep it that way: both jobs have
`if: github.repository == 'heykav/heykav' && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch')`,
so adding a PR/`workflow_run` trigger later does not run either job, and forks
of this repo do not run it on their schedules. `workflow_dispatch` requires
write access to the repo. The unused `repos` dispatch input was removed.

**T9. Supply chain of actions.** All actions are pinned to full commit SHAs,
resolved on 2026-09-29 with `git ls-remote` against github.com (the tag is
recorded in a trailing comment): checkout v7.0.1 `3d3c42e5...`,
upload-artifact v7.0.1 `043fb46d...`, download-artifact v8.0.1 `3e5f45b2...`,
claude-code-action v1.0.236 `8ce9314f...` (peeled from the annotated tag).
Residual: a SHA pin only freezes the action's own repo; claude-code-action
still installs Bun and npm dependencies and the Claude CLI at run time, and
the pins must be bumped deliberately (e.g. Dependabot for `github-actions`).

**T10. Cost / runaway.** `timeout-minutes` 45 (analyze) / 10 (publish);
`concurrency: daily-oss-scout` without cancellation so runs never overlap.

## Residual risks (accepted, not eliminated)

- The Claude OAuth token remains present in the `analyze` job. It is exposed
  to the runner, the action and its dependencies, the Claude CLI and `git` -
  not to third-party code, as long as the no-execution tool list stands.
- Prompt injection can make the findings misleading or malicious-looking
  (bad diffs, phishing links). Human review is the control.
- Claude Code permission matching for `Bash(git clone --depth 1 https://github.com/*)`
  is prefix/wildcard based; an injected model could append extra `git clone`
  flags. `GIT_ALLOW_PROTOCOL=https` and the lack of any write token bound the
  impact, but this is defence in depth, not a proof.
- Runtime-installed dependencies of claude-code-action are not pinned by us.

## Activation verdict

Defensible **only** in the committed no-third-party-execution configuration,
after a human reviews this PR, the repo setting for Actions-created PRs is
confirmed, and the owner accepts the residual risks above. Activation (merge
to the default branch) remains a manual decision; this change does not
enable, dispatch or merge anything.
