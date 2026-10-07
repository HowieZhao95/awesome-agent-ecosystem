import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import type { Catalog, HostAdapter } from '../src/contracts.ts';
import { CatalogApp } from '../src/ui/index.tsx';

const catalog = JSON.parse(await readFile(new URL('../site/catalog.json', import.meta.url), 'utf8')) as Catalog;

async function mount(props: { catalog?: Catalog; host?: HostAdapter; status?: 'loading' | 'error' | 'ready'; error?: string; onRetry?: () => void; messages?: Record<string, string> }, hash = '') {
  const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: `https://catalog.test/${hash}` });
  Object.assign(globalThis, {
    window: dom.window,
    document: dom.window.document,
    HTMLElement: dom.window.HTMLElement,
    Event: dom.window.Event,
    MouseEvent: dom.window.MouseEvent,
    HashChangeEvent: dom.window.HashChangeEvent,
    IS_REACT_ACT_ENVIRONMENT: true,
  });
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: dom.window.navigator });
  const container = dom.window.document.getElementById('root')!;
  const root: Root = createRoot(container);
  await act(async () => root.render(React.createElement(CatalogApp, props)));
  return { dom, container, root, close: () => { act(() => root.unmount()); dom.window.close(); } };
}

test('shows all five resource categories and filters cards when a category is selected', async () => {
  const ui = await mount({ catalog });
  try {
    const nav = ui.container.querySelector('[aria-label="资源类别"]');
    assert.ok(nav);
    for (const label of ['设计模板', '设计系统', 'Skills', '提示词', '插件']) {
      assert.ok([...nav.querySelectorAll('button')].some((button) => button.textContent?.includes(label)), `missing category ${label}`);
    }
    const button = [...nav.querySelectorAll('button')].find((item) => item.dataset.category === 'plugins')!;
    await act(async () => button.dispatchEvent(new ui.dom.window.MouseEvent('click', { bubbles: true })));
    assert.ok(ui.container.querySelectorAll('[data-resource-card]').length > 0);
    assert.ok([...ui.container.querySelectorAll('[data-resource-card]')].every((card) => card.getAttribute('data-category') === 'plugins'));
  } finally { ui.close(); }
});

test('labels registered resources, discovery entries, and total directory items separately', async () => {
  const ui = await mount({ catalog });
  try {
    assert.ok(ui.container.textContent?.includes('1166 个目录条目'));
    assert.ok(ui.container.textContent?.includes('367 个已登记资源 · 799 条发现线索'));
    assert.ok(ui.container.textContent?.includes('个关联发现入口'));
    assert.ok(!ui.container.textContent?.includes('26 个平台来源'), 'platform records are shown on their source page, not counted as browse items');
  } finally { ui.close(); }
});

test('renders loading and error states and invokes the host retry callback', async () => {
  const loading = await mount({ status: 'loading' });
  try { assert.ok(loading.container.querySelector('[role="status"]')?.textContent?.includes('正在加载')); }
  finally { loading.close(); }
  let retries = 0;
  const failed = await mount({ status: 'error', error: 'offline', onRetry: () => { retries += 1; } });
  try {
    assert.ok(failed.container.querySelector('[role="alert"]')?.textContent?.includes('offline'));
    const retry = failed.container.querySelector<HTMLButtonElement>('.pas-state-error button');
    assert.ok(retry);
    act(() => retry.click());
    assert.equal(retries, 1);
  } finally { failed.close(); }
});

