import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "auto_source_sync", ROOT / "scripts/auto-source-sync.py"
)
auto = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(auto)


class Response:
    def __init__(self, body, status=200):
        self._body = body
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")

    def json(self):
        return self._body


class AutoSourceSyncTests(unittest.TestCase):
    def test_catalog_candidate_and_snapshot_are_updated_together_without_duplicate_writes(self):
        writer = getattr(auto, 'write_catalog_candidates', None)
        self.assertTrue(callable(writer), 'catalog candidate writer must be implemented')
        manifest = json.loads((ROOT / 'data/catalog-manifest.json').read_text())
        report = json.loads((ROOT / 'docs/evidence/source-sync/opendesign.json').read_text())
        report['snapshot']['ref'] = 'f' * 40
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / 'catalog-manifest.json'
            target.write_text(json.dumps(manifest))
            self.assertEqual(writer({'opendesign': report}, root / 'reports', target), ['opendesign', 'catalog-manifest'])
            updated = json.loads(target.read_text())
            self.assertEqual(updated['source_commit'], 'f' * 40)
            self.assertEqual(updated['resource_id'], manifest['resource_id'])
            before = target.read_bytes()
            self.assertEqual(writer({'opendesign': report}, root / 'reports', target), [])
            self.assertEqual(target.read_bytes(), before)

    def test_invalid_catalog_candidate_does_not_replace_existing_source_report(self):
        writer = getattr(auto, 'write_catalog_candidates', None)
        self.assertTrue(callable(writer), 'catalog candidate writer must be implemented')
        manifest = json.loads((ROOT / 'data/catalog-manifest.json').read_text())
        report = json.loads((ROOT / 'docs/evidence/source-sync/opendesign.json').read_text())
        report['snapshot']['complete'] = False
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / 'catalog-manifest.json'
            target.write_text(json.dumps(manifest))
            output = root / 'reports'
            output.mkdir()
            prior = output / 'opendesign.json'
            prior.write_text('kept')
            with self.assertRaises(RuntimeError):
                writer({'opendesign': report}, output, target)
            self.assertEqual(prior.read_text(), 'kept')
    def test_incomplete_snapshot_fails_before_replacing_prior_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            prior = output / "opendesign.json"
            prior.write_text('{"snapshot":{"ref":"kept"}}\n')
            before = prior.read_bytes()
            partial = {"snapshot": {"ref": "b" * 40, "complete": False,
                                    "failures": [{"path": "missing", "error": "unreadable"}]}}
            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                reports = auto.collect_reports(["opendesign"], runner=lambda _: partial)
                auto.write_candidate_reports(reports, output)
            self.assertEqual(prior.read_bytes(), before)

    def test_resolves_full_commit_and_builds_official_archive_url(self):
        response = Response({"sha": "A" * 40})
        self.assertEqual(
            auto.resolve_commit(
                "nexu-io/open-design", "main", get=lambda *args, **kwargs: response
            ),
            "a" * 40,
        )
        self.assertEqual(
            auto.archive_url("nexu-io/open-design", "a" * 40),
            "https://codeload.github.com/nexu-io/open-design/tar.gz/" + "a" * 40,
        )

    def test_resolves_only_weekly_locked_sources(self):
        sources = {
            "sources": [
                {"id": "opendesign", "tracking": {"cadence": "weekly"}},
                {"id": "remotion-dev.skills", "tracking": {"cadence": "manual"}},
                {"id": "discover.github", "tracking": {"cadence": "weekly"}},
            ]
        }
        self.assertEqual(auto.automated_source_ids(sources), ["opendesign"])

    def test_candidate_reports_are_deterministic_and_write_only_on_change(self):
        reports = {"opendesign": {"snapshot": {"ref": "a" * 40}, "diff": {"changes": []}}}
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            first = auto.write_candidate_reports(reports, output)
            second = auto.write_candidate_reports(reports, output)
            self.assertEqual(first, ["opendesign"])
            self.assertEqual(second, [])
            self.assertEqual(json.loads((output / "opendesign.json").read_text()), reports["opendesign"])

    def test_batch_failure_writes_no_partial_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td)
            with self.assertRaises(RuntimeError):
                auto.collect_reports(
                    ["opendesign", "remotion"],
                    runner=lambda source: (
                        {"snapshot": {"source": source}}
                        if source == "opendesign"
                        else (_ for _ in ()).throw(RuntimeError("boom"))
                    ),
                )
            self.assertEqual(list(output.glob("*.json")), [])


if __name__ == "__main__":
    unittest.main()
