import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import type { Catalog, HostAdapter } from '../src/contracts.ts';
import { CatalogApp } from '../src/ui/index.tsx';

const canonical = JSON.parse(await readFile(new URL('../site/catalog.json', import.meta.url), 'utf8')) as Catalog;
const fullLegacyIndex = JSON.parse(await readFile(new URL('../docs/evidence/complete-directory/legacy-index.json', import.meta.url), 'utf8')) as NonNullable<Catalog['discovery']>;
const catalog: Catalog = structuredClone(canonical);
catalog.discovery = {
  schema_version: 1, source_id: 'discover.awesome-agent-ecosystem', input_sha256: 'c'.repeat(64),
  entries: [
    { id: 'discovery.prompt-library', title: 'Prompt Library', summary: 'A collection of writing prompts.', classification: { category: 'prompts', subtype: null, domains: [], formats: [], conventions: [], rationale: 'The legacy record identifies a collection.' }, source_url: 'https://github.com/example/prompts', channel_source: 'discover.awesome-agent-ecosystem', legacy_keys: ['prompt-library#1'], legacy: { category: 'prompts', subcat: 'library', platform: 'GitHub', source_label: 'Old index', stars: 123, installs: null, last_verified: null, vmethod: null }, content_kind: 'collection', expected_components: [], missing: ['original author and license not verified'] },
    { id: 'discovery.mapped', title: 'Canonical duplicate', summary: 'Already represented by a canonical resource.', classification: { category: 'templates', subtype: null, domains: [], formats: [], conventions: [], rationale: 'Mapped in the import review.' }, source_url: 'https://github.com/example/legacy-prototype', channel_source: 'discover.awesome-agent-ecosystem', legacy_keys: ['mapped#1'], legacy: { category: 'templates', subcat: null, platform: null, source_label: 'Historic Official label', stars: 7, installs: null, last_verified: null, vmethod: null }, content_kind: 'asset', expected_components: [], missing: [], mapped_resource_id: 'opendesign.web-prototype' },
  ], platforms: Array.from({ length: 26 }, (_, index) => ({ id: `platform-${index + 1}`, name: `Platform ${index + 1}`, url: null, summary: `Historical platform ${index + 1}.`, legacy_key: `source#${index + 1}`, source_label: 'Old platform label' })),
  coverage: { total_assets: 2, total_platforms: 26, outcomes: [
    { legacy_key: 'prompt-library#1', target_id: 'discovery.prompt-library', disposition: 'discovery', reason: 'retained as a discovery entry' },
    { legacy_key: 'mapped#1', target_id: 'opendesign.web-prototype', disposition: 'mapped', reason: 'represented canonically' },
  ] },
};
const baseDiscovery = structuredClone(catalog.discovery.entries[0]!);
for (let index = 2; index <= 776; index += 1) {
  const entry = structuredClone(baseDiscovery);
  entry.id = `discovery.large-${index}`;
  entry.title = `Legacy evidence ${index}`;
  entry.summary = `Historical large-catalog fixture ${index}.`;
  entry.legacy_keys = [`large-index/item-${index}`];
  catalog.discovery.entries.push(entry);
  catalog.discovery.coverage.outcomes.push({ legacy_key: entry.legacy_keys[0]!, target_id: entry.id, disposition: 'discovery', reason: 'fixture retained for browse coverage' });
}
catalog.discovery.coverage.total_assets = 777;

async function mount(hash = '', host?: HostAdapter, pageSize = 12, sourceCatalog: Catalog = catalog) {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: `https://catalog.test/${hash}` });
  Object.assign(globalThis, { window: dom.window, document: dom.window.document, HTMLElement: dom.window.HTMLElement, Event: dom.window.Event, MouseEvent: dom.window.MouseEvent, HashChangeEvent: dom.window.HashChangeEvent, IS_REACT_ACT_ENVIRONMENT: true });
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: dom.window.navigator });
  const container = dom.window.document.getElementById('root')!;
  const root: Root = createRoot(container);
  await act(async () => root.render(React.createElement(CatalogApp, { catalog: sourceCatalog, host, pageSize })));
  return { dom, container, close: () => { act(() => root.unmount()); dom.window.close(); } };
}

test('shows discovery entries in the default browse and keeps platform records out of the asset count', async () => {
  const ui = await mount('', undefined, 2000);
  try {
    assert.equal(ui.container.querySelectorAll('[data-resource-card]').length, catalog.resources.resources.length + 776);
    assert.ok(ui.container.querySelector('[data-resource-id="discovery.prompt-library"]'));
    assert.ok(ui.container.querySelector('[data-resource-id="discovery.large-776"]'));
    assert.ok(ui.container.textContent?.includes(String(catalog.resources.resources.length + 776)));
    assert.ok(!ui.container.querySelector('[data-resource-id="discovery.mapped"]'));
    const search = ui.container.querySelector<HTMLInputElement>('input[type="search"]')!;
    await act(async () => { search.value = 'Legacy evidence 776'; search.dispatchEvent(new ui.dom.window.Event('input', { bubbles: true })); });
    assert.equal(ui.container.querySelectorAll('[data-resource-card]').length, 1, 'search covers entries beyond the first page');
  } finally { ui.close(); }
});