test('combines category navigation with search and links by stable resource identity', async () => {
  const resource = catalog.resources.resources[0]!;
  const ui = await mount({ catalog });
  try {
    await act(async () => {
      const category = ui.container.querySelector<HTMLButtonElement>(`button[data-category="${resource.classification.category}"]`)!;
      category.dispatchEvent(new ui.dom.window.MouseEvent('click', { bubbles: true }));
    });
    const search = ui.container.querySelector<HTMLInputElement>('input[type="search"]')!;
    await act(async () => {
      Object.getOwnPropertyDescriptor(ui.dom.window.HTMLInputElement.prototype, 'value')?.set?.call(search, resource.title);
      search.dispatchEvent(new ui.dom.window.Event('input', { bubbles: true }));
    });
    assert.ok(ui.container.querySelectorAll('[data-resource-card]').length > 0);
    assert.equal(ui.container.querySelectorAll('[data-resource-card]').length, 1);
    assert.ok([...ui.container.querySelectorAll('[data-resource-card]')].every((card) => card.getAttribute('data-category') === resource.classification.category));
    const link = ui.container.querySelector<HTMLAnchorElement>(`a[href="#/resource/${encodeURIComponent(resource.id)}"]`);
    assert.ok(link, 'card links by stable resource id');
  } finally { ui.close(); }
});

test('applies subtype, domain, source, verification, and lifecycle select filters', async () => {
  const target = catalog.resources.resources[0]!;
  assert.ok(target.classification.subtype);
  const ui = await mount({ catalog });
  try {
    const category = ui.container.querySelector<HTMLButtonElement>(`button[data-category="${target.classification.category}"]`)!;
    act(() => category.click());
    const select = (name: string, value: string) => {
      const control = ui.container.querySelector<HTMLSelectElement>(`select[name="${name}"]`)!;
      act(() => {
        control.value = value;
        control.dispatchEvent(new ui.dom.window.Event('change', { bubbles: true }));
      });
    };
    select('subtype', target.classification.subtype!);
    select('domain', target.classification.domains[0]!);
    select('source', target.provenance.content_source);
    select('verification', target.verification.level);
    select('lifecycle', target.lifecycle.state);
    const visibleIds = [...ui.container.querySelectorAll<HTMLElement>('[data-resource-card]')].map((card) => card.dataset.resourceId);
    assert.ok(visibleIds.length > 0);
    const visibleResources = catalog.resources.resources.filter((item) => visibleIds.includes(item.id));
    assert.ok(visibleResources.every((item) => item.classification.subtype === target.classification.subtype));
    assert.ok(visibleResources.every((item) => item.classification.domains.includes(target.classification.domains[0]!)));
    assert.ok(visibleResources.every((item) => item.provenance.content_source === target.provenance.content_source));
    assert.ok(visibleResources.every((item) => item.verification.level === target.verification.level));
    assert.ok(visibleResources.every((item) => item.lifecycle.state === target.lifecycle.state));
  } finally { ui.close(); }
});

test('opens a stable resource hash directly after refresh', async () => {
  const resource = catalog.resources.resources[0]!;
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    assert.ok(ui.container.querySelector('[data-resource-detail]'));
    assert.ok(ui.container.textContent?.includes(resource.title));
  } finally { ui.close(); }
});

test('keeps acquisition and verification visible while secondary source metadata starts collapsed', async () => {
  const resource = catalog.resources.resources.find((item) => item.id === 'opendesign.web-prototype')!;
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const sourceLink = ui.container.querySelector<HTMLAnchorElement>(`a[href="${resource.provenance.upstream.url}"]`);
    assert.ok(sourceLink, 'the original source remains directly available');
    assert.ok(ui.container.querySelector('[data-verification-badge]'), 'the compact verification badge remains visible');
    assert.ok(ui.container.querySelector('.pas-caution'), 'unknown redistribution rights remain visible');

    const disclosure = ui.container.querySelector<HTMLDetailsElement>('details[data-disclosure="source-metadata"]');
    assert.ok(disclosure, 'secondary metadata uses native details');
    assert.equal(disclosure.open, false);
    const summary = disclosure.querySelector('summary');
    assert.ok(summary?.textContent?.includes('作者、许可与来源版本'));

    await act(async () => summary?.click());
    assert.equal(disclosure.open, true);
    assert.ok(disclosure.textContent?.includes(resource.license.expression!));
    const upstreamVersion = resource.provenance.upstream.ref.value;
    assert.ok(upstreamVersion);
    assert.ok(disclosure.textContent?.includes(upstreamVersion));
  } finally { ui.close(); }
});

