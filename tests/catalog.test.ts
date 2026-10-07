import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { filterBrowseResources, filterResources, getBrowseResource, getBrowseResources, getResource, getResourcePageUrl, getRelatedComponents, isAvailableForHost, loadCatalog, paginateResources } from '../src/catalog.ts';

const catalog = JSON.parse(await readFile(new URL('../site/catalog.json', import.meta.url), 'utf8'));
const discovery = JSON.parse(await readFile(new URL('../docs/evidence/complete-directory/legacy-index.json', import.meta.url), 'utf8'));

test('filters real catalog by category, subtype, domain, status, and search together', () => {
  const result = filterResources(catalog, { category: 'templates', subtype: 'prototype', domain: 'visual-design', lifecycle: 'candidate', query: 'web prototype' });
  assert.deepEqual(result.map((item) => item.id), ['opendesign.web-prototype']);
});

test('uses stable resource identity for lookup and detail URLs', () => {
  const item = getResource(catalog, 'opendesign.web-prototype');
  assert.equal(item?.id, 'opendesign.web-prototype');
  assert.equal(getResourcePageUrl(item!.id), '#/resource/opendesign.web-prototype');
  assert.equal(getResource(catalog, 'missing'), undefined);
});

test('gates host availability from the generated catalog projection', () => {
  const projected = { ...catalog, availability: { 'opendesign.web-prototype': ['opendesign'] } };
  assert.equal(isAvailableForHost(projected, 'opendesign.web-prototype', 'opendesign'), true);
  assert.equal(isAvailableForHost(projected, 'opendesign.web-prototype', 'thusdesign-web'), false);
  assert.equal(isAvailableForHost(catalog, 'opendesign.web-prototype', 'opendesign'), false);
});

test('paginates with clamped page bounds and retains total count', () => {
  const result = paginateResources(catalog.resources.resources, { page: 999, pageSize: 7 });
  const total = catalog.resources.resources.length;
  assert.equal(result.page, Math.ceil(total / 7));
  assert.equal(result.total, total);
  assert.deepEqual(result.items, catalog.resources.resources.slice((result.page - 1) * 7));
});

test('resolves only components linked by resource identity', () => {
  const linkedCatalog = structuredClone(catalog);
  const parent = getResource(linkedCatalog, 'thusdesign.td-drama-production')!;
  parent.components[0].resource_id = 'opendesign.web-prototype';
  const related = getRelatedComponents(linkedCatalog, parent);
  assert.ok(related.length > 0);
  assert.equal(related[0].resource?.id, 'opendesign.web-prototype');
});

test('rejects failed loads and schema version mismatch', async () => {
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => new Response('offline', { status: 503 }) }), /503/);
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => Response.json({ schema_version: 3 }) }), /invalid shape/);
  await assert.rejects(loadCatalog('/catalog.json', { expectedSchemaVersion: 99, fetchImpl: async () => Response.json(catalog) }), /schema version/);
  await assert.rejects(loadCatalog('/catalog.json', { expectedCatalogVersion: 'wrong', fetchImpl: async () => Response.json(catalog) }), /catalog version/);
});

test('loads the canonical generated catalog when the pinned catalog version matches', async () => {
  const loaded = await loadCatalog('/catalog.json', { expectedCatalogVersion: catalog.resources.meta.catalog_version, fetchImpl: async () => Response.json(catalog) });
  assert.deepEqual(loaded, catalog);
});

test('rejects malformed discovery metadata instead of failing while rendering the browse view', async () => {
  const invalid = structuredClone(catalog);
  invalid.discovery = { schema_version: 2, entries: 'not-an-array' };
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => Response.json(invalid) }), /invalid shape/);
});

test('loads the complete historical discovery payload with all 777 asset outcomes and 26 platform records', async () => {
  const payload = { ...structuredClone(catalog), discovery };
  const loaded = await loadCatalog('/catalog.json', { fetchImpl: async () => Response.json(payload) });
  assert.equal(loaded.discovery?.coverage.total_assets, 777);
  assert.equal(loaded.discovery?.coverage.outcomes.length, 777);
  assert.equal(loaded.discovery?.platforms.length, 26);
});

