"""Evidence guards for framework identity and independently indexed design systems."""
import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class FrameworkInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = yaml.safe_load((ROOT / "data/resources.yaml").read_text())
        cls.resources = {item["id"]: item for item in cls.catalog["resources"]}
        cls.inventory = json.loads((ROOT / "docs/evidence/template-decoupling/design-system-inventory.json").read_text())

    def test_each_audited_design_system_has_one_independent_record_with_core_files(self):
        expected_ids = {entry["resource_id"] for entry in self.inventory["entries"]}
        actual_ids = {item["id"] for item in self.resources.values()
                      if item["classification"]["category"] == "design-systems"
                      and item["provenance"]["content_source"] == "opendesign"}
        self.assertEqual(expected_ids, actual_ids)
        for entry in self.inventory["entries"]:
            resource = self.resources[entry["resource_id"]]
            by_role = {file["role"]: file for file in resource["design_system"]["files"]
                       if file["role"] in {"manifest", "rules", "tokens-css"}}
            self.assertEqual({"manifest", "rules", "tokens-css"}, set(by_role))
            prefix = "design-systems/" + entry["slug"] + "/"
            for role, name in [("manifest", "manifest.json"), ("rules", "DESIGN.md"), ("tokens-css", "tokens.css")]:
                self.assertEqual(prefix + name, by_role[role]["path"])
            self.assertEqual("pending", resource["review"]["status"])
            self.assertEqual([], resource["verification"]["tested_hosts"])
            self.assertNotIn("template", resource)

    def test_style_entrypoints_and_content_recipes_do_not_create_duplicate_frameworks(self):
        templates = [resource for resource in self.resources.values()
                     if resource["classification"]["category"] == "templates"]
        upstream_framework_paths = []
        for resource in templates:
            files = resource["template"]["files"]
            self.assertTrue({"instructions", "framework", "example", "support"} <= {item["role"] for item in files})
            self.assertEqual("external-design-system", resource["template"]["style"]["policy"])
            self.assertNotIn("design_system_id", resource["template"])
            self.assertEqual("candidate", resource["lifecycle"]["state"])
            upstream_framework_paths.extend(item["path"] for item in files if item["role"] == "framework")
        self.assertEqual(len(upstream_framework_paths), len(set(upstream_framework_paths)))
        pitch = self.resources["opendesign.html-ppt-pitch-deck"]
        self.assertEqual("skills", pitch["classification"]["category"])
        deck = self.resources["opendesign.html-ppt"]
        self.assertEqual("deck", deck["classification"]["subtype"])
        self.assertTrue(any(item["path"].endswith("templates/deck.html") for item in deck["template"]["files"]))

    def test_reclassification_preserves_legacy_resource_identity_and_review(self):
        selected = ["opendesign.motion-frames", "opendesign.docs-page", "opendesign.social-carousel", "opendesign.mockup-device-3d", "opendesign.html-ppt-pitch-deck"]
        for identity in selected:
            resource = self.resources[identity]
            self.assertEqual("skills", resource["classification"]["category"])
            self.assertIsNone(resource["classification"]["subtype"])
            self.assertEqual("pending", resource["review"]["status"])
            self.assertEqual([], resource["verification"]["tested_hosts"])
            self.assertNotIn("template", resource)


if __name__ == "__main__":
    unittest.main()