test('opens source records directly and lists resources by source identity', async () => {
  const source = catalog.sources.sources.find((item) => item.id === catalog.resources.resources[0]?.provenance.content_source)!;
  const resource = catalog.resources.resources.find((item) => item.provenance.content_source === source.id)!;
  const ui = await mount({ catalog }, `#/source/${encodeURIComponent(source.id)}`);
  try {
    assert.ok(ui.container.querySelector('[data-source-detail]'));
    assert.ok(ui.container.textContent?.includes(source.name));
    assert.ok(ui.container.querySelector(`a[href="#/resource/${encodeURIComponent(resource.id)}"]`));
  } finally { ui.close(); }
});

test('category navigation from a direct resource route returns to the filtered catalog', async () => {
  const resource = catalog.resources.resources[0]!;
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const category = ui.container.querySelector<HTMLButtonElement>('button[data-category="skills"]')!;
    await act(async () => category.click());
    assert.equal(ui.container.querySelector('[data-resource-detail]'), null);
    assert.ok([...ui.container.querySelectorAll('[data-resource-card]')].every((item) => item.getAttribute('data-category') === 'skills'));
  } finally { ui.close(); }
});

test('shows withdrawn resources with their reason and without host actions', async () => {
  const withdrawn = structuredClone(catalog);
  const resource = withdrawn.resources.resources[0]!;
  resource.lifecycle = { state: 'withdrawn', reason: 'Upstream withdrew this asset.', replacement_id: null };
  resource.previews = [];
  const ui = await mount({ catalog: withdrawn }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    assert.ok(ui.container.textContent?.includes('已撤回'));
    assert.ok(ui.container.textContent?.includes('Upstream withdrew this asset.'));
    assert.ok(!ui.container.querySelector('[aria-label="宿主操作"]'));
  } finally { ui.close(); }
});

test('shows missing previews on a real resource detail page', async () => {
  const withoutPreview = structuredClone(catalog);
  const resource = withoutPreview.resources.resources.find((item) => {
    const supportedSourceFile = (url: string) => /\.(md|markdown|json|css)(?:\?|$)/i.test(url);
    const sourceUrls = [item.provenance.upstream.url, ...item.verification.evidence.map((evidence) => evidence.locator)];
    return item.previews.length === 0 && !sourceUrls.some(supportedSourceFile);
  })!;
  assert.ok(resource);
  const ui = await mount({ catalog: withoutPreview }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    assert.ok(ui.container.textContent?.includes('暂无可内嵌预览'));
    assert.equal(ui.container.querySelectorAll('[data-resource-detail]').length, 1);
  } finally { ui.close(); }
});

