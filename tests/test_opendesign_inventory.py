"""Contract tests for the read-only OpenDesign intake inventory."""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "opendesign-inventory.py"
spec = importlib.util.spec_from_file_location("opendesign_inventory", MODULE_PATH)
assert spec and spec.loader
inventory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_module)


class OpenDesignInventoryTests(unittest.TestCase):
    def make_archive(self, files: dict[str, str], root: str | None = None) -> Path:
        archive_root = root or f"open-design-{inventory_module.UPSTREAM_COMMIT}"
        temp = tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False)
        temp.close()
        with tarfile.open(temp.name, "w:gz") as archive:
            for name, content in files.items():
                relative = name.split("/", 1)[1] if name.startswith("snapshot/") else name
                archive_name = f"{archive_root}/{relative}"
                payload = content.encode("utf-8")
                info = tarfile.TarInfo(archive_name)
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        return Path(temp.name)

    def test_every_entry_has_content_grounded_classification_and_body_hash(self):
        archive = self.make_archive({
            "snapshot/design-templates/blueprint/SKILL.md": "---\nname: blueprint\n---\nBuild a dashboard with filters and charts. Reuse assets/template.html and references/layouts.md.\n",
            "snapshot/design-templates/blueprint/assets/template.html": "<main><select aria-label='Filter'></select><canvas></canvas></main>",
            "snapshot/design-templates/blueprint/references/layouts.md": "Dashboard layout with filter rail and chart grid.",
            "snapshot/design-templates/blueprint/example.html": "<main>Example dashboard</main>",
        })

        result = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 1, "skills": 0})
        entry = result["inputs"]["design-templates"]["entries"][0]

        self.assertIn("design-templates/blueprint/SKILL.md", entry["classification"]["evidence_paths"])
        self.assertEqual(64, len(entry["body_sha256"]))
        self.assertIn("dashboard", entry["classification"]["rationale"].lower())
        self.assertEqual("dashboard", entry["classification"]["subtype"])
        self.assertEqual("pending", entry["review"]["status"])
        self.assertEqual([], entry["verification"]["tested_hosts"])

    def test_style_variant_points_to_shared_framework_without_creating_template(self):
        archive = self.make_archive({
            "snapshot/design-templates/html-ppt/SKILL.md": "Build a deck from templates/deck.html and references/layouts.md.",
            "snapshot/design-templates/html-ppt/templates/deck.html": "<section class='slide'></section>",
            "snapshot/design-templates/html-ppt/references/layouts.md": "Slide sequence and presenter navigation.",
            "snapshot/design-templates/html-ppt-taste-editorial/SKILL.md": "Create editorial minimalist slides with serif headings and warm cream backgrounds.",
            "snapshot/design-templates/html-ppt-taste-editorial/example.html": "<section class='slide'>Editorial</section>",
        })

        result = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 2, "skills": 0})
        entries = {entry["slug"]: entry for entry in result["inputs"]["design-templates"]["entries"]}
        variant = entries["html-ppt-taste-editorial"]

        self.assertEqual("shared_framework_reference", variant["disposition"])
        self.assertEqual("opendesign.html-ppt", variant["target"]["resource_id"])
        self.assertEqual([], [proposal for proposal in result["proposals"]["resources"] if proposal["id"].endswith("html-ppt-taste-editorial")])
        self.assertIn("style", variant["classification"]["rationale"].lower())

    def test_missing_framework_and_thin_metadata_remain_browsable_references(self):
        archive = self.make_archive({
            "snapshot/design-templates/motion-frames/SKILL.md": "Create a single looping CSS animation composition.",
            "snapshot/design-templates/motion-frames/example.html": "<div class='pulse'></div>",
            "snapshot/skills/metadata-only/SKILL.md": "---\nname: metadata-only\ndescription: Catalog entry only.\n---\n",
        })

        result = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 1, "skills": 1})
        templates = result["inputs"]["design-templates"]["entries"]
        skills = result["inputs"]["skills"]["entries"]

        self.assertEqual("reference", templates[0]["disposition"])
        self.assertIn("framework", " ".join(templates[0]["missing"]).lower())
        self.assertEqual("reference", skills[0]["disposition"])
        self.assertTrue(any("thin" in reason.lower() for reason in skills[0]["missing"]))

    def test_explicit_manifest_claims_are_asset_scoped_and_unknowns_stay_unknown(self):
        archive = self.make_archive({
            "snapshot/skills/declared/open-design.json": json.dumps({"name": "declared", "author": {"name": "Example Author"}, "license": "MIT"}),
            "snapshot/skills/declared/SKILL.md": "A detailed workflow with input checks, output steps, and a validation procedure." * 3,
            "snapshot/skills/undeclared/SKILL.md": "A detailed workflow with input checks, output steps, and a validation procedure." * 3,
        })

        result = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 0, "skills": 2})
        entries = {entry["slug"]: entry for entry in result["inputs"]["skills"]["entries"]}

        self.assertEqual({"name": "Example Author", "evidence_path": "skills/declared/open-design.json"}, entries["declared"]["rights"]["author"])
        self.assertEqual("MIT", entries["declared"]["rights"]["license"])
        self.assertIsNone(entries["undeclared"]["rights"]["author"])
        self.assertIsNone(entries["undeclared"]["rights"]["license"])

    def test_resource_proposals_match_resource_profile_without_auto_approval(self):
        archive = self.make_archive({
            "snapshot/design-templates/sample/SKILL.md": "Build a reusable application interface from a task brief, with layout steps and an explicit review checklist.",
            "snapshot/design-templates/sample/assets/template.html": "<main><nav></nav><button>Continue</button></main>",
            "snapshot/design-templates/sample/example.html": "<main>Sample</main>",
            "snapshot/design-templates/sample/references/checklist.md": "Check navigation, layout, and responsive behavior.",
        })

        report = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 1, "skills": 0})
        proposal = report["proposals"]["resources"][0]

        self.assertEqual("candidate", proposal["lifecycle"]["state"])
        self.assertEqual("pending", proposal["review"]["status"])
        self.assertEqual([], proposal["verification"]["tested_hosts"])
        self.assertIn("limits", proposal["verification"])
        self.assertEqual({"instructions", "framework", "example", "support"}, {item["role"] for item in proposal["template"]["files"]})
        self.assertNotIn("intake", proposal)

    def test_existing_ids_are_checked_by_exact_path_or_body_hash_and_hash_mismatches_are_visible(self):
        shared_body = "A detailed skill workflow with input checks, concrete output steps, and validation criteria. " * 3
        archive = self.make_archive({
            "snapshot/plugins/_official/examples/sample/SKILL.md": shared_body,
            "snapshot/design-templates/sample/SKILL.md": "A different detailed skill workflow with input checks, concrete output steps, and validation criteria. " * 3,
            "snapshot/skills/sample/SKILL.md": shared_body,
        })
        resource_data = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", encoding="utf-8", delete=False)
        resource_data.write("resources:\n- id: opendesign.sample\n  provenance:\n    upstream:\n      kind: git\n      path: plugins/_official/examples/sample/SKILL.md\n  authors:\n    status: unknown\n")
        resource_data.close()
        self.addCleanup(Path(resource_data.name).unlink, missing_ok=True)

        report = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 1, "skills": 1}, resource_data=resource_data.name)
        entries = {entry["input"]: entry for section in report["inputs"].values() for entry in section["entries"]}

        self.assertEqual("identical-skill-sha256", entries["skills"]["matched_existing"]["basis"])
        self.assertTrue(entries["skills"]["matched_existing"]["body_sha256_equal"])
        self.assertEqual("stable-resource-id-same-source-folder", entries["design-templates"]["matched_existing"]["basis"])
        self.assertFalse(entries["design-templates"]["matched_existing"]["body_sha256_equal"])

    def test_repeated_runs_are_deterministic_and_source_urls_are_pinned(self):
        archive = self.make_archive({
            "snapshot/skills/example/SKILL.md": "A detailed multi-step task workflow with a clear output and validation step." * 3,
        })
        kwargs = {"expected_entry_counts": {"design-templates": 0, "skills": 1}}
        first = inventory_module.inventory_archive(archive, **kwargs)
        second = inventory_module.inventory_archive(archive, **kwargs)
        entry = first["inputs"]["skills"]["entries"][0]

        self.assertEqual(first, second)
        self.assertIn("/blob/", entry["source_url"])
        self.assertIn(inventory_module.UPSTREAM_COMMIT, entry["source_url"])
        self.assertEqual(first["coverage"], second["coverage"])

    def test_every_nonresource_entry_has_a_linked_reference_target(self):
        archive = self.make_archive({
            "snapshot/design-templates/recipe/SKILL.md": "A detailed business workflow that calls the shared html-ppt master framework and describes a distinct task recipe.",
            "snapshot/design-templates/recipe/example.html": "<section class='slide'>Example</section>",
            "snapshot/design-templates/style/SKILL.md": "Editorial style guidance with serif headings and a warm cream palette.",
            "snapshot/design-templates/style/example.html": "<h1>Example</h1>",
        })

        result = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 2, "skills": 0})
        entries = [entry for section in result["inputs"].values() for entry in section["entries"]]
        linked = {entry["entry_id"]: entry for entry in result["proposals"]["related_entries"]}

        for entry in entries:
            self.assertTrue(entry["source_url"])
            self.assertTrue(entry["target"]["reason"])
            if entry["disposition"] in {"reference", "shared_framework_reference", "existing_resource"}:
                self.assertIn(entry["id"], linked)
                self.assertEqual(entry["source_url"], linked[entry["id"]]["source_url"])
                self.assertEqual(entry["body_sha256"], linked[entry["id"]]["body_sha256"])

    def test_editorial_variant_requires_matching_real_scene_and_navigation_code(self):
        scenes = "".join(f"<section class='scene s{n}'></section>" for n in range(1, 4))
        html = f"<main>{scenes}<button class='pager'></button><script>window.addEventListener('keydown', () => {{}})</script></main>"
        archive = self.make_archive({
            "snapshot/skills/after-hours-editorial-template/SKILL.md": "A dark editorial HyperFrames style for cinematic storyboards with serif typography and palette guidance.",
            "snapshot/skills/after-hours-editorial-template/assets/template.html": html,
            "snapshot/skills/after-hours-editorial-template/example.html": "<main>Editorial sample</main>",
            "snapshot/skills/8-bit-orbit-video-template/SKILL.md": "Build a three-scene HyperFrames video template.",
            "snapshot/skills/8-bit-orbit-video-template/assets/template.html": html,
            "snapshot/skills/8-bit-orbit-video-template/example.html": "<main>Orbit sample</main>",
        })

        report = inventory_module.inventory_archive(archive, expected_entry_counts={"design-templates": 0, "skills": 2})
        alias = next(entry for entry in report["inputs"]["skills"]["entries"] if entry["slug"] == "after-hours-editorial-template")

        self.assertEqual("shared_framework_reference", alias["disposition"])
        self.assertEqual("opendesign.8-bit-orbit-video-template", alias["target"]["resource_id"])
        self.assertFalse(any(item["id"] == "opendesign.after-hours-editorial-template" for item in report["proposals"]["resources"]))

    def test_wrong_snapshot_root_fails_before_replacing_existing_reports(self):
        archive = self.make_archive({"snapshot/skills/example/SKILL.md": "A detailed multi-step task workflow." * 10}, root="open-design-wrong-revision")
        output_json = tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False)
        output_json.write(b"existing inventory report\n")
        output_json.close()
        output_coverage = tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False)
        output_coverage.write(b"existing coverage report\n")
        output_coverage.close()
        self.addCleanup(Path(output_json.name).unlink, missing_ok=True)
        self.addCleanup(Path(output_coverage.name).unlink, missing_ok=True)
        original_json = Path(output_json.name).read_bytes()
        original_coverage = Path(output_coverage.name).read_bytes()

        result = subprocess.run([
            sys.executable, str(MODULE_PATH), "--archive", str(archive),
            "--json", output_json.name, "--coverage", output_coverage.name,
        ], cwd=ROOT, capture_output=True, text=True, check=False)

        self.assertNotEqual(0, result.returncode)
        self.assertIn(f"open-design-{inventory_module.UPSTREAM_COMMIT}", result.stderr)
        self.assertIn("archive root", result.stderr.lower())
        self.assertEqual(original_json, Path(output_json.name).read_bytes())
        self.assertEqual(original_coverage, Path(output_coverage.name).read_bytes())


if __name__ == "__main__":
    unittest.main()
