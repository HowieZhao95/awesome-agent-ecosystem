"""Regression tests for idempotent catalog imports."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog():
    return {
        "meta": {"updated": "2026-09-01"},
        "categories": [
            {"id": category, "entries": entries}
            for category, entries in (
                ("plugins", [{"name": "old-name", "url": "https://github.com/example/tool"}]),
                ("skills", [{"name": "old-skill", "url": "https://github.com/example/skill"}]),
                ("mcp", []),
            )
        ],
    }


class ImportIdentityTests(unittest.TestCase):
    def test_marketplace_does_not_duplicate_a_renamed_resource_url(self):
        script = load_script("import-marketplace")
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / "resources.yaml"
            data.write_text(yaml.safe_dump(catalog()), encoding="utf-8")
            before = data.read_bytes()
            official = {"plugins": [{"name": "new-name", "homepage": "https://github.com/example/tool", "description": "A tool"}]}
            with patch.object(script, "DATA_FILE", str(data)), patch.object(script, "fetch", side_effect=[official, {"plugins": []}] * script.CPD_PAGES):
                script.main()
            self.assertEqual(before, data.read_bytes())

    def test_skills_import_does_not_duplicate_a_renamed_resource_url(self):
        script = load_script("import-skills-mcp")
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / "resources.yaml"
            data.write_text(yaml.safe_dump(catalog()), encoding="utf-8")
            before = data.read_bytes()
            skill = {"items": [{"name": "new-skill", "full_name": "example/skill", "html_url": "https://github.com/example/skill", "stargazers_count": 1000}]}
            with patch.object(script, "DATA_FILE", str(data)), patch.object(script, "fetch", side_effect=[skill, {"servers": []}, {"items": []}]):
                script.main()
            self.assertEqual(before, data.read_bytes())

    def test_marketplace_keeps_official_results_when_optional_directory_is_rate_limited(self):
        script = load_script("import-marketplace")
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / "resources.yaml"
            data.write_text(yaml.safe_dump(catalog()), encoding="utf-8")
            official = {"plugins": [{"name": "unique", "homepage": "https://github.com/example/unique", "description": "A tool"}]}
            limited = URLError("rate limited")
            with patch.object(script, "DATA_FILE", str(data)), patch.object(script, "fetch", side_effect=[official, limited]):
                script.main()
            doc = yaml.safe_load(data.read_text(encoding="utf-8"))
            self.assertIn("unique", [e["name"] for e in doc["categories"][0]["entries"]])

    def test_skills_search_reads_a_second_page(self):
        script = load_script("import-skills-mcp")
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / "resources.yaml"
            data.write_text(yaml.safe_dump(catalog()), encoding="utf-8")
            first_page = {"items": [
                {"name": f"skill-{i}", "full_name": f"example/skill-{i}",
                 "html_url": f"https://github.com/example/skill-{i}", "stargazers_count": 1000}
                for i in range(100)
            ]}
            second_page = {"items": [{"name": "page-two", "full_name": "example/page-two",
                                      "html_url": "https://github.com/example/page-two", "stargazers_count": 1000}]}
            with patch.object(script, "DATA_FILE", str(data)), patch.object(script, "fetch", side_effect=[first_page, second_page, {"servers": []}, {"items": []}]) as fetch:
                script.main()
            doc = yaml.safe_load(data.read_text(encoding="utf-8"))
            names = {e["name"] for e in doc["categories"][1]["entries"]}
            self.assertIn("page-two", names)
            self.assertIn("page=2", fetch.call_args_list[1].args[0])

    def test_mcp_github_search_continues_when_optional_registry_is_limited(self):
        script = load_script("import-skills-mcp")
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder) / "resources.yaml"
            data.write_text(yaml.safe_dump(catalog()), encoding="utf-8")
            limited = URLError("rate limited")
            mcp = {"items": [{"name": "new-mcp", "full_name": "example/new-mcp",
                              "html_url": "https://github.com/example/new-mcp", "stargazers_count": 1000}]}
            with patch.object(script, "DATA_FILE", str(data)), patch.object(script, "fetch", side_effect=[{"items": []}, limited, mcp]):
                script.main()
            doc = yaml.safe_load(data.read_text(encoding="utf-8"))
            self.assertIn("new-mcp", [e["name"] for e in doc["categories"][2]["entries"]])


if __name__ == "__main__":
    unittest.main()