test('renders a host operation failure as visible feedback', async () => {
  const host = {
    hostId: 'demo-host',
    account: { status: async () => 'signed-in' as const, login: async () => {} },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
    operations: { add: async () => { throw new Error('host refused'); }, install: async () => {}, apply: async () => {}, configure: async () => {} },
    theme: { get: () => 'light' as const, set: () => {} },
    i18n: { locale: 'zh-CN', translate: (key: string) => key },
    links: { open: () => {} },
    preview: { open: async () => {} },
  } satisfies HostAdapter;
  const resource = catalog.resources.resources.find((item) => item.lifecycle.state !== 'withdrawn')!;
  const ui = await mount({ catalog, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    await act(async () => { ui.container.querySelector<HTMLButtonElement>('button[data-action="add"]')?.click(); await Promise.resolve(); });
    assert.ok(ui.container.textContent?.includes('host refused'));
  } finally { ui.close(); }
});

test('routes all four approved host callbacks and refreshes projected host state', async () => {
  const demoCatalog = structuredClone(catalog);
  const resource = demoCatalog.resources.resources.find((item) => item.classification.category === 'plugins')!;
  assert.ok(resource);
  resource.lifecycle.state = 'usable';
  resource.review.status = 'approved';
  resource.license.status = 'verified';
  resource.license.redistribution = 'allowed';
  resource.verification.level = 'usage-tested';
  resource.verification.tested_hosts = ['demo-host'];
  demoCatalog.availability = { ...(demoCatalog.availability ?? {}), [resource.id]: ['demo-host'] };
  const called: string[] = [];
  const state = { added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: true };
  const host: HostAdapter = {
    hostId: 'demo-host',
    account: { status: async () => 'signed-in', login: async () => {} },
    assetStatus: async () => ({ ...state }),
    operations: {
      add: async () => { called.push('add'); state.added = true; },
      install: async () => { called.push('install'); state.installed = true; },
      apply: async () => { called.push('apply'); state.applied = true; },
      configure: async () => { called.push('configure'); state.requiresConfiguration = false; },
    },
    theme: { get: () => 'dark', set: () => {} },
    i18n: { locale: 'en', translate: (key) => ({ brand: 'Demo host', 'search.label': 'Find resources', 'theme.label': 'Appearance' }[key] ?? key) },
    links: { open: () => {} },
    preview: { open: () => {} },
  };
  const ui = await mount({ catalog: demoCatalog, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    assert.equal(ui.container.querySelector('.pas-app')?.getAttribute('data-theme'), 'dark');
    assert.ok(ui.container.querySelector('.pas-theme-label')?.textContent?.includes('Appearance'));
    assert.ok(ui.container.textContent?.includes('Demo host'));
    assert.equal(ui.container.querySelector<HTMLButtonElement>('button[data-action="install"]')?.disabled, false);
    for (const action of ['add', 'install', 'apply', 'configure']) {
      const button = ui.container.querySelector<HTMLButtonElement>(`button[data-action="${action}"]`)!;
      assert.ok(button, `expected ${action} host control`);
      await act(async () => {
        button.click();
        await new Promise((resolve) => setTimeout(resolve, 0));
      });
    }
    assert.deepEqual(called, ['add', 'install', 'apply', 'configure']);
    assert.ok(ui.container.textContent?.includes('已添加'));
  } finally { ui.close(); }
});

test('does not expose install for a host without a resource availability grant', async () => {
  const host: HostAdapter = {
    hostId: 'thusdesign',
    account: { status: async () => 'signed-in', login: async () => {} },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
    operations: { add: async () => {}, install: async () => {}, apply: async () => {}, configure: async () => {} },
    theme: { get: () => 'system', set: () => {} },
    i18n: { locale: 'zh-CN', translate: (key) => key },
    links: { open: () => {} },
    preview: { open: () => {} },
  };
  const resource = catalog.resources.resources[0]!;
  const ui = await mount({ catalog, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    assert.equal(ui.container.querySelector('button[data-action="install"]'), null);
    assert.ok(ui.container.textContent?.includes('尚未满足此宿主的使用验证条件'));
  } finally { ui.close(); }
});

test('waits for the host login callback before showing signed-in state', async () => {
  const resource = catalog.resources.resources[0]!;
  let accountState: 'signed-in' | 'signed-out' = 'signed-out';
  let finishLogin!: () => void;
  let loginCalls = 0;
  const host: HostAdapter = {
    hostId: 'login-test-host',
    account: {
      status: async () => accountState,
      login: async () => {
        loginCalls += 1;
        await new Promise<void>((resolve) => { finishLogin = () => { accountState = 'signed-in'; resolve(); }; });
      },
    },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
    operations: { add: async () => {}, install: async () => {}, apply: async () => {}, configure: async () => {} },
    theme: { get: () => 'light', set: () => {} },
    i18n: { locale: 'zh-CN', translate: (key) => key },
    links: { open: () => {} },
    preview: { open: () => {} },
  };
  const ui = await mount({ catalog, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    assert.equal(ui.container.querySelector('[data-action="login"]')?.textContent, '登录宿主');
    await act(async () => { ui.container.querySelector<HTMLButtonElement>('[data-action="login"]')?.click(); });
    assert.equal(loginCalls, 1);
    assert.ok(ui.container.querySelector('[data-action="login"]'), 'the host still reports signed out while login is pending');
    await act(async () => { finishLogin(); await Promise.resolve(); });
    assert.equal(ui.container.querySelector('[data-action="login"]'), null);
    assert.ok(ui.container.textContent?.includes('未添加'));
  } finally { ui.close(); }
});

test('uses host theme and translated filter labels and reports a requested theme change', async () => {
  const themeChanges: string[] = [];
  const translations: Record<string, string> = {
    brand: 'Localized host catalog',
    'search.label': 'Find resources',
    'filter.source': 'Publisher',
    'theme.label': 'Appearance',
    'theme.light': 'Light mode',
    'theme.dark': 'Dark mode',
  };
  let themeValue: 'light' | 'dark' | 'system' = 'dark';
  let themeReads = 0;
  const host: HostAdapter = {
    hostId: 'theme-test-host',
    account: { status: async () => 'signed-out', login: async () => {} },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
    operations: { add: async () => {}, install: async () => {}, apply: async () => {}, configure: async () => {} },
    theme: { get: () => { themeReads += 1; return themeValue; }, set: (value) => { themeValue = value; themeChanges.push(value); } },
    i18n: { locale: 'en', translate: (key) => translations[key] ?? key },
    links: { open: () => {} },
    preview: { open: () => {} },
  };
  const ui = await mount({ catalog, host });
  try {
    assert.ok(themeReads > 0);
    assert.equal(ui.container.querySelector('.pas-app')?.getAttribute('data-theme'), 'dark');
    assert.ok(ui.container.textContent?.includes('Localized host catalog'));
    assert.ok(ui.container.querySelector<HTMLInputElement>('input[type="search"][aria-label="Find resources"]'));
    assert.ok([...ui.container.querySelectorAll('label')].some((label) => label.textContent?.includes('Publisher')));
    const themeSelect = ui.container.querySelector<HTMLSelectElement>('#theme-select')!;
    assert.ok([...themeSelect.options].some((option) => option.textContent === 'Light mode'));
    act(() => {
      themeSelect.value = 'light';
      themeSelect.dispatchEvent(new ui.dom.window.Event('change', { bubbles: true }));
    });
    assert.deepEqual(themeChanges, ['light']);
    assert.equal(ui.container.querySelector('.pas-app')?.getAttribute('data-theme'), 'light');
  } finally { ui.close(); }
});

test('routes external links and preview requests through the host adapter', async () => {
  const resource = catalog.resources.resources.find((item) => item.provenance.upstream.url && item.previews.length > 0)!;
  const openedLinks: string[] = [];
  const openedPreviews: string[] = [];
  const host: HostAdapter = {
    hostId: 'navigation-test-host',
    account: { status: async () => 'signed-in', login: async () => {} },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
    operations: { add: async () => {}, install: async () => {}, apply: async () => {}, configure: async () => {} },
    theme: { get: () => 'light', set: () => {} },
    i18n: { locale: 'zh-CN', translate: (key) => key },
    links: { open: (url) => { openedLinks.push(url); } },
    preview: { open: (_resource, url) => { openedPreviews.push(url); } },
  };
  const ui = await mount({ catalog, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    const sourceLink = [...ui.container.querySelectorAll<HTMLAnchorElement>('a')].find((link) => link.textContent?.includes('打开上游文件'))!;
    await act(async () => sourceLink.click());
    assert.deepEqual(openedLinks, [resource.provenance.upstream.url]);
    const hostPreview = [...ui.container.querySelectorAll<HTMLButtonElement>('button')].find((button) => button.textContent?.includes('在宿主中打开预览'))!;
    await act(async () => hostPreview.click());
    assert.deepEqual(openedPreviews, [resource.previews[0]?.url]);
  } finally { ui.close(); }
});

test('withdrawn resources suppress every host action even when the host grants availability', async () => {
  const withdrawn = structuredClone(catalog);
  const resource = withdrawn.resources.resources.find((item) => item.classification.category === 'plugins')!;
  resource.lifecycle = { state: 'withdrawn', reason: 'Withdrawn for this host test.', replacement_id: null };
  withdrawn.availability = { ...(withdrawn.availability ?? {}), [resource.id]: ['withdrawn-test-host'] };
  const called: string[] = [];
  const host: HostAdapter = {
    hostId: 'withdrawn-test-host',
    account: { status: async () => 'signed-in', login: async () => {} },
    assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: true }),
    operations: {
      add: async () => { called.push('add'); },
      install: async () => { called.push('install'); },
      apply: async () => { called.push('apply'); },
      configure: async () => { called.push('configure'); },
    },
    theme: { get: () => 'light', set: () => {} },
    i18n: { locale: 'zh-CN', translate: (key) => key },
    links: { open: () => {} },
    preview: { open: () => {} },
  };
  const ui = await mount({ catalog: withdrawn, host }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 0)); });
    assert.ok(ui.container.textContent?.includes('Withdrawn for this host test.'));
    assert.equal(ui.container.querySelector('[aria-label="宿主操作"]'), null);
    for (const action of ['login', 'add', 'install', 'apply', 'configure']) {
      assert.equal(ui.container.querySelector(`[data-action="${action}"]`), null, `withdrawn resource exposes ${action}`);
    }
    assert.deepEqual(called, []);
  } finally { ui.close(); }
});

