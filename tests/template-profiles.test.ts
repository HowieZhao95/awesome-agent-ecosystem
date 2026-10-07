import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { runInNewContext } from 'node:vm';
import { parse } from 'yaml';
import type { Resource } from '../src/contracts.ts';

const resourcesSource = parse(await readFile(new URL('../data/resources.yaml', import.meta.url), 'utf8')) as { resources: Resource[] };
const catalog = JSON.parse(await readFile(new URL('../site/catalog.json', import.meta.url), 'utf8')) as {
  schema_version: number;
  resources: { resources: Resource[] };
};
const projectionSource = await readFile(new URL('../site/data.js', import.meta.url), 'utf8');
const projectionContext: { __DATA?: unknown } = {};
runInNewContext(`${projectionSource}\nglobalThis.__DATA = DATA;`, projectionContext);
const projectedData = JSON.parse(JSON.stringify(projectionContext.__DATA)) as {
  categories: { id: string; entries: Resource[] }[];
};

test('canonical template and design-system profiles appear in both generated v3 views', () => {
  const profiled = resourcesSource.resources.filter((resource) => resource.template || resource.design_system);
  assert.ok(profiled.some((resource) => resource.template), 'canonical data should include an audited template profile');
  assert.ok(profiled.some((resource) => resource.design_system), 'canonical data should include a design-system profile');

  for (const resource of profiled) {
    const fullRecord = catalog.resources.resources.find((candidate) => candidate.id === resource.id);
    assert.ok(fullRecord, `full catalog is missing ${resource.id}`);
    assert.deepEqual(fullRecord.template, resource.template);
    assert.deepEqual(fullRecord.design_system, resource.design_system);

    const category = projectedData.categories.find((candidate) => candidate.id === resource.classification.category);
    const siteRecord = category?.entries.find((candidate) => candidate.id === resource.id);
    assert.ok(siteRecord, `site projection is missing ${resource.id}`);
    assert.deepEqual(siteRecord.template, resource.template);
    assert.deepEqual(siteRecord.design_system, resource.design_system);
  }
});

test('ordinary v3 resources remain valid without optional profiles', () => {
  assert.equal(catalog.schema_version, 3);
  const ordinaryResource = resourcesSource.resources.find((resource) => !resource.template && !resource.design_system);
  assert.ok(ordinaryResource, 'canonical catalog retains records where these profiles do not apply');
  assert.ok(catalog.resources.resources.some((resource) => resource.id === ordinaryResource.id));
});