test('rejects malformed optional discovery add-ons and missing discovery arrays', async () => {
  const invalidAddon = structuredClone(catalog);
  invalidAddon.discovery.additional_sources = { source_id: 'opendesign', ref: {}, entries: 82 };
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => Response.json(invalidAddon) }), /invalid shape/);

  const missingPlatforms = structuredClone(catalog);
  delete missingPlatforms.discovery.platforms;
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => Response.json(missingPlatforms) }), /invalid shape/);

  const malformedOutcomes = structuredClone(catalog);
  malformedOutcomes.discovery.coverage.outcomes = [null];
  await assert.rejects(loadCatalog('/catalog.json', { fetchImpl: async () => Response.json(malformedOutcomes) }), /invalid shape/);
});

test('keeps strict canonical filtering separate from a merged discovery browse projection', () => {
  const expanded = structuredClone(catalog);
  expanded.discovery = {
    schema_version: 1,
    source_id: 'discover.awesome-agent-ecosystem',
    input_sha256: 'a'.repeat(64),
    entries: [{
      id: 'legacy.prompt-collection', title: 'Prompt collection', summary: 'A collection of prompts.',
      classification: { category: 'prompts', subtype: null, domains: [], formats: [], conventions: [], rationale: 'Historical record describes a collection.' },
      source_url: null, channel_source: 'discover.awesome-agent-ecosystem', legacy_keys: ['old:prompts:1'],
      legacy: { category: 'prompts', subcat: 'library', platform: 'GitHub', source_label: 'Awesome list', stars: 4, installs: null, last_verified: null, vmethod: null },
      content_kind: 'collection', expected_components: [], missing: ['original content URL not identified'],
    }], platforms: [], coverage: { total_assets: 1, total_platforms: 0, outcomes: [{ legacy_key: 'old:prompts:1', target_id: 'legacy.prompt-collection', disposition: 'discovery', reason: 'retained as discovery' }] },
  };
  const browse = getBrowseResources(expanded);
  assert.equal(browse.length, catalog.resources.resources.length + 1);
  assert.equal(filterResources(expanded, { query: 'Prompt collection' }).length, 0, 'canonical API stays strict');
  assert.equal(filterBrowseResources(expanded, { query: 'Prompt collection' })[0]?.directory_origin, 'discovery');
  assert.equal(filterBrowseResources(expanded, { origin: 'discovery', channel: 'discover.awesome-agent-ecosystem' }).length, 1);
  assert.equal(getBrowseResource(expanded, 'legacy.prompt-collection')?.provenance.upstream, null);
  assert.equal(getBrowseResource(expanded, 'legacy.prompt-collection')?.components.length, 0);
});

test('does not duplicate a discovery entry already mapped to a canonical resource', () => {
  const expanded = structuredClone(catalog);
  expanded.discovery = {
    schema_version: 1, source_id: 'discover.awesome-agent-ecosystem', input_sha256: 'b'.repeat(64),
    entries: [{
      id: 'legacy.mapped', title: 'Mapped', summary: 'Already represented.',
      classification: { category: 'skills', subtype: null, domains: [], formats: [], conventions: [], rationale: 'Historical category differs from canonical classification.' },
      source_url: null, channel_source: 'discover.awesome-agent-ecosystem', legacy_keys: ['old:key'],
      legacy: { category: 'templates', subcat: null, platform: null, source_label: null, stars: null, installs: null, last_verified: null, vmethod: null },
      content_kind: 'asset', expected_components: [], missing: [], mapped_resource_id: 'opendesign.web-prototype',
    }], platforms: [], coverage: { total_assets: 1, total_platforms: 0, outcomes: [{ legacy_key: 'old:key', target_id: 'opendesign.web-prototype', disposition: 'mapped', reason: 'represented canonically' }] },
  };
  const browse = getBrowseResources(expanded);
  assert.equal(browse.filter((item) => item.id === 'opendesign.web-prototype').length, 1);
  assert.equal(browse.find((item) => item.id === 'opendesign.web-prototype')?.discovery_aliases?.[0]?.title, 'Mapped');
  assert.equal(filterBrowseResources(expanded, { query: 'Mapped' })[0]?.id, 'opendesign.web-prototype');
  assert.ok(!filterBrowseResources(expanded, { category: 'skills' }).some((item) => item.id === 'opendesign.web-prototype'), 'an alias cannot move a canonical resource into another primary category');
  assert.equal(getBrowseResource(expanded, 'legacy.mapped')?.id, 'opendesign.web-prototype');
});