test('loads public HTML only after click and keeps the preview sandbox without same-origin access', async () => {
  const resource = catalog.resources.resources.find((item) => item.previews.some((preview) => preview.kind === 'html'))!;
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response('<script>window.parent.secret = true</script><main>Preview</main>', { status: 200 });
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const load = ui.container.querySelector<HTMLButtonElement>('button[data-preview-load="html"]')!;
    assert.ok(load, 'HTML is not loaded before the user clicks');
    await act(async () => { load.click(); await new Promise((resolve) => setTimeout(resolve, 0)); });
    const frame = ui.container.querySelector<HTMLIFrameElement>('iframe');
    assert.ok(frame);
    assert.equal(frame.getAttribute('sandbox'), 'allow-scripts');
    assert.ok(!frame.getAttribute('sandbox')?.includes('allow-same-origin'));
    assert.ok(frame.srcdoc.includes('<script>'));
  } finally { globalThis.fetch = originalFetch; ui.close(); }
});

test('resolves relative stylesheet links in HTML previews against their exact upstream directory', async () => {
  const previewed = structuredClone(catalog);
  const resource = previewed.resources.resources.find((item) => item.classification.category === 'design-systems')!;
  const ref = resource.provenance.upstream.ref.value!;
  const sourceUrl = `https://github.com/nexu-io/open-design/blob/${ref}/design-systems/agentic/system/previews/colors.html`;
  const cssUrl = `https://raw.githubusercontent.com/nexu-io/open-design/${ref}/design-systems/agentic/system/tokens.css`;
  resource.previews = [{ kind: 'html', url: sourceUrl, status: 'reference', evidence: [] }];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input) => String(input) === cssUrl
    ? new Response(':root { --accent: #ff385c; }', { status: 200 })
    : new Response('<!doctype html><html><head><base href="https://old.invalid/"><link rel="stylesheet" href="../tokens.css"></head><body><main>Color reference</main></body></html>', { status: 200 });
  const ui = await mount({ catalog: previewed }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const load = ui.container.querySelector<HTMLButtonElement>('button[data-preview-load="html"]')!;
    await act(async () => { load.click(); await new Promise((resolve) => setTimeout(resolve, 0)); });
    const frame = ui.container.querySelector<HTMLIFrameElement>('iframe')!;
    const parsed = new ui.dom.window.DOMParser().parseFromString(frame.srcdoc, 'text/html');
    const expectedDirectory = `https://raw.githubusercontent.com/nexu-io/open-design/${ref}/design-systems/agentic/system/previews/`;
    assert.equal(parsed.querySelectorAll('base').length, 1);
    assert.equal(parsed.querySelector('base')?.getAttribute('href'), expectedDirectory);
    assert.equal(parsed.querySelector('style')?.getAttribute('data-source-url'), new URL('../tokens.css', expectedDirectory).href);
  } finally { globalThis.fetch = originalFetch; ui.close(); }
});

