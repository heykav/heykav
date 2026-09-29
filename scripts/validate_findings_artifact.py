#!/usr/bin/env python3
"""Validate the daily-oss-scout findings artifact and copy it to a fixed path.

Used by the TRUSTED `publish` job of .github/workflows/daily-oss-scout.yml.
The artifact was produced by the UNTRUSTED `analyze` job (model output that
may have been steered by third-party repository content), so it is treated
strictly as data:

  * the destination name is built from the run id (numeric) - never from any
    name found inside the artifact;
  * the artifact directory must contain exactly one entry: a regular file
    named "<run_id>.md" (no subdirectories, no symlinks, no other files);
  * size must be 1..MAX_BYTES bytes;
  * content must be strict UTF-8 and contain no NUL bytes;
  * the destination "findings/<run_id>.md" must match ^findings/[0-9]+\\.md$,
    must not exist yet, and neither it nor its parent may be a symlink.

Exit status 0 on success (prints the destination path), 1 on rejection.
Standard library only; no network.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys

MAX_BYTES = 200 * 1024
RUN_ID_RE = re.compile(r"^[0-9]{1,20}$")
DEST_RE = re.compile(r"^findings/[0-9]+\.md$")


class ArtifactRejected(Exception):
    pass


def validate_and_copy(artifact_dir: str, run_id: str, dest_root: str,
                      max_bytes: int = MAX_BYTES) -> str:
    if not RUN_ID_RE.fullmatch(run_id or ""):
        raise ArtifactRejected("run id is not purely numeric")

    rel_dest = f"findings/{run_id}.md"
    if not DEST_RE.fullmatch(rel_dest):
        raise ArtifactRejected("destination path failed pattern check")
    expected_name = f"{run_id}.md"

    st = os.lstat(artifact_dir)
    if not stat.S_ISDIR(st.st_mode):
        raise ArtifactRejected("artifact dir is not a real directory")

    entries = os.listdir(artifact_dir)
    if len(entries) != 1:
        raise ArtifactRejected(f"expected exactly 1 entry, found {len(entries)}")
    if entries[0] != expected_name:
        raise ArtifactRejected("artifact file name does not match run id")

    src = os.path.join(artifact_dir, expected_name)
    st = os.lstat(src)
    if stat.S_ISLNK(st.st_mode):
        raise ArtifactRejected("artifact file is a symlink")
    if not stat.S_ISREG(st.st_mode):
        raise ArtifactRejected("artifact entry is not a regular file")
    if st.st_size == 0:
        raise ArtifactRejected("artifact file is empty")
    if st.st_size > max_bytes:
        raise ArtifactRejected(f"artifact file too large ({st.st_size} > {max_bytes})")

    # O_NOFOLLOW closes the lstat->open race for the final component.
    fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as fh:
        data = fh.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ArtifactRejected("artifact file grew past size cap")
    if b"\x00" in data:
        raise ArtifactRejected("artifact file contains NUL bytes")
    try:
        data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ArtifactRejected(f"artifact file is not valid UTF-8: {exc}") from None

    root = os.path.realpath(dest_root)
    findings_dir = os.path.join(root, "findings")
    if os.path.lexists(findings_dir):
        fst = os.lstat(findings_dir)
        if stat.S_ISLNK(fst.st_mode) or not stat.S_ISDIR(fst.st_mode):
            raise ArtifactRejected("destination findings/ is not a real directory")
    else:
        os.mkdir(findings_dir)
    dest = os.path.join(root, rel_dest)
    if os.path.dirname(dest) != findings_dir:
        raise ArtifactRejected("destination escaped findings/")

    # O_EXCL + O_NOFOLLOW: never overwrite, never write through a symlink.
    out = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(out, "wb") as fh:
        fh.write(data)
    return rel_dest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--artifact-dir", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--dest-root", required=True)
    p.add_argument("--max-bytes", type=int, default=MAX_BYTES)
    a = p.parse_args(argv)
    try:
        rel = validate_and_copy(a.artifact_dir, a.run_id, a.dest_root, a.max_bytes)
    except (ArtifactRejected, OSError) as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 1
    print(rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
