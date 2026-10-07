"""Template and design-system profile contract regression tests."""
import sys
import unittest
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate import _profile_file_errors, validate_data
from scripts.build import build_outputs
from test_phase1_catalog import fixture_root, read_yaml


def profile_docs(resource):
    temp, root = fixture_root()
    categories = read_yaml(root, "categories")
    sources = read_yaml(root, "sources")
    resources = read_yaml(root, "resources")
    resources["resources"] = [resource]
    temp.cleanup()
    return categories, sources, resources


def template_resource():
    temp, root = fixture_root()
    resource = read_yaml(root, "resources")["resources"][0]
    temp.cleanup()
    resource["template"] = {
        "files": [
            {"role": "instructions", "path": "templates/web/SKILL.md", "url": "https://example.test/repo/blob/" + "a" * 40 + "/templates/web/SKILL.md"},
            {"role": "framework", "path": "templates/web/src", "url": "https://example.test/repo/tree/" + "a" * 40 + "/templates/web/src"},
            {"role": "example", "path": "templates/web/examples/basic", "url": "https://example.test/repo/tree/" + "a" * 40 + "/templates/web/examples/basic"},
        ],
        "style": {"policy": "external-design-system", "upstream_status": "independent", "note": "Style is supplied independently."},
    }
    return resource


class TemplateProfileTests(unittest.TestCase):
    def errors(self, resource):
        return validate_data(*profile_docs(resource))

    def test_accepts_optional_profile_free_legacy_v3_resource(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        self.assertEqual([], validate_data(read_yaml(root, "categories"), read_yaml(root, "sources"), read_yaml(root, "resources")))

    def test_accepts_template_profile_with_framework_instructions_and_example(self):
        self.assertEqual([], self.errors(template_resource()))

    def test_build_projection_preserves_template_profile(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        resources = read_yaml(root, "resources")
        resources["resources"][0]["template"] = template_resource()["template"]
        (root / "data" / "resources.yaml").write_text(yaml.safe_dump(resources, sort_keys=False), encoding="utf-8")
        build_outputs(root)
        site_data = (root / "site" / "data.js").read_text(encoding="utf-8")
        self.assertIn('"template": {', site_data)
        catalog = json.loads((root / "site" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(resources["resources"][0]["template"], catalog["resources"]["resources"][0]["template"])

    def test_rejects_template_file_role_from_design_system_profile(self):
        resource = template_resource()
        resource["template"]["files"][0]["role"] = "manifest"
        self.assertTrue(any("template.files" in error and "role" in error for error in self.errors(resource)))

    def test_rejects_design_system_profile_on_template_category(self):
        resource = template_resource()
        resource["design_system"] = {"files": [{"role": "manifest", "path": "manifest.json", "url": "https://example.test/manifest.json"}]}
        self.assertTrue(any("design_system" in error for error in self.errors(resource)))

    def test_rejects_template_reference_that_does_not_match_locked_upstream(self):
        resource = template_resource()
        resource["template"]["files"][0]["url"] = "https://elsewhere.test/repo/blob/" + "b" * 40 + "/templates/web/SKILL.md"
        self.assertTrue(any("locked ref" in error for error in self.errors(resource)))

    def test_profile_url_matches_actual_upstream_full_blob_locator(self):
        resources = read_yaml(ROOT, "resources")["resources"]
        resource = next(item for item in resources if item["id"] == "opendesign.web-prototype")
        upstream = resource["provenance"]["upstream"]
        errors = _profile_file_errors(
            resource["id"], "template",
            {"files": [{"role": "instructions", "path": upstream["path"], "url": upstream["url"]}]},
            {"instructions", "framework", "example", "support"}, upstream,
        )
        self.assertEqual([], errors)

    def test_unknown_git_ref_allows_only_exact_parent_file_locator(self):
        resource = next(item for item in read_yaml(ROOT, "resources")["resources"] if item["id"] == "voltagent.linear-design-reference")
        upstream = resource["provenance"]["upstream"]
        profile = {"files": [{"role": "rules", "path": upstream["path"], "url": upstream["url"]}]}
        self.assertEqual([], _profile_file_errors(resource["id"], "design_system", profile, {"manifest", "rules", "tokens-css", "example", "support"}, upstream))
        profile["files"][0]["url"] = upstream["url"].replace("/main/", "/" + "a" * 40 + "/")
        self.assertTrue(_profile_file_errors(resource["id"], "design_system", profile, {"manifest", "rules", "tokens-css", "example", "support"}, upstream))

    def test_rejects_style_binding_fields_in_template_profile(self):
        resource = template_resource()
        resource["template"]["design_system_id"] = "brand.theme"
        self.assertTrue(any("template: expected only files and style" in error for error in self.errors(resource)))

    def test_usable_template_requires_complete_independent_profile(self):
        resource = template_resource()
        resource["template"]["style"]["upstream_status"] = "mixed"
        resource["lifecycle"]["state"] = "usable"
        errors = self.errors(resource)
        self.assertTrue(any("usable" in error and "independent" in error for error in errors))

    def test_design_system_profile_accepts_missing_optional_references_but_not_missing_core_roles_when_usable(self):
        resource = template_resource()
        resource["classification"]["category"] = "design-systems"
        resource["classification"]["subtype"] = None
        resource.pop("template")
        resource["design_system"] = {"files": [
            {"role": "manifest", "path": "manifest.json", "url": "https://example.test/repo/blob/" + "a" * 40 + "/manifest.json"},
            {"role": "rules", "path": "DESIGN.md", "url": "https://example.test/repo/blob/" + "a" * 40 + "/DESIGN.md"},
            {"role": "tokens-css", "path": "tokens.css", "url": "https://example.test/repo/blob/" + "a" * 40 + "/tokens.css"},
        ]}
        self.assertEqual([], self.errors(resource))
        resource["design_system"]["files"] = resource["design_system"]["files"][:1]
        self.assertEqual([], self.errors(resource), "candidate design systems may document only the files currently found")
        resource["design_system"]["files"] = [
            {"role": "manifest", "path": "manifest.json", "url": "https://example.test/repo/blob/" + "a" * 40 + "/manifest.json"},
            {"role": "rules", "path": "DESIGN.md", "url": "https://example.test/repo/blob/" + "a" * 40 + "/DESIGN.md"},
            {"role": "tokens-css", "path": "tokens.css", "url": "https://example.test/repo/blob/" + "a" * 40 + "/tokens.css"},
        ]
        resource["design_system"]["files"] = resource["design_system"]["files"][1:]
        resource["lifecycle"]["state"] = "usable"
        errors = self.errors(resource)
        self.assertTrue(any("design system" in error.lower() and "manifest" in error.lower() for error in errors))
