"""Coverage and stability contract for the legacy discovery projection."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
SCRIPT = ROOT / "scripts" / "discovery-index.py"


class DiscoveryIndexTests(unittest.TestCase):
    def run_index(self, output, data=None, resources=None, overrides=None):
        args = [
            PYTHON, str(SCRIPT), "--data", str(data or ROOT / "data/discovery/legacy-v2.yaml"),
            "--resources", str(resources or ROOT / "data/resources.yaml"),
            "--categories", str(ROOT / "data/categories.yaml"),
            "--overrides", str(overrides or ROOT / "data/discovery/classification-overrides.yaml"),
            "--output", str(output),
        ]
        return subprocess.run(args, capture_output=True, text=True)

    def test_all_legacy_assets_and_platforms_have_deterministic_browse_outcomes(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp) / "first.json", Path(temp) / "second.json"
            result = self.run_index(first)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.run_index(second).returncode, 0)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            doc = json.loads(first.read_text())

        raw = (ROOT / "data/discovery/legacy-v2.yaml").read_bytes()
        self.assertEqual(doc["schema_version"], 1)
        self.assertEqual(doc["source_id"], "discover.awesome-agent-ecosystem")
        self.assertEqual(doc["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(doc["coverage"]["total_assets"], 777)
        self.assertEqual(doc["coverage"]["total_platforms"], 26)
        self.assertEqual(len(doc["coverage"]["outcomes"]), 777)
        self.assertEqual(len({outcome["legacy_key"] for outcome in doc["coverage"]["outcomes"]}), 777)
        self.assertEqual(len(doc["entries"]), 777)
        self.assertEqual(len(doc["platforms"]), 26)
        self.assertEqual(len({entry["id"] for entry in doc["entries"]}), 777)

    def test_unknown_provenance_and_collection_content_are_not_promoted_to_resources(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "index.json"
            result = self.run_index(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            entries = json.loads(output.read_text())["entries"]
        by_key = {key: entry for entry in entries for key in entry["legacy_keys"]}
        cookbook = by_key["prompts/OpenAI Cookbook"]
        self.assertEqual(cookbook["content_kind"], "collection")
        self.assertIsNone(cookbook["classification"]["subtype"])
        self.assertEqual(cookbook["channel_source"], "discover.awesome-agent-ecosystem")
        self.assertEqual(cookbook["legacy"]["source_label"], "official")
        self.assertTrue(cookbook["missing"])
        self.assertNotIn("authors", cookbook)
        self.assertNotIn("license", cookbook)
        self.assertNotIn("components", cookbook)
        project_template = by_key["prompts/模板：React / Next.js"]
        self.assertEqual(project_template["content_kind"], "collection")
        self.assertEqual(project_template["classification"]["subtype"], "principle")
        mcp = by_key["mcp/playwright-mcp"]
        self.assertEqual(mcp["expected_components"], ["mcp-server"])
        self.assertIn("only an expectation", mcp["missing"][-1])
        cli = by_key["cli/Codex CLI"]
        self.assertEqual(cli["expected_components"], ["cli"])
        design_cli = by_key["design-docs/@google/design.md CLI"]
        self.assertEqual(design_cli["classification"]["category"], "plugins")
        design_keys = [key for key in by_key if key.startswith("design-docs/")]
        self.assertEqual(len(design_keys), 32)
        invoice = by_key["skills/invoice-organizer"]
        self.assertNotIn("audio", invoice["classification"]["domains"])

    def test_identity_keeps_template_selectors_and_distinct_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            data = base / "legacy.yaml"
            data.write_text(yaml.safe_dump({"categories": [{"id": "plugins", "entries": [
                {"name": "Shared Template", "url": "https://example.test/templates?id=one", "source": "community", "note": "template"},
                {"name": "Shared Template", "url": "https://example.test/templates?id=two", "source": "community", "note": "template"},
                {"name": "Plugin Alpha", "url": "https://github.com/org/plugins", "source": "community", "note": "plugin"},
                {"name": "Plugin Beta", "url": "https://github.com/org/plugins", "source": "community", "note": "plugin"},
            ]}]}, sort_keys=False), encoding="utf-8")
            resources = base / "resources.yaml"
            resources.write_text("schema_version: 3\nresources: []\n", encoding="utf-8")
            output = base / "index.json"
            # Missing overrides are valid for new/temporary input; unchanged legacy rows use defaults.
            result = self.run_index(output, data=data, resources=resources, overrides=base / "not-created.yaml")
            self.assertEqual(result.returncode, 0, result.stderr)
            doc = json.loads(output.read_text())
        self.assertEqual(len(doc["entries"]), 4)
        self.assertEqual(len(doc["coverage"]["outcomes"]), 4)
        self.assertEqual({entry["source_url"].split("=")[-1] for entry in doc["entries"] if "Shared Template" == entry["title"]}, {"one", "two"})

    def test_legacy_input_bytes_are_unchanged(self):
        path = ROOT / "data/discovery/legacy-v2.yaml"
        before = path.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_index(Path(temp) / "index.json")
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