test('inlines pinned raw GitHub CSS dependencies in a design system preview with source provenance', async () => {
  const previewed = structuredClone(catalog);
  const resource = previewed.resources.resources.find((item) => item.classification.category === 'design-systems')!;
  const ref = resource.provenance.upstream.ref.value!;
  const sourceUrl = `https://github.com/nexu-io/open-design/blob/${ref}/design-systems/agentic/system/previews/colors.html`;
  const cssUrl = `https://raw.githubusercontent.com/nexu-io/open-design/${ref}/design-systems/agentic/system/tokens.css`;
  resource.previews = [{ kind: 'html', url: sourceUrl, status: 'reference', evidence: [] }];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input) => String(input) === cssUrl
    ? new Response(':root { --accent: #ff385c; }', { status: 200, headers: { 'content-type': 'text/plain' } })
    : new Response('<!doctype html><html><head><link rel="stylesheet" href="../tokens.css"></head><body><main>Color swatch</main></body></html>', { status: 200 });
  const ui = await mount({ catalog: previewed }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const load = ui.container.querySelector<HTMLButtonElement>('button[data-preview-load="html"]')!;
    await act(async () => { load.click(); await new Promise((resolve) => setTimeout(resolve, 0)); });
    const frame = ui.container.querySelector<HTMLIFrameElement>('iframe')!;
    assert.ok(frame.srcdoc.includes('<style data-source-url="https://raw.githubusercontent.com/nexu-io/open-design/'));
    assert.ok(frame.srcdoc.includes(':root { --accent: #ff385c; }'));
    assert.ok(frame.srcdoc.includes(`data-source-url="${cssUrl}"`));
    assert.ok(!frame.srcdoc.includes('href="../tokens.css"'));
    assert.equal(frame.getAttribute('sandbox'), 'allow-scripts');
    assert.ok(!frame.getAttribute('sandbox')?.includes('allow-same-origin'));
  } finally { globalThis.fetch = originalFetch; ui.close(); }
});

