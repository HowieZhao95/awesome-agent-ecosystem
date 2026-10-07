import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("source_sync_core", ROOT / "scripts/source_tools/core.py")
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


class SourceSyncTests(unittest.TestCase):
    def test_identical_locked_snapshots_have_no_changes(self):
        old = {"ref": "a" * 40, "files": {"x/SKILL.md": {"sha256": "1", "metadata": {"name": "x"}}}}
        new = {"ref": "b" * 40, "files": {"x/SKILL.md": {"sha256": "1", "metadata": {"name": "x"}}}}
        self.assertEqual(core.diff_snapshots(old, new)["changes"], [])

    def test_reports_added_changed_removed_and_content_rename(self):
        old = {"ref": "a", "files": {"old/SKILL.md": {"sha256": "same", "metadata": {}}, "changed": {"sha256": "old", "metadata": {}}, "removed": {"sha256": "gone", "metadata": {}}}}
        new = {"ref": "b", "files": {"new/SKILL.md": {"sha256": "same", "metadata": {}}, "changed": {"sha256": "new", "metadata": {}}, "added": {"sha256": "fresh", "metadata": {}}}}
        changes = core.diff_snapshots(old, new)["changes"]
        self.assertEqual({(x["kind"], x.get("path"), x.get("from"), x.get("to")) for x in changes}, {
            ("rename", None, "old/SKILL.md", "new/SKILL.md"), ("changed", "changed", None, None),
            ("removed", "removed", None, None), ("added", "added", None, None),
        })

    def test_duplicate_content_renames_pair_one_to_one_deterministically(self):
        old = {"files": {"a/1": {"sha256": "same", "metadata": {}}, "b/1": {"sha256": "same", "metadata": {}}}}
        new = {"files": {"a/2": {"sha256": "same", "metadata": {}}, "b/2": {"sha256": "same", "metadata": {}}}}
        changes = core.diff_snapshots(old, new)["changes"]
        self.assertEqual([(change["from"], change["to"]) for change in changes], [("a/1", "a/2"), ("b/1", "b/2")])

    def test_identity_rename_detected_even_when_content_changes(self):
        old = {"files": {"old/open-design.json": {"sha256": "1", "identity": "plugin:card", "metadata": {}}}}
        new = {"files": {"new/open-design.json": {"sha256": "2", "identity": "plugin:card", "metadata": {}}}}
        change = core.diff_snapshots(old, new)["changes"]
        self.assertEqual(change[0]["kind"], "rename")
        self.assertEqual(change[0]["content_changed"], True)

    def test_failed_snapshot_does_not_replace_existing_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "upstream"
            target = root / "skills/remotion-best-practices"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: [invalid\n---\nbody")
            baseline = Path(td) / "baseline.json"
            expected = '{"ref":"' + "b" * 40 + '","files":{"kept":{"sha256":"abc"}}}\n'
            baseline.write_text(expected)
            output = Path(td) / "candidate.json"
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/source-sync.py"), "--source", "remotion", "--ref", "c" * 40,
                "--directory", str(root), "--baseline", str(baseline), "--output", str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(baseline.read_text(), expected)
            diff = json.loads(output.read_text())["diff"]
            self.assertFalse(diff["complete"])
            self.assertEqual(diff["changes"], [])
            self.assertTrue(diff["suppressed_incomplete_removals"])

    def test_partial_snapshot_lists_failures_without_dropping_successes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "x").mkdir()
            (root / "x/SKILL.md").write_text("---\nname: demo\ndescription: Demo\n---\nBody must not be retained")
            result = core.snapshot_directory(root, "remotion", "c" * 40, selected=["x/SKILL.md", "missing/SKILL.md"])
            self.assertIn("x/SKILL.md", result["files"])
            self.assertEqual(result["failures"], ["missing/SKILL.md"])
            self.assertEqual(result["files"]["x/SKILL.md"]["metadata"]["name"], "demo")
            self.assertNotIn("Body must not be retained", json.dumps(result))

    def test_mutable_ref_rejected_for_public_snapshot(self):
        with self.assertRaises(core.SnapshotError):
            core.validate_locked_ref("main")
        self.assertEqual(core.validate_locked_ref("d" * 40), "d" * 40)

    def test_metadata_fingerprint_is_stable(self):
        left = core.file_record("x/SKILL.md", b"---\nname: Demo\ndescription: D\n---\nfirst body")
        right = core.file_record("x/SKILL.md", b"---\nname: Demo\ndescription: D\n---\nsecond body")
        self.assertEqual(left["metadata_fingerprint"], right["metadata_fingerprint"])
        self.assertNotEqual(left["sha256"], right["sha256"])

    def test_manifest_metadata_is_retained_without_manifest_body(self):
        record = core.file_record("plugins/card/open-design.json", b'{"id":"card","name":"Card","license":"MIT","privateBody":"secret"}')
        self.assertEqual(record["identity"], "card")
        self.assertEqual(record["metadata"]["license"], "MIT")
        self.assertNotIn("secret", json.dumps(record))

    def test_invalid_selected_frontmatter_marks_snapshot_incomplete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "bad").mkdir()
            (root / "bad/SKILL.md").write_text("---\nname: [invalid\n---\nbody")
            snapshot = core.snapshot_directory(root, "remotion", "c" * 40, ["bad/SKILL.md"])
            self.assertEqual(snapshot["files"], {})
            self.assertEqual(snapshot["failures"][0]["path"], "bad/SKILL.md")

    def test_legacy_discovery_exports_only_selected_public_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "legacy.yaml"
            source.write_text("categories:\n- id: skills\n  entries:\n  - name: one\n    url: https://example.org/one\n    note: first\n    stars: 99\n  - name: two\n    url: https://example.org/two\n    note: second\n")
            snapshot = core.snapshot_discovery(source, "f" * 40, ["skills/one"])
            self.assertEqual(list(snapshot["files"]), ["skills/one"])
            self.assertNotIn("stars", json.dumps(snapshot))
            self.assertNotIn("skills/two", json.dumps(snapshot))

    def test_partial_snapshot_suppresses_ambiguous_removals(self):
        old = {"files": {"gone": {"sha256": "old", "metadata": {}}}}
        new = {"files": {}, "failures": ["unreadable"]}
        diff = core.review_diff(old, new)
        self.assertEqual(diff["changes"], [])
        self.assertEqual([change["path"] for change in diff["suppressed_incomplete_removals"]], ["gone"])

    def test_cli_reads_new_locked_commit_against_catalog_baseline_ref(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "upstream"
            for name in ("remotion-best-practices",):
                folder = root / "skills" / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(f"---\nname: {name}\n---\nPrivate body is never in output")
            output = Path(td) / "candidate.json"
            baseline = Path(td) / "baseline.json"
            baseline_data = {"ref": "b" * 40, "files": {"skills/remotion-render/SKILL.md": {"sha256": "old-content", "identity": "remotion-render", "metadata": {"name": "remotion-render"}}}}
            baseline.write_text(json.dumps(baseline_data))
            baseline_before = baseline.read_text()
            sha = "a" * 40
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/source-sync.py"), "--source", "remotion", "--ref", sha,
                "--directory", str(root), "--baseline", str(baseline), "--output", str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(report["snapshot"]["ref"], sha)
            self.assertEqual(report["snapshot"]["catalog_baseline_refs"], ["473352613039e718e46655a26df224851e84c4aa"])
            self.assertTrue(report["snapshot"]["complete"])
            self.assertEqual([item["kind"] for item in report["diff"]["changes"]], ["removed", "added"])
            self.assertEqual(report["diff"]["changes"][0]["path"], "skills/remotion-render/SKILL.md")
            self.assertTrue(report["snapshot"]["catalog_missing_paths"])
            self.assertEqual(baseline.read_text(), baseline_before)
            self.assertNotIn("Private body", output.read_text())

    def test_archive_root_binds_snapshot_to_selected_repository_and_sha(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wrong-root"
            root.mkdir()
            (root / "selected.txt").write_text("candidate")
            archive = Path(td) / "fixture.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(root, arcname="remotion-skills-" + "c" * 40)
            with self.assertRaises(core.SnapshotError):
                core.snapshot_archive(archive, "remotion", "d" * 40, ["selected.txt"])

    def test_remote_url_must_name_the_selected_repository_and_sha(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate.json"
            sha = "d" * 40
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/source-sync.py"), "--source", "remotion", "--ref", sha,
                "--url", f"https://github.com/other/skills/archive/{sha}.tar.gz", "--output", str(output),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remotion-dev/skills", result.stderr)
            self.assertFalse(output.exists())

    def test_cli_refuses_canonical_output_and_baseline_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td) / "upstream"
            directory.mkdir()
            baseline = Path(td) / "baseline.json"
            original = '{"ref":"locked","files":{}}\n'
            baseline.write_text(original)
            args = [sys.executable, str(ROOT / "scripts/source-sync.py"), "--source", "remotion", "--ref", "e" * 40,
                    "--directory", str(directory), "--baseline", str(baseline)]
            result = subprocess.run(args + ["--output", str(baseline)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(baseline.read_text(), original)
            canonical = ROOT / "data/resources.yaml"
            before = canonical.read_bytes()
            result = subprocess.run(args[:6] + ["--directory", str(directory), "--output", str(canonical)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(canonical.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
