"""Offline tests for the daily-oss-scout publish path.

Run: python3 -m unittest discover -s tests -v
No network: git remotes are local bare repos and `gh` is a stub on PATH.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import validate_findings_artifact as v  # noqa: E402

RUN_ID = "1234567890"
GOOD = "# Findings\n\n## repo-a\nclean. Unicode ok: é ✓\n".encode("utf-8")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.art = os.path.join(self.tmp, "artifact")
        self.dest = os.path.join(self.tmp, "repo")
        os.mkdir(self.art)
        os.mkdir(self.dest)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def put(self, name, data=GOOD):
        path = os.path.join(self.art, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        return path

    def run_v(self, run_id=RUN_ID):
        return v.validate_and_copy(self.art, run_id, self.dest)

    def assertRejected(self, run_id=RUN_ID):
        with self.assertRaises(v.ArtifactRejected):
            self.run_v(run_id)
        self.assertFalse(os.path.exists(os.path.join(self.dest, "findings", f"{RUN_ID}.md")))

    def test_accepts_good_file(self):
        self.put(f"{RUN_ID}.md")
        self.assertEqual(self.run_v(), f"findings/{RUN_ID}.md")
        with open(os.path.join(self.dest, "findings", f"{RUN_ID}.md"), "rb") as fh:
            self.assertEqual(fh.read(), GOOD)

    def test_accepts_exactly_max_size(self):
        self.put(f"{RUN_ID}.md", b"a" * v.MAX_BYTES)
        self.run_v()

    def test_rejects_wrong_name(self):
        self.put("999.md")
        self.assertRejected()

    def test_rejects_non_md_name(self):
        self.put(f"{RUN_ID}.sh")
        self.assertRejected()

    def test_rejects_nested_path(self):
        self.put(f"findings/{RUN_ID}.md")
        self.assertRejected()

    def test_rejects_traversal_run_id(self):
        self.put(f"{RUN_ID}.md")
        for bad in ("../1", "1/../2", "12a", "", "1 2", "1\n2"):
            with self.subTest(run_id=bad):
                self.assertRejected(run_id=bad)

    def test_rejects_oversize(self):
        self.put(f"{RUN_ID}.md", b"a" * (v.MAX_BYTES + 1))
        self.assertRejected()

    def test_rejects_empty(self):
        self.put(f"{RUN_ID}.md", b"")
        self.assertRejected()

    def test_rejects_non_utf8(self):
        self.put(f"{RUN_ID}.md", b"ok \xff\xfe bad")
        self.assertRejected()

    def test_rejects_nul(self):
        self.put(f"{RUN_ID}.md", b"ok\x00bad")
        self.assertRejected()

    def test_rejects_symlink_file(self):
        target = os.path.join(self.tmp, "secret.txt")
        with open(target, "wb") as fh:
            fh.write(b"secret")
        os.symlink(target, os.path.join(self.art, f"{RUN_ID}.md"))
        self.assertRejected()

    def test_rejects_symlinked_artifact_dir(self):
        real = os.path.join(self.tmp, "real")
        os.mkdir(real)
        with open(os.path.join(real, f"{RUN_ID}.md"), "wb") as fh:
            fh.write(GOOD)
        os.rmdir(self.art)
        os.symlink(real, self.art)
        self.assertRejected()

    def test_rejects_multiple_files(self):
        self.put(f"{RUN_ID}.md")
        self.put("extra.md")
        self.assertRejected()

    def test_rejects_directory_entry(self):
        os.mkdir(os.path.join(self.art, f"{RUN_ID}.md"))
        self.assertRejected()

    def test_rejects_symlinked_dest_findings_dir(self):
        self.put(f"{RUN_ID}.md")
        elsewhere = os.path.join(self.tmp, "elsewhere")
        os.mkdir(elsewhere)
        os.symlink(elsewhere, os.path.join(self.dest, "findings"))
        with self.assertRaises(v.ArtifactRejected):
            self.run_v()
        self.assertEqual(os.listdir(elsewhere), [])

    def test_refuses_to_overwrite(self):
        self.put(f"{RUN_ID}.md")
        os.mkdir(os.path.join(self.dest, "findings"))
        with open(os.path.join(self.dest, "findings", f"{RUN_ID}.md"), "wb") as fh:
            fh.write(b"existing")
        with self.assertRaises(FileExistsError):
            self.run_v()

    def test_cli_exit_codes(self):
        self.put("wrong.md")
        r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "validate_findings_artifact.py"),
                            "--artifact-dir", self.art, "--run-id", RUN_ID, "--dest-root", self.dest],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("REJECTED", r.stderr)


GH_STUB = """#!/usr/bin/env bash
# offline stand-in for gh: records argv, never touches the network
printf '%s\\0' "$@" >> "$GH_STUB_LOG"
printf '\\n' >> "$GH_STUB_LOG"
if [ "$1" = "pr" ] && [ "$2" = "create" ]; then
  while [ $# -gt 0 ]; do
    if [ "$1" = "--body-file" ]; then cp -- "$2" "$GH_STUB_BODY"; fi
    shift
  done
  echo "https://github.com/heykav/heykav/pull/999"
fi
exit 0
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


class PublishDryRunTests(unittest.TestCase):
    """End-to-end dry run of scripts/oss_scout_publish.sh against temp repos."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.remote = os.path.join(self.tmp, "remote.git")
        self.work = os.path.join(self.tmp, "work")
        self.art = os.path.join(self.tmp, "artifact")
        self.bin = os.path.join(self.tmp, "bin")
        os.mkdir(self.art)
        os.mkdir(self.bin)
        git(self.tmp, "init", "-q", "--bare", "-b", "main", self.remote)
        git(self.tmp, "init", "-q", "-b", "main", self.work)
        shutil.copytree(os.path.join(REPO, "scripts"), os.path.join(self.work, "scripts"))
        os.mkdir(os.path.join(self.work, "findings"))
        open(os.path.join(self.work, "findings", ".gitkeep"), "w").close()
        git(self.work, "add", "-A")
        git(self.work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
        git(self.work, "remote", "add", "origin", self.remote)
        git(self.work, "push", "-q", "origin", "main")
        with open(os.path.join(self.bin, "gh"), "w") as fh:
            fh.write(GH_STUB)
        os.chmod(os.path.join(self.bin, "gh"), 0o755)
        self.log = os.path.join(self.tmp, "gh.log")
        self.body = os.path.join(self.tmp, "body.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def publish(self, run_id=RUN_ID):
        env = {
            "PATH": self.bin + os.pathsep + os.environ.get("PATH", ""),
            "HOME": self.tmp,
            "RUN_ID": run_id,
            "ARTIFACT_DIR": self.art,
            "GH_TOKEN": "dummy-not-a-real-token",
            "GH_STUB_LOG": self.log,
            "GH_STUB_BODY": self.body,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        return subprocess.run(["bash", "scripts/oss_scout_publish.sh"], cwd=self.work, env=env,
                              capture_output=True, text=True)

    def test_happy_path_with_hostile_content(self):
        hostile = ('# x\n$(touch /tmp/pwned) `id` "; rm -rf / #\n'
                   "---\n--title evil --base attacker\n").encode()
        with open(os.path.join(self.art, f"{RUN_ID}.md"), "wb") as fh:
            fh.write(hostile)
        r = self.publish()
        self.assertEqual(r.returncode, 0, r.stderr)
        branches = git(self.remote, "branch", "--list", "oss-scout/*").split()
        self.assertEqual(len(branches), 1)
        branch = branches[0]
        self.assertRegex(branch, rf"^oss-scout/\d{{4}}-\d{{2}}-\d{{2}}-{RUN_ID}$")
        files = git(self.remote, "diff", "--name-only", "main", branch).split()
        self.assertEqual(files, [f"findings/{RUN_ID}.md"])
        self.assertEqual(git(self.remote, "show", f"{branch}:findings/{RUN_ID}.md").encode(), hostile)
        with open(self.log, "rb") as fh:
            calls = [c.split(b"\0")[:-1] for c in fh.read().split(b"\n") if c]
        self.assertEqual(calls[0], [b"auth", b"setup-git"])
        pr = calls[1]
        self.assertEqual(pr[:3], [b"pr", b"create", b"--draft"])
        self.assertNotIn(b"--body", pr)
        self.assertNotIn(b"evil", b" ".join(pr))
        with open(self.body, encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn(f"findings/{RUN_ID}.md", body)
        self.assertNotIn("pwned", body)
        self.assertFalse(os.path.exists("/tmp/pwned"))

    def test_rejected_artifact_pushes_nothing(self):
        with open(os.path.join(self.art, "evil.md"), "wb") as fh:
            fh.write(GOOD)
        r = self.publish()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(git(self.remote, "branch", "--list", "oss-scout/*").strip(), "")
        self.assertFalse(os.path.exists(self.log))

    def test_non_numeric_run_id_rejected(self):
        r = self.publish(run_id="1;id")
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(self.log))


if __name__ == "__main__":
    unittest.main()
