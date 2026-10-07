import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { filterResources, getResource, getResourcePageUrl, getRelatedComponents, isAvailableForHost, loadCatalog, paginateResources } from '../src/catalog.ts';

const catalog = JSON.parse(await readFile(new URL('../site/catalog.json', import.meta.url), 'utf8'));

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