test('renders every target from the complete 777-entry legacy index in one browse result set', async () => {
  const completeCatalog = structuredClone(canonical);
  completeCatalog.discovery = fullLegacyIndex;
  const targets = new Set(fullLegacyIndex.entries.map((entry) => entry.mapped_resource_id ?? entry.id));
  const canonicalIds = new Set(completeCatalog.resources.resources.map((resource) => resource.id));
  const expectedCardCount = canonicalIds.size + [...targets].filter((id) => !canonicalIds.has(id)).length;
  const ui = await mount('', undefined, 2000, completeCatalog);
  try {
    const renderedIds = new Set([...ui.container.querySelectorAll<HTMLElement>('[data-resource-card]')].map((card) => card.dataset.resourceId));
    assert.equal(renderedIds.size, expectedCardCount);
    for (const id of targets) assert.ok(renderedIds.has(id), `missing browse target for ${id}`);
    assert.ok(ui.container.textContent?.includes(String(expectedCardCount)));
  } finally { ui.close(); }
  const sourcePage = await mount('#/source/discover.awesome-agent-ecosystem', undefined, 12, completeCatalog);
  try {
    assert.equal(sourcePage.container.querySelectorAll('[data-platform-record]').length, fullLegacyIndex.platforms.length);
    assert.equal(sourcePage.container.querySelectorAll('[data-discovery-record]').length, fullLegacyIndex.entries.length);
  } finally { sourcePage.close(); }
});

test('filters discovery origin and opens the historical source page with all platform records', async () => {
  const ui = await mount();
  try {
    const origin = ui.container.querySelector<HTMLSelectElement>('select[name="origin"]')!;
    await act(async () => { origin.value = 'discovery'; origin.dispatchEvent(new ui.dom.window.Event('change', { bubbles: true })); });
    assert.ok([...ui.container.querySelectorAll<HTMLElement>('[data-resource-card]')].every((card) => card.dataset.resourceId?.startsWith('discovery.') || card.dataset.resourceId === 'opendesign.web-prototype'));
  } finally { ui.close(); }
  const sourcePage = await mount('#/source/discover.awesome-agent-ecosystem');
  try {
    assert.equal(sourcePage.container.querySelectorAll('[data-platform-record]').length, 26);
    assert.ok(sourcePage.container.querySelector('a[href="#/resource/opendesign.web-prototype"]')?.textContent?.includes('Canonical duplicate'));
    assert.ok(sourcePage.container.textContent?.includes('不计入资源数'));
  } finally { sourcePage.close(); }
});

test('direct refresh shows discovery evidence and gaps without fabricated provenance or host operations', async () => {
  let operations = 0;
  let statusReads = 0;
  const host: HostAdapter = {
    hostId: 'test', account: { status: async () => 'signed-in', login: async () => {} },
    assetStatus: async () => { statusReads += 1; return { added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }; },
    operations: { add: async () => { operations++; }, install: async () => { operations++; }, apply: async () => { operations++; }, configure: async () => { operations++; } },
    theme: { get: () => 'light', set: () => {} }, i18n: { locale: 'zh-CN', translate: (key) => key }, links: { open: () => {} }, preview: { open: () => {} },
  };
  const ui = await mount(`#/resource/${encodeURIComponent('discovery.prompt-library')}`, host);
  try {
    const detail = ui.container.querySelector('[data-discovery-detail]');
    assert.ok(detail, 'direct resource route resolves after refresh');
    assert.ok(detail.textContent?.includes('collection'));
    assert.ok(detail.textContent?.includes('原始作者与许可') || detail.textContent?.includes('original author and license not verified'));
    const sourceLink = detail.querySelector<HTMLAnchorElement>('a[data-discovery-source]');
    assert.equal(sourceLink?.href, 'https://github.com/example/prompts');
    assert.ok(sourceLink?.textContent?.includes('发现线索链接'));
    assert.equal(detail.querySelector('[aria-label="宿主操作"]'), null);
    assert.equal(detail.querySelector('[data-verification-badge]')?.textContent, '未验证');
    assert.equal(operations, 0);
    assert.equal(statusReads, 0);
  } finally { ui.close(); }
});

test('keeps unknown source URLs empty on a direct discovery route', async () => {
  const withoutSourceUrl = structuredClone(catalog);
  withoutSourceUrl.discovery!.entries[0]!.source_url = null;
  const ui = await mount('#/resource/discovery.prompt-library', undefined, 12, withoutSourceUrl);
  try {
    const detail = ui.container.querySelector('[data-discovery-detail]');
    assert.ok(detail);
    assert.equal(detail.querySelector('a[data-discovery-source]'), null);
    assert.ok(detail.textContent?.includes('尚未定位到具体内容来源链接'));
  } finally { ui.close(); }
});

test('direct legacy aliases open the canonical resource once and retain historical source lineage', async () => {
  const ui = await mount('#/resource/discovery.mapped');
  try {
    assert.equal(ui.container.querySelectorAll('[data-resource-detail]').length, 1);
    assert.ok(ui.container.textContent?.includes('Web Prototype'));
    const alias = ui.container.querySelector('[data-discovery-alias]');
    assert.ok(alias?.textContent?.includes('Canonical duplicate'));
    assert.ok(alias?.textContent?.includes('Historic Official label'));
    assert.ok(alias?.querySelector('a[href="https://github.com/example/legacy-prototype"]'));
    assert.ok(alias?.textContent?.includes('历史来源标签仅保留原记录信息'));
  } finally { ui.close(); }
});
