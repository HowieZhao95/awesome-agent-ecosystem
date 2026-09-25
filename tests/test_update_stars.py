import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "update-stars.py"
SPEC = importlib.util.spec_from_file_location("update_stars", SCRIPT)
update_stars = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update_stars)


class FakeResponse:
    def __init__(self, status_code, payload=None, etag=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = {"ETag": etag} if etag else {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, dict(headers or {}), timeout))
        return self.responses.pop(0)


def resource_doc(stars=1):
    return {
        "meta": {"updated": "2026-01-01"},
        "categories": [
            {
                "id": "skills",
                "entries": [
                    {"name": "One", "url": "https://github.com/acme/tool", "stars": stars},
                    {"name": "Alias", "url": "https://github.com/acme/tool/tree/main/skill", "stars": stars},
                    {"name": "Elsewhere", "url": "https://example.com/x", "stars": None},
                ],
            }
        ],
    }


class UpdateStarsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.data_file = root / "resources.yaml"
        self.state_file = root / "github-repo-state.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_doc(self, doc):
        self.data_file.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    def test_unique_repo_is_requested_once_and_real_change_is_atomic(self):
        self.write_doc(resource_doc(stars=1))
        session = FakeSession([
            FakeResponse(200, {"stargazers_count": 9}, '"v2"'),
        ])

        result = update_stars.run(
            self.data_file, self.state_file, session=session, today="2026-02-03"
        )

        self.assertEqual(1, len(session.calls))
        saved = yaml.safe_load(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual([9, 9], [e["stars"] for e in saved["categories"][0]["entries"][:2]])
        self.assertEqual("2026-02-03", saved["meta"]["updated"])
        self.assertEqual('"v2"', json.loads(self.state_file.read_text())["repos"]["acme/tool"]["etag"])
        self.assertEqual(2, result.updated_entries)

    def test_304_uses_etag_and_writes_nothing(self):
        self.write_doc(resource_doc(stars=9))
        self.state_file.write_text(
            json.dumps({"version": 1, "repos": {"acme/tool": {"etag": '"v2"'}}}),
            encoding="utf-8",
        )
        yaml_before = self.data_file.read_bytes()
        state_before = self.state_file.read_bytes()
        session = FakeSession([FakeResponse(304)])

        result = update_stars.run(
            self.data_file, self.state_file, session=session, today="2026-02-04"
        )

        self.assertEqual('"v2"', session.calls[0][1]["If-None-Match"])
        self.assertEqual(yaml_before, self.data_file.read_bytes())
        self.assertEqual(state_before, self.state_file.read_bytes())
        self.assertEqual(0, result.updated_entries)

    def test_200_with_same_stars_writes_only_changed_etag_state(self):
        self.write_doc(resource_doc(stars=9))
        self.state_file.write_text(
            json.dumps({"version": 1, "repos": {"acme/tool": {"etag": '"v2"'}}}),
            encoding="utf-8",
        )
        yaml_before = self.data_file.read_bytes()
        session = FakeSession([FakeResponse(200, {"stargazers_count": 9}, '"v3"')])

        update_stars.run(
            self.data_file, self.state_file, session=session, today="2026-02-04"
        )

        self.assertEqual(yaml_before, self.data_file.read_bytes())
        saved_state = json.loads(self.state_file.read_text(encoding="utf-8"))
        self.assertEqual('"v3"', saved_state["repos"]["acme/tool"]["etag"])

    def test_fetch_records_referenced_repository_metadata(self):
        self.write_doc(resource_doc(stars=9))
        response = FakeResponse(200, {
            "stargazers_count": 9,
            "html_url": "https://github.com/acme/tool",
            "description": "Reference project",
            "pushed_at": "2026-02-01T00:00:00Z",
            "default_branch": "main",
            "archived": False,
            "topics": ["agent", "skill"],
        }, '"v2"')

        update_stars.run(self.data_file, self.state_file, session=FakeSession([response]))

        saved = json.loads(self.state_file.read_text())["repos"]["acme/tool"]
        self.assertEqual("Reference project", saved["description"])
        self.assertEqual("2026-02-01T00:00:00Z", saved["pushed_at"])
        self.assertEqual("main", saved["default_branch"])
        self.assertEqual(["agent", "skill"], saved["topics"])
        self.assertEqual(9, saved["stars"])

    def test_new_alias_without_stars_keeps_the_curated_empty_metric(self):
        doc = resource_doc(stars=9)
        doc["categories"][0]["entries"][1]["stars"] = None
        self.write_doc(doc)
        self.state_file.write_text(
            json.dumps({"version": 1, "repos": {"acme/tool": {"etag": '"v2"'}}}),
            encoding="utf-8",
        )
        session = FakeSession([FakeResponse(304)])

        update_stars.run(self.data_file, self.state_file, session=session)

        self.assertEqual('"v2"', session.calls[0][1]["If-None-Match"])
        saved = yaml.safe_load(self.data_file.read_text(encoding="utf-8"))
        self.assertIsNone(saved["categories"][0]["entries"][1]["stars"])

    def test_repo_metadata_does_not_fill_an_intentionally_empty_star_field(self):
        self.write_doc(resource_doc(stars=None))
        session = FakeSession([FakeResponse(200, {"stargazers_count": 999}, '"v2"')])
        before = self.data_file.read_bytes()

        result = update_stars.run(self.data_file, self.state_file, session=session)

        self.assertEqual(before, self.data_file.read_bytes())
        self.assertEqual(0, result.updated_entries)

    def test_any_failure_prevents_partial_yaml_or_state_write(self):
        doc = resource_doc(stars=1)
        doc["categories"][0]["entries"].append(
            {"name": "Two", "url": "https://github.com/other/repo", "stars": 2}
        )
        self.write_doc(doc)
        self.state_file.write_text(json.dumps({"version": 1, "repos": {}}), encoding="utf-8")
        yaml_before = self.data_file.read_bytes()
        state_before = self.state_file.read_bytes()
        session = FakeSession([
            FakeResponse(200, {"stargazers_count": 10}, '"a"'),
            FakeResponse(503),
        ])

        with self.assertRaises(update_stars.ScanFailed):
            update_stars.run(
                self.data_file, self.state_file, session=session, today="2026-02-04"
            )

        self.assertEqual(yaml_before, self.data_file.read_bytes())
        self.assertEqual(state_before, self.state_file.read_bytes())

    def test_missing_repository_is_reported_without_blocking_other_updates(self):
        doc = resource_doc(stars=1)
        doc["categories"][0]["entries"].append(
            {"name": "Missing", "url": "https://github.com/old/missing", "stars": 2}
        )
        self.write_doc(doc)
        session = FakeSession([
            FakeResponse(200, {"stargazers_count": 10}, '"a"'),
            FakeResponse(404),
        ])

        result = update_stars.run(self.data_file, self.state_file, session=session)

        self.assertEqual(("old/missing",), result.missing_repos)
        saved = yaml.safe_load(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(10, saved["categories"][0]["entries"][0]["stars"])
        self.assertEqual(2, saved["categories"][0]["entries"][-1]["stars"])


if __name__ == "__main__":
    unittest.main()
