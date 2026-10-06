"""Contract tests for the draft public-assets catalog pipeline."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def fixture_root():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / "data").mkdir()
    (root / "site").mkdir()
    (root / "data" / "categories.yaml").write_text(
        (ROOT / "data" / "categories.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (root / "data" / "sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 3,
        "sources": [{
            "id": "upstream", "name": "Upstream", "url": "https://example.test/repo",
            "roles": ["content-upstream"], "access": "public",
            "tracking": {"scope": "assets/", "exclude": [], "baseline": "main",
                         "cadence": "manual", "method": "manual", "promotion": "review",
                         "last_checked": "2026-10-07", "limitations": []},
        }, {
            "id": "discovery", "name": "Discovery", "url": "https://example.test/list",
            "roles": ["discovery-channel"], "access": "public",
            "tracking": {"scope": "one entry", "exclude": [], "baseline": "2026-10-07",
                         "cadence": "manual", "method": "manual", "promotion": "review",
                         "last_checked": "2026-10-07", "limitations": []},
        }, {
            "id": "distribution", "name": "Distribution", "url": "https://example.test/install",
            "roles": ["distribution-channel"], "access": "public",
            "tracking": {"scope": "one package", "exclude": [], "baseline": "0.1.0",
                         "cadence": "manual", "method": "manual", "promotion": "review",
                         "last_checked": "2026-10-07", "limitations": []},
        }],
    }, sort_keys=False), encoding="utf-8")
    resource = {
        "id": "example.prototype",
        "title": "Example prototype",
        "summary": "A reusable web prototype.",
        "purpose": "Create a web prototype.",
        "classification": {"category": "templates", "subtype": "prototype",
                           "domains": ["visual-design"], "formats": ["html"],
                           "conventions": [], "rationale": "The delivered artifact is an interface prototype."},
        "provenance": {"relation": "curated", "content_source": "upstream",
                       "discovered_via": ["discovery"],
                       "upstream": {"kind": "git", "url": "https://example.test/repo",
                                    "path": "assets/prototype/index.html", "selector": None,
                                    "ref": {"kind": "commit", "value": "a" * 40}},
                       "derives_from": [], "changes": None},
        "authors": {"status": "unknown", "identities": [], "evidence": []},
        "publisher": {"status": "unknown", "identities": [], "evidence": []},
        "license": {"status": "unknown", "expression": None, "scope": None,
                    "evidence": [], "redistribution": "unknown"},
        "distribution": [{"kind": "repository", "channel_source": "distribution",
                          "url": "https://example.test/repo"}],
        "previews": [],
        "compatibility": {"hosts": ["web"], "runtimes": [], "dependencies": [], "constraints": []},
        "components": [],
        "lifecycle": {"state": "candidate", "reason": "Needs review.", "replacement_id": None},
        "review": {"status": "pending", "by": None, "at": None, "evidence": []},
        "verification": {"level": "unverified", "checked_at": None, "by": None,
                         "evidence": [], "limits": ["No usage test."]},
    }
    (root / "data" / "resources.yaml").write_text(yaml.safe_dump({
        "schema_version": 3,
        "meta": {"catalog_version": "0.1.0-draft", "updated": "2026-10-07",
                 "review": {"status": "pending"}},
        "resources": [resource],
    }, sort_keys=False), encoding="utf-8")
    return temp, root


def read_yaml(root, name):
    path = root / "data" / f"{name}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(root, name, value):
    (root / "data" / f"{name}.yaml").write_text(
        yaml.safe_dump(value, sort_keys=False), encoding="utf-8"
    )


class Phase1CatalogTests(unittest.TestCase):
    def test_taxonomy_has_the_requested_phase_one_categories_and_subtypes(self):
        doc = yaml.safe_load((ROOT / "data" / "categories.yaml").read_text(encoding="utf-8"))
        categories = {category["id"]: category for category in doc["categories"]}
        self.assertEqual({"templates", "design-systems", "skills", "prompts", "plugins"}, set(categories))
        self.assertEqual(
            {"prototype", "deck", "three-d", "dashboard", "motion-graphics", "document", "custom"},
            {subtype["id"] for subtype in categories["templates"]["subtypes"]},
        )
        self.assertEqual(
            {"image", "video", "principle"},
            {subtype["id"] for subtype in categories["prompts"]["subtypes"]},
        )

    def test_validator_accepts_a_complete_pending_candidate(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS: schema_version=3", result.stdout)

    def test_source_url_may_be_unknown_only_with_explicit_access_limitation(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        sources = read_yaml(root, "sources")
        source = sources["sources"][2]
        source["url"] = None
        source["access"] = "unknown"
        source["tracking"]["limitations"] = ["The public distribution endpoint was not confirmed."]
        write_yaml(root, "sources", sources)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_source_with_known_access_requires_http_url(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        sources = read_yaml(root, "sources")
        sources["sources"][2]["url"] = None
        write_yaml(root, "sources", sources)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("url", result.stdout + result.stderr)

    def test_validator_rejects_unknown_subtype(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["classification"]["subtype"] = "unlisted"
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("subtype", result.stdout + result.stderr)

    def test_validator_blocks_usable_with_unknown_license_and_no_approval(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["lifecycle"]["state"] = "usable"
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("usable", result.stdout + result.stderr)

    def test_validator_rejects_wrong_source_role_and_unlocked_git_reference(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        item = doc["resources"][0]
        item["provenance"]["content_source"] = "discovery"
        item["provenance"]["upstream"]["path"] = None
        item["provenance"]["upstream"]["ref"] = {"kind": "branch", "value": "main"}
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        output = result.stdout + result.stderr
        self.assertIn("content-upstream", output)
        self.assertIn("path", output)
        self.assertIn("git source needs a repository-relative path", output)

    def test_branch_reference_is_allowed_for_a_candidate_but_does_not_claim_a_release(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["provenance"]["upstream"]["ref"] = {"kind": "branch", "value": "main"}
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validator_rejects_duplicate_identity_and_known_author_without_evidence(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        duplicate = dict(doc["resources"][0])
        duplicate["title"] = "A different title for the same ID"
        duplicate["authors"] = {"status": "known", "identities": [], "evidence": []}
        doc["resources"].append(duplicate)
        doc["resources"][0]["authors"] = {"status": "known", "identities": [], "evidence": []}
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        output = result.stdout + result.stderr
        self.assertIn("duplicate id", output)
        self.assertIn("authors", output)

    def test_validator_rejects_duplicate_upstream_distribution_unit_even_with_distinct_ids(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        duplicate = yaml.safe_load(yaml.safe_dump(doc["resources"][0]))
        duplicate["id"] = "example.other-title"
        duplicate["title"] = "A separate title"
        doc["resources"].append(duplicate)
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("duplicate distribution unit", result.stdout + result.stderr)

    def test_validator_requires_adaptation_lineage_and_change_description(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["provenance"]["relation"] = "adapted"
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("derives_from and changes", result.stdout + result.stderr)

    def test_validator_enforces_plugin_component_identity_type_and_delivery(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        item = doc["resources"][0]
        item["classification"]["category"] = "plugins"
        item["classification"]["subtype"] = None
        item["components"] = [{
            "id": "component-one", "type": "unknown", "resource_id": "missing-resource",
            "upstream": {"url": "https://example.test/component", "ref": {"kind": "branch", "value": "main"}},
            "subtype": None,
        }]
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        output = result.stdout + result.stderr
        self.assertIn("component type", output)
        self.assertIn("resource_id", output)
        self.assertIn("delivery", output)

    def test_validator_requires_stable_ascii_component_ids(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        item = doc["resources"][0]
        item["classification"]["category"] = "plugins"
        item["classification"]["subtype"] = None
        item["components"] = [{
            "id": "invalid component id", "type": "skill", "resource_id": None,
            "upstream": {"kind": "product", "url": "https://example.test/component",
                         "path": "skills/example/SKILL.md", "selector": "example",
                         "ref": {"kind": "unknown", "value": None}},
            "subtype": None, "delivery": "contained",
        }]
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("invalid component id", result.stdout + result.stderr)

    def test_validator_rejects_source_role_confusion_and_components_on_non_plugin(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["components"] = [{"id": "c", "type": "skill"}]
        sources = read_yaml(root, "sources")
        sources["sources"][1]["roles"] = ["specification"]
        write_yaml(root, "resources", doc)
        write_yaml(root, "sources", sources)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        output = result.stdout + result.stderr
        self.assertIn("discovery-channel", output)
        self.assertIn("only plugins", output)

    def test_validator_distinguishes_discovery_and_distribution_source_roles(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["provenance"]["discovered_via"] = ["distribution"]
        doc["resources"][0]["distribution"][0]["channel_source"] = "discovery"
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        output = result.stdout + result.stderr
        self.assertIn("discovery-channel", output)
        self.assertIn("distribution-channel", output)

    def test_validator_makes_general_domain_exclusive(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["classification"]["domains"] = ["general", "visual-design"]
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("general is exclusive", result.stdout + result.stderr)

    def test_candidate_can_keep_unknown_upstream_reference_without_claiming_a_version(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        doc["resources"][0]["provenance"]["upstream"]["ref"] = {"kind": "unknown", "value": None}
        write_yaml(root, "resources", doc)
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "validate.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_build_emits_compatibility_data_and_complete_draft_export(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        (root / "scripts").mkdir()
        # Relocate the script so its ROOT points only at the temporary fixture.
        (root / "scripts" / "build.py").write_text(
            (ROOT / "scripts" / "build.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "scripts" / "validate.py").write_text(
            (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [PYTHON, str(root / "scripts" / "build.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        catalog = json.loads((root / "site" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(3, catalog["schema_version"])
        self.assertEqual("example.prototype", catalog["resources"]["resources"][0]["id"])
        site_data = (root / "site" / "data.js").read_text(encoding="utf-8")
        self.assertIn('"id": "templates"', site_data)
        self.assertIn('"relation": "curated"', site_data)
        self.assertIn('"state": "candidate"', site_data)
        self.assertNotIn("人工验证", site_data)
        readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn("0.1.0-draft", readme)
        self.assertIn("candidate", readme)
        targets = re.findall(r"\[[^\]]+\]\(#([^)]+)\)", readme)
        anchors = set(re.findall(r'<a id="([^"]+)"></a>', readme))
        self.assertEqual(set(targets), set(categories["id"] for categories in read_yaml(root, "categories")["categories"]))
        self.assertTrue(set(targets) <= anchors, f"missing generated anchors: {set(targets) - anchors}")

    def test_build_lists_mixed_plugin_components_without_copying_component_content(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        doc = read_yaml(root, "resources")
        plugin = doc["resources"][0]
        plugin["id"] = "example.mixed-plugin"
        plugin["title"] = "Mixed plugin"
        plugin["classification"]["category"] = "plugins"
        plugin["classification"]["subtype"] = None
        plugin["components"] = [
            {"id": "guide-skill", "type": "skill", "resource_id": None,
             "upstream": {"kind": "product", "url": "https://example.test/plugin",
                          "path": "skills/guide/SKILL.md", "selector": "guide-skill",
                          "ref": {"kind": "unknown", "value": None}},
             "subtype": None, "delivery": "contained", "content": "COMPONENT_BODY_MUST_NOT_BE_COPIED"},
            {"id": "remote-tools", "type": "mcp-server", "resource_id": None,
             "upstream": {"kind": "product", "url": "https://example.test/plugin",
                          "path": "plugin.json", "selector": "mcp-server", "ref": {"kind": "unknown", "value": None}},
             "subtype": None, "delivery": "referenced"},
            {"id": "cli-entry", "type": "cli", "resource_id": None,
             "upstream": {"kind": "product", "url": "https://example.test/plugin",
                          "path": "plugin.json", "selector": "cli", "ref": {"kind": "unknown", "value": None}},
             "subtype": None, "delivery": "host-provided"},
        ]
        write_yaml(root, "resources", doc)
        (root / "scripts").mkdir()
        for filename in ("build.py", "validate.py"):
            (root / "scripts" / filename).write_text(
                (ROOT / "scripts" / filename).read_text(encoding="utf-8"), encoding="utf-8"
            )
        result = subprocess.run(
            [PYTHON, str(root / "scripts" / "build.py"), "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        readme = (root / "README.md").read_text(encoding="utf-8")
        for value in ("Mixed plugin", "guide-skill", "mcp-server", "remote-tools", "cli", "cli-entry",
                      "contained", "referenced", "host-provided"):
            self.assertIn(value, readme)
        self.assertNotIn("COMPONENT_BODY_MUST_NOT_BE_COPIED", readme)

    def test_build_is_deterministic_and_validation_failure_preserves_outputs(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        (root / "scripts").mkdir()
        script = root / "scripts" / "build.py"
        script.write_text((ROOT / "scripts" / "build.py").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "scripts" / "validate.py").write_text(
            (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8"), encoding="utf-8"
        )
        command = [PYTHON, str(script), "--root", str(root)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        outputs = [root / "README.md", root / "site" / "data.js", root / "site" / "catalog.json"]
        snapshot = [path.read_bytes() for path in outputs]
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        self.assertEqual(snapshot, [path.read_bytes() for path in outputs])
        doc = read_yaml(root, "resources")
        doc["resources"][0]["classification"]["subtype"] = "invalid"
        write_yaml(root, "resources", doc)
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(0, failed.returncode)
        self.assertEqual(snapshot, [path.read_bytes() for path in outputs])

    def test_legacy_ingestion_scripts_default_to_discovery_queue(self):
        import importlib.util

        expected = Path("data/discovery/legacy-v2.yaml")
        for name, variable in (("import-marketplace", "DATA_FILE"), ("import-skills-mcp", "DATA_FILE")):
            spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertEqual(expected, Path(getattr(module, variable)).relative_to(ROOT))
        spec = importlib.util.spec_from_file_location("update_stars", ROOT / "scripts" / "update-stars.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(expected, module.DATA.relative_to(ROOT))
        spec = importlib.util.spec_from_file_location("validate_discovery", ROOT / "scripts" / "validate-discovery.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(expected, Path(module.DATA).relative_to(ROOT))

    def test_link_checker_can_target_a_discovery_fixture(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        target = root / "data" / "legacy.yaml"
        target.write_text(yaml.safe_dump({
            "categories": [{"id": "legacy", "entries": [{"name": "Probe", "url": "invalid://offline"}]}]
        }), encoding="utf-8")
        result = subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "link-check.py"), "--data", str(target)],
            capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Probe", result.stdout)


if __name__ == "__main__":
    unittest.main()