test('renders fetched Skill source as plain text after an explicit click', async () => {
  const resource = catalog.resources.resources.find((item) => item.classification.category === 'skills' && item.provenance.upstream.url.endsWith('.md'))!;
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response('# Skill source\n<script>not executed</script>', { status: 200 });
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const load = ui.container.querySelector<HTMLButtonElement>('button[data-preview-load="markdown"]')!;
    assert.ok(load);
    await act(async () => { load.click(); await new Promise((resolve) => setTimeout(resolve, 0)); });
    const body = ui.container.querySelector<HTMLElement>('.pas-source-text')!;
    assert.ok(body.textContent?.includes('<script>not executed</script>'));
    assert.equal(body.querySelector('script'), null);
  } finally { globalThis.fetch = originalFetch; ui.close(); }
});

test('shows multiple real preview references in a navigable image carousel', async () => {
  const withGallery = structuredClone(catalog);
  const resource = withGallery.resources.resources[0]!;
  resource.previews = [
    { kind: 'image', url: 'https://assets.example.test/first.png', status: 'reference', evidence: [] },
    { kind: 'image', url: 'https://assets.example.test/second.png', status: 'reference', evidence: [] },
    { kind: 'video', url: 'https://assets.example.test/clip.mp4', status: 'reference', evidence: [] },
  ];
  const ui = await mount({ catalog: withGallery }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const image = ui.container.querySelector<HTMLImageElement>('.pas-gallery img')!;
    assert.ok(image.src.endsWith('/first.png'));
    await act(async () => ui.container.querySelector<HTMLButtonElement>('[aria-label="下一张"]')?.click());
    assert.ok(ui.container.querySelector<HTMLImageElement>('.pas-gallery img')?.src.endsWith('/second.png'));
    assert.ok(ui.container.querySelector('video[controls]'));
  } finally { ui.close(); }
});

