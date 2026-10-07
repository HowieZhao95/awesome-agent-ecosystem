"""Every known source entry must have an actual public browse destination."""
import json
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from discovery_index.core import build_index


class CompleteDirectoryCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources_doc = yaml.safe_load((ROOT / "data/resources.yaml").read_text())
        cls.resources = {item["id"]: item for item in cls.resources_doc["resources"]}
        cls.index = build_index(ROOT / "data/discovery/legacy-v2.yaml", ROOT / "data/resources.yaml", ROOT / "data/discovery/classification-overrides.yaml")
        cls.references = yaml.safe_load((ROOT / "data/discovery/opendesign-references.yaml").read_text())["entries"]
        cls.od = json.loads((ROOT / "docs/evidence/complete-directory/opendesign-inventory.json").read_text())

    def test_all_777_historical_entries_have_visible_unique_targets_and_26_platforms(self):
        self.assertEqual(777, self.index["coverage"]["total_assets"])
        self.assertEqual(777, len(self.index["coverage"]["outcomes"]))
        self.assertEqual(777, len({row["legacy_key"] for row in self.index["coverage"]["outcomes"]}))
        self.assertEqual(26, len(self.index["platforms"]))
        targets = set(self.resources) | {row["id"] for row in self.index["entries"]}
        for row in self.index["coverage"]["outcomes"]:
            self.assertIn(row["target_id"], targets)
            self.assertTrue(row["reason"])
        for entry in self.index["entries"]:
            if entry.get("mapped_resource_id"):
                self.assertIn(entry["mapped_resource_id"], self.resources)
            self.assertIn(entry["classification"]["category"], {"templates", "design-systems", "skills", "prompts", "plugins"})

    def test_all_277_opendesign_entries_resolve_to_a_resource_or_source_reference(self):
        self.assertEqual(277, self.od["coverage"]["entry_total"])
        self.assertEqual(0, self.od["coverage"]["unaccounted_entries"])
        self.assertEqual({}, self.od["coverage"]["count_mismatches"])
        reference_by_key = {key: entry for entry in self.references for key in entry["legacy_keys"]}
        proposal_by_path = {row["provenance"]["upstream"]["path"]: row for row in self.od["proposals"]["resources"]}
        related = self.od["proposals"]["related_entries"]
        self.assertEqual(277, len(proposal_by_path) + len(related))
        for path, proposal in proposal_by_path.items():
            self.assertIn(proposal["id"], self.resources)
            resource = self.resources[proposal["id"]]
            self.assertEqual(path, resource["provenance"]["upstream"]["path"])
            self.assertEqual("pending", resource["review"]["status"])
            self.assertEqual([], resource["verification"]["tested_hosts"])
        for row in related:
            self.assertIn(row["input_key"], reference_by_key)
            ref = reference_by_key[row["input_key"]]
            self.assertEqual(row["source_url"], ref["source_url"])
            if ref.get("mapped_resource_id"):
                self.assertIn(ref["mapped_resource_id"], self.resources)

    def test_raw_discovery_never_fabricates_audited_source_or_installation_metadata(self):
        for entry in self.index["entries"] + self.references:
            for field in ("provenance", "authors", "publisher", "license", "components", "verification"):
                self.assertNotIn(field, entry)
            self.assertTrue(entry["missing"])


if __name__ == "__main__":
    unittest.main()
