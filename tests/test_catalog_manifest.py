import copy
import importlib.util
import json
import unittest
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('source_core', ROOT / 'scripts/source_tools/core.py')
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)
VALIDATOR_SPEC = importlib.util.spec_from_file_location('validate_catalog', ROOT / 'scripts/validate.py')
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)


class CatalogManifestTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {'source': 'opendesign', 'repository': 'nexu-io/open-design',
                         'ref': 'a' * 40, 'complete': True, 'failures': [],
                         'files': {'templates/web/SKILL.md': {'size': 10, 'sha256': 'b' * 64},
                                   'LICENSE': {'size': 20, 'sha256': 'c' * 64}}}
        self.manifest = {'schema_version': 1, 'resource_id': 'opendesign.web-prototype',
                         'source_id': 'opendesign', 'repository': 'nexu-io/open-design',
                         'source_commit': 'a' * 40, 'root': 'templates/web',
                         'title': 'Web Prototype', 'author': 'OpenDesign',
                         'license_evidence': [{'path': 'LICENSE', 'declared': 'Apache-2.0'}],
                         'files': [{'path': 'templates/web/SKILL.md', 'relative_path': 'SKILL.md',
                                    'size': 10, 'sha256': 'b' * 64},
                                   {'path': 'LICENSE', 'relative_path': 'UPSTREAM-LICENSE',
                                    'size': 20, 'sha256': 'c' * 64}], 'change': 'add'}

    def validate(self, manifest=None):
        validator = getattr(core, 'validate_catalog_manifest', None)
        self.assertTrue(callable(validator), 'catalog manifest validation must be implemented')
        return validator(manifest or self.manifest, self.snapshot)

    def test_accepts_a_complete_pinned_manifest_with_license_evidence(self):
        self.assertEqual(self.validate(), [])

    def test_rejects_tampered_digest(self):
        self.manifest['files'][0]['sha256'] = 'd' * 64
        self.assertTrue(any('digest' in error for error in self.validate()))

    def test_rejects_path_escape_and_file_outside_selected_scope(self):
        self.manifest['files'][0]['relative_path'] = '../escaped'
        self.assertTrue(any('path' in error for error in self.validate()))
        self.manifest['files'][0]['relative_path'] = 'SKILL.md'
        self.manifest['files'][0]['path'] = 'unreviewed/SKILL.md'
        self.assertTrue(any('scope' in error for error in self.validate()))

    def test_rejects_encoded_path_escape_in_a_storage_destination(self):
        self.manifest['files'][0]['relative_path'] = 'files/%2e%2e/SKILL.md'
        self.assertTrue(any('path' in error for error in self.validate()))

    def test_rejects_missing_license_notice_and_duplicate_destinations(self):
        self.manifest['files'].pop()
        self.assertTrue(any('license' in error for error in self.validate()))
        self.manifest['files'].append(copy.deepcopy(self.manifest['files'][0]))
        self.assertTrue(any('duplicate' in error for error in self.validate()))

    def test_rejects_source_commit_or_identity_mismatch(self):
        self.manifest['source_commit'] = 'e' * 40
        self.assertTrue(any('commit' in error for error in self.validate()))
        self.manifest['source_id'] = 'another-source'
        self.assertTrue(any('source' in error for error in self.validate()))

    def test_real_web_prototype_manifest_preserves_all_files_and_both_license_claims(self):
        manifest = json.loads((ROOT / 'data/catalog-manifest.json').read_text())
        snapshot = json.loads((ROOT / 'docs/evidence/source-sync/opendesign.json').read_text())['snapshot']
        self.assertEqual(manifest['resource_id'], 'opendesign.web-prototype')
        self.assertEqual(len(manifest['files']), 7)
        self.assertEqual({item['declared'] for item in manifest['license_evidence']}, {'MIT', 'Apache-2.0'})
        self.assertEqual(core.validate_catalog_manifest(manifest, snapshot), [])

    def test_refresh_keeps_resource_identity_and_updates_file_digests(self):
        refresh = getattr(core, 'refresh_catalog_manifest', None)
        self.assertTrue(callable(refresh), 'catalog manifest refresh must be implemented')
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['ref'] = 'e' * 40
        snapshot['files']['templates/web/SKILL.md']['sha256'] = 'd' * 64
        result = refresh(self.manifest, snapshot)
        self.assertEqual(result['resource_id'], self.manifest['resource_id'])
        self.assertEqual(result['source_commit'], 'e' * 40)
        self.assertEqual(result['files'][0]['relative_path'], 'SKILL.md')
        self.assertEqual(result['files'][0]['sha256'], 'd' * 64)
        self.assertEqual(result['change'], 'update')
        self.assertEqual(self.manifest['source_commit'], 'a' * 40)

    def test_repeated_refresh_does_not_change_a_manifest(self):
        refresh = getattr(core, 'refresh_catalog_manifest', None)
        self.assertTrue(callable(refresh), 'catalog manifest refresh must be implemented')
        self.assertEqual(refresh(self.manifest, self.snapshot), self.manifest)

    def test_refresh_refuses_an_incomplete_or_different_source(self):
        refresh = getattr(core, 'refresh_catalog_manifest', None)
        self.assertTrue(callable(refresh), 'catalog manifest refresh must be implemented')
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['complete'] = False
        with self.assertRaises(core.SnapshotError):
            refresh(self.manifest, snapshot)
        snapshot['complete'] = True
        snapshot['source'] = 'another'
        with self.assertRaises(core.SnapshotError):
            refresh(self.manifest, snapshot)

    def test_changed_repository_license_requires_a_new_rights_review(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['files']['LICENSE']['sha256'] = 'd' * 64
        result = core.refresh_catalog_manifest(self.manifest, snapshot)
        self.assertEqual(result['license_evidence'][0]['declared'], 'unknown')

    def test_repository_quality_gate_rejects_a_tampered_catalog_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(ROOT / 'data', root / 'data')
            shutil.copytree(ROOT / 'docs/evidence/source-sync', root / 'docs/evidence/source-sync')
            manifest_path = root / 'data/catalog-manifest.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['files'][0]['sha256'] = '0' * 64
            manifest_path.write_text(json.dumps(manifest))
            errors = validator.validate_catalog(root)
            self.assertTrue(any('digest' in error for error in errors), errors)


if __name__ == '__main__':
    unittest.main()