test('shows template framework files separately from reference examples and labels mixed upstream honestly', async () => {
  const profiled = structuredClone(catalog);
  const resource = profiled.resources.resources.find((item) => item.classification.category === 'templates')!;
  Object.assign(resource, {
    template: {
      files: [
        { role: 'instructions', path: 'SKILL.md', url: 'https://example.test/SKILL.md' },
        { role: 'framework', path: 'assets/seed.html', url: 'https://example.test/seed.html' },
        { role: 'example', path: 'examples/demo.html', url: 'https://example.test/demo.html' },
        { role: 'support', path: 'references/checklist.md', url: 'https://example.test/checklist.md' },
      ],
      style: { policy: 'external-design-system', upstream_status: 'mixed', note: 'Prompt still preserves the upstream visual signature.' },
    },
  });
  const ui = await mount({ catalog: profiled }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const detail = ui.container.querySelector('[data-resource-detail]')!;
    assert.ok(detail.textContent?.includes('内容与代码框架'));
    assert.ok(detail.textContent?.includes('参考示例（样式不属于模板）'));
    assert.ok(detail.textContent?.includes('上游框架与风格待拆分'));
    assert.ok(detail.textContent?.includes('Prompt still preserves the upstream visual signature.'));
    assert.ok(detail.querySelector('a[href="https://example.test/seed.html"]'));
    assert.ok(detail.querySelector('a[href="https://example.test/demo.html"]'));
    assert.ok(!detail.textContent?.includes('样式已解耦'));
  } finally { ui.close(); }
});

test('keeps legacy template records without profiles readable and shows profile completion as pending', async () => {
  const legacy = structuredClone(catalog);
  const resource = legacy.resources.resources.find((item) => item.classification.category === 'templates')!;
  delete resource.template;
  const ui = await mount({ catalog: legacy }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const detail = ui.container.querySelector('[data-resource-detail]')!;
    assert.ok(detail.textContent?.includes(resource.title));
    assert.ok(detail.textContent?.includes('文件角色待补充'));
  } finally { ui.close(); }
});

test('lists the design system core files and makes missing core roles explicit', async () => {
  const profiled = structuredClone(catalog);
  const resource = profiled.resources.resources.find((item) => item.classification.category === 'design-systems')!;
  Object.assign(resource, {
    design_system: {
      files: [
        { role: 'manifest', path: 'manifest.json', url: 'https://example.test/manifest.json' },
        { role: 'rules', path: 'DESIGN.md', url: 'https://example.test/DESIGN.md' },
      ],
    },
  });
  const ui = await mount({ catalog: profiled }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const detail = ui.container.querySelector('[data-resource-detail]')!;
    assert.ok(detail.textContent?.includes('设计系统文件'));
    assert.ok(detail.querySelector('a[href="https://example.test/manifest.json"]'));
    assert.ok(detail.querySelector('a[href="https://example.test/DESIGN.md"]'));
    assert.ok(detail.textContent?.includes('缺少核心文件角色：tokens.css'));
  } finally { ui.close(); }
});

test('keeps an explicitly previewable design system example available when the profile names the same URL', async () => {
  const resource = catalog.resources.resources.find((item) => item.classification.category === 'design-systems'
    && item.design_system?.files.some((file) => file.role === 'example' && item.previews.some((preview) => preview.url === file.url))
    && item.previews.some((preview) => preview.kind === 'html'))!;
  assert.ok(resource, 'uses a real design system record whose example profile file is also an HTML preview');
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response('<!doctype html><html><head><link rel="stylesheet" href="../tokens.css"></head><body><main>Design system example</main></body></html>', { status: 200 });
  const ui = await mount({ catalog }, `#/resource/${encodeURIComponent(resource.id)}`);
  try {
    const load = ui.container.querySelector<HTMLButtonElement>('button[data-preview-load="html"]');
    assert.ok(load, 'the profile example remains available in the explicit preview area');
    await act(async () => { load.click(); await new Promise((resolve) => setTimeout(resolve, 0)); });
    assert.ok(ui.container.querySelector('iframe[title*="隔离预览"]'));
  } finally { globalThis.fetch = originalFetch; ui.close(); }
});

test('shows the canonical category definition when a category is selected', async () => {
  const ui = await mount({ catalog });
  try {
    const category = catalog.categories.categories.find((item) => item.id === 'templates')!;
    await act(async () => ui.container.querySelector<HTMLButtonElement>('button[data-category="templates"]')?.click());
    assert.ok(ui.container.textContent?.includes(category.definition));
  } finally { ui.close(); }
});
