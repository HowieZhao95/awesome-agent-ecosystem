import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parse } from 'yaml';
import { CategoryIdValues, ComponentTypeIdValues, ConventionIdValues, DomainIdValues, FormatIdValues, SubtypeIdValues } from '../src/generated/enums.ts';
import { getResourcePageUrl } from '../src/catalog.ts';

test('every generated literal set exactly matches the YAML source of truth', async () => {
  const source = parse(await readFile(new URL('../data/categories.yaml', import.meta.url), 'utf8'));
  assert.deepEqual(CategoryIdValues, source.categories.map((item: { id: string }) => item.id));
  assert.deepEqual(SubtypeIdValues, source.categories.flatMap((item: { subtypes?: { id: string }[] }) => item.subtypes?.map((subtype) => subtype.id) ?? []));
  assert.deepEqual(DomainIdValues, source.dimensions.domains.map((item: { id: string }) => item.id));
  assert.deepEqual(FormatIdValues, source.dimensions.formats.map((item: { id: string }) => item.id));
  assert.deepEqual(ConventionIdValues, source.dimensions.conventions.map((item: { id: string }) => item.id));
  assert.deepEqual(ComponentTypeIdValues, source.dimensions.plugin_component_types.map((item: { id: string }) => item.id));
});

test('public detail links encode resource identity without depending on its title', () => {
  assert.equal(getResourcePageUrl('vendor.name/with space'), '#/resource/vendor.name%2Fwith%20space');
});
