"""Build integration: discoverable entries are public without weakening resource records."""
import json
from pathlib import Path
import unittest
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build import build_outputs
from test_phase1_catalog import fixture_root


class DiscoveryBuildTests(unittest.TestCase):
    def test_build_includes_discovery_index_and_keeps_strict_resource_source_unchanged(self):
        temp, root = fixture_root()
        self.addCleanup(temp.cleanup)
        discovery_path = root / "data/discovery/legacy-v2.yaml"
        discovery_path.parent.mkdir()
        discovery_path.write_text(yaml.safe_dump({"categories": [
            {"id": "mcp", "entries": [{"name": "demo-mcp", "url": "https://github.com/example/demo-mcp", "note": "MCP discovery link", "source": "community", "platform": "GitHub"}]},
            {"id": "prompts", "entries": [{"name": "Prompt tutorial", "url": "https://example.org/tutorial", "note": "提示工程教程", "source": "community", "platform": "website"}]},
            {"id": "platforms", "entries": [{"name": "Example directory", "url": "https://example.org", "note": "Discovery platform"}]},
        ]}, allow_unicode=True), encoding="utf-8")
        source_before = (root / "data/resources.yaml").read_bytes()
        build_outputs(root)
        exported = json.loads((root / "site/catalog.json").read_text())
        self.assertIn("discovery", exported)
        self.assertEqual(2, len(exported["discovery"]["entries"]))
        self.assertEqual(1, len(exported["discovery"]["platforms"]))
        self.assertEqual(1, len(exported["resources"]["resources"]))
        self.assertEqual(source_before, (root / "data/resources.yaml").read_bytes())
        self.assertIn('"discovery":', (root / "site/data.js").read_text())
        self.assertIn("Discovery", (root / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
