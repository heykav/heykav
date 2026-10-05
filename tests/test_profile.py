"""Offline checks for curated onboarding and the public repository boundary."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("profile_update", ROOT / "scripts/update_profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class StartHereTests(unittest.TestCase):
    def project(self, name="public"):
        return dict(name=name, url=f"https://github.com/heykav/{name}",
                    entrypoint="Run | inspect", evidence="[Guide](https://example.com)",
                    limitation="Simulation\nonly", description="demo", tags=["Python"])

    def test_table(self):
        rendered = profile.render_start_here([self.project()])
        self.assertIn("Run &#124; inspect", rendered)
        self.assertIn("Simulation only", rendered)
        self.assertIn("[public]", rendered)

    def test_missing_optional_field_skips_row(self):
        for field in ("entrypoint", "evidence", "limitation"):
            project = self.project()
            del project[field]
            self.assertNotIn("[public]", profile.render_start_here([project]))

    def test_private_deleted_and_forks_are_excluded(self):
        overrides = {name: self.project(name) for name in ("public", "secret", "deleted", "fork")}
        repos = [dict(name=name, private=name == "secret", fork=name == "fork",
                      pushed_at="2026-01-01", html_url=f"https://github.com/heykav/{name}",
                      description="demo") for name in ("public", "secret", "fork", "new")]
        with patch.object(profile, "gh_json", return_value=repos), \
             patch.object(profile, "load_overrides", return_value=overrides), \
             patch.object(profile, "repo_languages", return_value={"Python": 1}):
            projects = profile.fetch_projects()
        self.assertEqual({p["name"] for p in projects}, {"public", "new"})
        table = profile.render_start_here(projects)
        self.assertIn("[public]", table)
        for name in ("secret", "deleted", "fork", "new"):
            self.assertNotIn(f"[{name}]", table)

    def test_markers_preserve_unrelated_text(self):
        before = "Bio\n<!-- AUTO:start-here:start -->\nold\n<!-- AUTO:start-here:end -->\nOther"
        self.assertEqual(profile.replace_marker_block(before, "start-here", "new"),
                         before.replace("\nold\n", "\nnew\n"))
        for bad in ("no marker", before + before):
            with self.assertRaises(SystemExit):
                profile.replace_marker_block(bad, "start-here", "new")

    def test_committed_table_contains_only_curated_entries(self):
        data = profile.load_overrides("projects")
        readme = (ROOT / "README.md").read_text()
        table = profile.read_marker_block(readme, "start-here")
        rows = table.splitlines()[2:]
        # Public-state changes may safely remove a curated row at refresh time.
        # Every remaining row must still match exactly one curated rendering.
        allowed = {
            profile.render_start_here([dict(name=name,
                url=f"https://github.com/heykav/{name}", **item)]).splitlines()[-1]
            for name, item in data.items()
        }
        self.assertEqual(len(rows), len(set(rows)))
        self.assertTrue(set(rows).issubset(allowed))


if __name__ == "__main__":
    unittest.main()
