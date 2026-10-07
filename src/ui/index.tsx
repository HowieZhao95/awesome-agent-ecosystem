import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { Catalog, DesignSystemProfile, HostAdapter, ProfileFile, Resource, TemplateProfile } from '../contracts.js';
import { filterResources, getResource, isAvailableForHost } from '../catalog.js';

export interface CatalogAppProps {
  catalog?: Catalog;
  host?: HostAdapter;
  status?: 'loading' | 'error' | 'ready';
  error?: string;
  locale?: string;
  messages?: Record<string, string>;
  theme?: 'light' | 'dark' | 'system';
  accent?: string;
  pageSize?: number;
  onRetry?: () => void;
}

type Route = { type: 'catalog' } | { type: 'resource'; id: string } | { type: 'source'; id: string };
type Filters = { category: string; subtype: string; domain: string; source: string; verification: string; lifecycle: string; query: string };

const EMPTY_FILTERS: Filters = { category: '', subtype: '', domain: '', source: '', verification: '', lifecycle: '', query: '' };
const DEFAULT_MESSAGES: Record<string, string> = {
  'skip.main': '跳到主要内容', 'categories.title': '资源类别', 'category.all': '全部资源',
  'brand': 'Agent 资源目录', 'page.title': 'Agent 创作资源', 'theme.label': '界面主题', 'theme.light': '浅色', 'theme.dark': '深色',
  'catalog.eyebrow': 'PUBLIC RESOURCE CATALOG', 'catalog.intro': '从公开来源发现的模板、设计系统、Skills、提示词和插件，按真实来源与验证状态浏览。',
  'resource.count': '{count} 项资源', 'catalog.version': '目录版本 {version}', 'catalog.updated': '更新于 {date}',
  'search.label': '搜索资源', 'search.placeholder': '搜索名称、用途或简介…',
  'filter.subtype': '子类型', 'filter.domain': '领域', 'filter.source': '来源', 'filter.verification': '验证', 'filter.lifecycle': '生命周期', 'filter.all': '全部',
  'result.all': '全部资源', 'result.count': '{count} 项结果', 'filter.clear': '清除筛选', 'result.empty': '没有符合条件的资源。',
  'page.previous': '上一页', 'page.next': '下一页', 'page.current': '第 {page} / {count} 页',
  'state.loading': '正在加载资源目录…', 'state.error': '目录加载失败：{error}', 'state.unavailable': '资源目录不可用', 'state.retry': '重试',
  'detail.back': '← 返回资源目录', 'detail.notFound': '找不到这个资源。', 'source.notFound': '找不到这个来源。',
  'preview.eyebrow': '预览与来源文件', 'preview.title': '资源内容', 'preview.empty': '暂无可内嵌预览；请使用下方原始来源入口。',
  'preview.loading': '正在读取…', 'preview.readText': '读取来源文本', 'preview.readHtml': '加载隔离预览', 'preview.openHost': '在宿主中打开预览',
  'preview.failed': '读取失败。你可以直接打开原始来源。', 'preview.mediaFailed': '媒体加载失败，请打开原始来源。', 'preview.external': '预览来自外部来源，浏览器会向该来源请求内容。预览状态：{status}。', 'preview.openSource': '查看原始来源 ↗',
  'preview.openImage': '打开 {title} 的图片预览', 'preview.imageAlt': '{title} 外部预览', 'preview.unsupported': '当前不支持此预览格式。',
  'preview.previous': '上一张', 'preview.next': '下一张', 'preview.gallery': '{title} 图片轮播', 'preview.image': '{title} 图片 {number}', 'preview.imageCount': '{number} / {count}',
  'detail.withdrawn': '此资源已撤回', 'detail.hostActions': '宿主操作', 'detail.signIn': '登录宿主', 'detail.notSignedIn': '未登录', 'detail.hostLoading': '读取宿主状态…', 'detail.builtIn': '宿主内置', 'detail.added': '已添加', 'detail.notAdded': '未添加', 'detail.hostUnavailable': '尚未满足此宿主的使用验证条件',
  'detail.installed': '已安装', 'detail.applied': '已应用', 'detail.needsConfiguration': '需要配置',
  'action.add': '添加到宿主', 'action.install': '安装', 'action.apply': '应用', 'action.configure': '配置',
  'section.classification': '分类与用途', 'section.sourceRights': '原始来源与权利', 'section.verification': '验证状态', 'section.components': '插件组成', 'section.dependencies': '依赖', 'section.constraints': '适配限制', 'section.evidence': '核查文件与证据', 'section.runtimes': '运行环境',
  'source.original': '打开上游文件 ↗', 'source.location': '原始位置', 'source.path': '文件路径', 'source.selector': '选择器', 'source.version': '来源版本', 'source.relation': '来源关系', 'source.author': '作者', 'source.license': '许可', 'source.content': '内容来源', 'source.public': '公开来源', 'source.restricted': '受限来源', 'source.unknown': '访问状态未知', 'source.noLicense': '获取、安装或再分发前，请在来源确认许可范围与权利状态。', 'source.distribution': '打开分发来源 ↗', 'source.openFile': '查看文件 ↗', 'source.noTestedHost': '无', 'source.noCheckDate': '尚无检查日期',
  'source.archive': '来源档案', 'source.access': '访问状态', 'source.roles': '来源角色', 'source.openWebsite': '打开来源网站 ↗', 'source.tracking': '来源追踪', 'source.resources': '目录中的资源', 'source.noResources': '当前目录没有关联资源。', 'source.accessWarning': '来源访问受限或尚未确认公开。页面只展示已登记的公开元数据，不承诺来源内容可获取。',
  'source.acquisition': '获取入口', 'source.metadataDetails': '作者、许可与来源版本', 'source.verificationDetails': '验证详情', 'source.compatibilityDetails': '运行环境、依赖与限制',
  'template.framework': '内容与代码框架', 'template.examples': '参考示例（样式不属于模板）', 'template.pending': '文件角色待补充', 'template.independent': '上游框架与风格已独立', 'template.mixed': '上游框架与风格待拆分', 'template.unknown': '上游框架与风格关系未知', 'template.policy': '风格策略', 'template.policy.external-design-system': '由独立设计系统提供', 'template.note': '来源说明',
  'designSystem.files': '设计系统文件', 'designSystem.missing': '缺少核心文件角色：{roles}', 'designSystem.role.manifest': 'manifest.json', 'designSystem.role.rules': 'DESIGN.md / 设计规范', 'designSystem.role.tokens-css': 'tokens.css', 'designSystem.role.example': '示例', 'designSystem.role.support': '辅助文件',
  'fileRole.instructions': '操作指南', 'fileRole.framework': '框架文件', 'fileRole.example': '参考示例', 'fileRole.support': '辅助文件', 'category.definition': '分类定义',
  'source.viewResource': '查看关联资源 ↗', 'source.componentSource': '组件来源 ↗', 'source.hostProvided': '宿主提供 · 查看声明 ↗', 'source.type': '资源类别', 'source.testedHost': '检验宿主', 'source.verified': '已核实', 'source.reference': '来源引用', 'source.redistribution': '再分发', 'source.open': '打开',
};
type Translator = (key: string, fallback?: string) => string;
const TextContext = createContext<Translator>((_key, fallback) => fallback ?? _key);
function useText() { return useContext(TextContext); }
const LABELS: Record<string, string> = {
  reference: '仅供参考', candidate: '候选', usable: '可用', withdrawn: '已撤回',
  unverified: '未验证', 'source-inspected': '已检查来源', 'usage-tested': '已实测',
  contained: '随资源包含', referenced: '外部引用', 'host-provided': '由宿主提供',
};

function routeFromHash(hash: string): Route {
  const match = hash.match(/^#\/(resource|source)\/(.+)$/);
  if (!match) return { type: 'catalog' };
  let id = match[2] ?? '';
  try { id = decodeURIComponent(id); } catch { return { type: 'catalog' }; }
  return { type: match[1] as 'resource' | 'source', id };
}

function stableRoute(type: 'resource' | 'source', id: string) {
  return `#/${type}/${encodeURIComponent(id)}`;
}

function externalRawUrl(url: string) {
  return url.replace(/^https:\/\/github\.com\/([^/]+\/[^/]+)\/blob\/([^/]+)\/(.+)$/, 'https://raw.githubusercontent.com/$1/$2/$3');
}

function rawGithubPinnedRoot(url: string) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== 'raw.githubusercontent.com') return null;
    const [owner, repository, revision] = parsed.pathname.split('/').filter(Boolean);
    if (!owner || !repository || !revision || !/^[a-f0-9]{40}$/i.test(revision)) return null;
    return `${parsed.origin}/${owner}/${repository}/${revision}/`;
  } catch { return null; }
}

async function prepareHTMLPreview(html: string, sourceUrl: string) {
  if (typeof window === 'undefined' || !safeExternalUrl(sourceUrl)) return html;
  const parsed = new window.DOMParser().parseFromString(html, 'text/html');
  parsed.querySelectorAll('base').forEach((base) => base.remove());
  const base = parsed.createElement('base');
  const sourceDirectory = new URL('.', sourceUrl).href;
  base.href = sourceDirectory;
  parsed.head.insertBefore(base, parsed.head.firstChild);

  const pinnedRoot = rawGithubPinnedRoot(sourceUrl);
  if (pinnedRoot) {
    for (const link of parsed.querySelectorAll<HTMLLinkElement>('link[rel~="stylesheet"][href]')) {
      const href = link.getAttribute('href');
      if (!href) continue;
      const cssUrl = new URL(href, sourceDirectory);
      if (!cssUrl.href.startsWith(pinnedRoot)) continue;
      const response = await fetch(cssUrl.href);
      if (!response.ok) throw new Error(`${response.status} ${response.statusText} while loading preview stylesheet`);
      const style = parsed.createElement('style');
      style.dataset.sourceUrl = cssUrl.href;
      style.textContent = (await response.text()).replace(/</g, '\\3C ');
      link.replaceWith(style);
    }
  }

  const doctype = parsed.doctype ? `<!doctype ${parsed.doctype.name}>` : '';
  return `${doctype}${parsed.documentElement.outerHTML}`;
}

function safeExternalUrl(url: string) {
  try { return ['http:', 'https:'].includes(new URL(url).protocol); } catch { return false; }
}

function unique(values: Array<string | null | undefined>) {
  return [...new Set(values.filter((value): value is string => Boolean(value)))].sort((a, b) => a.localeCompare(b));
}

function human(value: string | null | undefined) {
  if (!value) return '';
  return LABELS[value] ?? value.replaceAll('-', ' ');
}

function linkButtonLabel(operation: string) {
  return ({ add: '添加到宿主', install: '安装', apply: '应用', configure: '配置' } as Record<string, string>)[operation] ?? operation;
}

export function CatalogApp({ catalog, host, status = catalog ? 'ready' : 'loading', error, locale, messages = {}, theme = 'system', accent, pageSize = 12, onRetry }: CatalogAppProps) {
  const [route, setRoute] = useState<Route>(() => typeof window === 'undefined' ? { type: 'catalog' } : routeFromHash(window.location.hash));
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [operationError, setOperationError] = useState('');
  const [previewState, setPreviewState] = useState<Record<string, 'loading' | 'error' | 'ready'>>({});
  const [previewText, setPreviewText] = useState<Record<string, string>>({});
  const resolveTheme = () => {
    if (theme !== 'system') return theme;
    const hostTheme = host?.theme.get();
    if (hostTheme && hostTheme !== 'system') return hostTheme;
    return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };
  const [themeValue, setThemeValue] = useState<'light' | 'dark'>(resolveTheme);

  useEffect(() => {
    const update = () => setRoute(routeFromHash(window.location.hash));
    window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, []);

  useEffect(() => {
    setThemeValue(resolveTheme());
  }, [theme, host]);

  const resources = catalog?.resources.resources ?? [];
  const categories = catalog?.categories.categories ?? [];
  const dimensions = catalog?.categories.dimensions;
  const sourceRecords = catalog?.sources.sources ?? [];
  const visibleCategories = categories;
  const selectedCategory = categories.find((item) => item.id === filters.category);
  const subtypeOptions = selectedCategory?.subtypes ?? [];
  const domainOptions = dimensions?.domains ?? [];
  const filtered = useMemo(() => catalog ? filterResources(catalog, filters) : [], [catalog, filters]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / Math.max(1, pageSize)));
  const safePage = Math.min(page, pageCount);
  const pageResources = filtered.slice((safePage - 1) * pageSize, safePage * pageSize);
  const resource = route.type === 'resource' && catalog ? getResource(catalog, route.id) : undefined;
  const source = route.type === 'source' ? sourceRecords.find((item) => item.id === route.id) : undefined;
  const t: Translator = (key, fallback = '') => {
    if (messages[key] !== undefined) return messages[key]!;
    const translated = host?.i18n.translate(key);
    if (translated && translated !== key) return translated;
    return DEFAULT_MESSAGES[key] ?? fallback;
  };

  function hostLink(event: React.MouseEvent<HTMLAnchorElement>, url: string) {
    if (!host) return;
    event.preventDefault();
    host.links.open(url);
  }

  function setFilter<K extends keyof Filters>(key: K, value: Filters[K]) {
    setPage(1);
    setFilters((previous) => ({ ...previous, [key]: value }));
  }

  function selectCategory(category: string) {
    setPage(1);
    setFilters((previous) => ({ ...previous, category, subtype: '' }));
    if (route.type !== 'catalog') {
      setRoute({ type: 'catalog' });
      if (typeof window !== 'undefined') window.location.hash = '#/';
    }
  }

  async function runOperation(action: 'add' | 'install' | 'apply' | 'configure', item: Resource) {
    if (!host || item.lifecycle.state === 'withdrawn') return;
    setOperationError('');
    try { await host.operations[action](item); }
    catch (cause) { setOperationError(cause instanceof Error ? cause.message : String(cause)); }
  }

  async function loadPreview(item: Resource, index: number, preview: Resource['previews'][number]) {
    const key = `${item.id}:${index}`;
    setPreviewState((previous) => ({ ...previous, [key]: 'loading' }));
    try {
      const url = externalRawUrl(preview.url);
      if (!safeExternalUrl(url)) throw new Error('Unsupported preview URL');
      const response = await fetch(url);
      if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
      const body = await response.text();
      const content = preview.kind.toLowerCase() === 'html' || /\.html?(?:\?|$)/i.test(url)
        ? await prepareHTMLPreview(body, url)
        : body;
      setPreviewText((previous) => ({ ...previous, [key]: content }));
      setPreviewState((previous) => ({ ...previous, [key]: 'ready' }));
    } catch (cause) {
      setPreviewState((previous) => ({ ...previous, [key]: 'error' }));
      setOperationError(`预览读取失败：${cause instanceof Error ? cause.message : String(cause)}`);
    }
  }

  const rootStyle = { '--catalog-accent': accent ?? 'var(--pas-accent-default)' } as React.CSSProperties;
  return <TextContext.Provider value={t}><div className="pas-app" data-theme={themeValue} data-locale={locale ?? host?.i18n.locale} style={rootStyle}>
    <a className="pas-skip-link" href="#main-content">{t('skip.main', '跳到主要内容')}</a>
    <div className="pas-layout">
      <aside className="pas-sidebar">
        <a className="pas-brand" href="#/" aria-label={t('brand', 'Agent 资源目录')}>
          <span className="pas-brand-mark" aria-hidden="true">A</span><span>{t('brand', 'Agent 资源目录')}</span>
        </a>
        <nav aria-label={t('categories.title', '资源类别')} className="pas-category-nav">
          <p className="pas-eyebrow">{t('categories.title', '资源类别')}</p>
          <button type="button" data-category="" aria-pressed={!filters.category} onClick={() => selectCategory('')}>{t('category.all', '全部资源')} <span>{resources.length}</span></button>
          {visibleCategories.map((category) => <button key={category.id} type="button" data-category={category.id} aria-pressed={filters.category === category.id} onClick={() => selectCategory(category.id)}>
            {t(`category.${category.id}`, category.label)}<span>{resources.filter((item) => item.classification.category === category.id).length}</span>
          </button>)}
        </nav>
        <div className="pas-sidebar-foot"><span className="pas-status-dot" />{t('catalog.traceable', '来源和状态可追溯')}</div>
      </aside>

      <main id="main-content" className="pas-main">
        <header className="pas-topbar">
          <div><p className="pas-eyebrow">{t('catalog.eyebrow', 'PUBLIC RESOURCE CATALOG')}</p><h1>{t('page.title', 'Agent 创作资源')}</h1></div>
          <div className="pas-top-actions">
            <label className="pas-theme-label" htmlFor="theme-select">{t('theme.label', '界面主题')}</label>
            <select id="theme-select" value={themeValue} onChange={(event) => {
              const next = event.target.value as 'light' | 'dark'; setThemeValue(next); host?.theme.set(next);
            }}><option value="light">{t('theme.light', '浅色')}</option><option value="dark">{t('theme.dark', '深色')}</option></select>
          </div>
        </header>

        {status === 'loading' && <div className="pas-state" role="status">{t('state.loading', '正在加载资源目录…')}</div>}
        {status === 'error' && <div className="pas-state pas-state-error" role="alert">{t('state.error', `目录加载失败：${error ?? '请稍后重试'}`).replace('{error}', error ?? '请稍后重试')}{onRetry && <button type="button" onClick={onRetry}>{t('state.retry', '重试')}</button>}</div>}
        {status === 'ready' && !catalog && <div className="pas-state pas-state-error" role="alert">{t('state.unavailable', '资源目录不可用')}</div>}

        {status === 'ready' && catalog && route.type === 'source' && <SourceDetail source={source} catalog={catalog} />}
        {status === 'ready' && catalog && route.type === 'resource' && <>
          {resource ? <ResourceDetail resource={resource} sourceRecords={sourceRecords} host={host} availableForHost={Boolean(host && isAvailableForHost(catalog, resource.id, host.hostId))} catalog={catalog} operationError={operationError} onOperation={runOperation} onLoadPreview={loadPreview} previewState={previewState} previewText={previewText} onHostLink={hostLink} />
            : <div className="pas-state" role="status">{t('detail.notFound', '找不到这个资源。')}<a href="#/">{t('detail.back', '返回目录')}</a></div>}
        </>}

        {status === 'ready' && catalog && route.type === 'catalog' && <>
          <section className="pas-intro">
            <p>{t('catalog.intro', '从公开来源发现的模板、设计系统、Skills、提示词和插件，按真实来源与验证状态浏览。')}</p>
            <div className="pas-catalog-meta"><span>{t('resource.count', '{count} 项资源').replace('{count}', String(resources.length))}</span><span>{t('catalog.version', `目录版本 ${catalog.resources.meta.catalog_version}`).replace('{version}', catalog.resources.meta.catalog_version)}</span><span>{t('catalog.updated', `更新于 ${catalog.resources.meta.updated}`).replace('{date}', catalog.resources.meta.updated)}</span></div>
          </section>
          <section className="pas-controls" aria-label="目录筛选">
            <label className="pas-search"><span className="pas-search-icon" aria-hidden="true">⌕</span><span className="pas-visually-hidden">{t('search.label', '搜索资源')}</span>
              <input type="search" aria-label={t('search.label', '搜索资源')} placeholder={t('search.placeholder', '搜索名称、用途或简介…')} value={filters.query} onInput={(event) => setFilter('query', event.currentTarget.value)} />
            </label>
            <div className="pas-filter-grid">
              <FilterSelect label={t('filter.subtype', '子类型')} name="subtype" value={filters.subtype} options={subtypeOptions.map((item) => [item.id, item.label])} onChange={(value) => setFilter('subtype', value)} />
              <FilterSelect label={t('filter.domain', '领域')} name="domain" value={filters.domain} options={domainOptions.map((item) => [item.id, item.label])} onChange={(value) => setFilter('domain', value)} />
              <FilterSelect label={t('filter.source', '来源')} name="source" value={filters.source} options={unique(resources.map((item) => item.provenance.content_source)).map((id) => [id, sourceRecords.find((item) => item.id === id)?.name ?? id])} onChange={(value) => setFilter('source', value)} />
              <FilterSelect label={t('filter.verification', '验证')} name="verification" value={filters.verification} options={unique(resources.map((item) => item.verification.level)).map((id) => [id, t(`verification.${id}`, human(id))])} onChange={(value) => setFilter('verification', value)} />
              <FilterSelect label={t('filter.lifecycle', '生命周期')} name="lifecycle" value={filters.lifecycle} options={unique(resources.map((item) => item.lifecycle.state)).map((id) => [id, t(`lifecycle.${id}`, human(id))])} onChange={(value) => setFilter('lifecycle', value)} />
            </div>
          </section>
          <div className="pas-result-heading"><div><h2>{filters.category ? t(`category.${filters.category}`, categories.find((item) => item.id === filters.category)?.label ?? filters.category) : t('result.all', '全部资源')}</h2><span>{t('result.count', '{count} 项结果').replace('{count}', String(filtered.length))}</span>{selectedCategory?.definition && <p className="pas-category-definition"><b>{t('category.definition', '分类定义')}</b> {selectedCategory.definition}</p>}</div>
            {Object.values(filters).some(Boolean) && <button className="pas-text-button" type="button" onClick={() => { setFilters(EMPTY_FILTERS); setPage(1); }}>{t('filter.clear', '清除筛选')}</button>}
          </div>
          {filtered.length === 0 ? <div className="pas-state">{t('result.empty', '没有符合条件的资源。')}<button type="button" onClick={() => setFilters(EMPTY_FILTERS)}>{t('filter.clear', '清除筛选')}</button></div> : <>
            <div className="pas-resource-grid">
              {pageResources.map((item) => <ResourceCard key={item.id} resource={item} categories={categories} onLinkClick={hostLink} />)}
            </div>
            {pageCount > 1 && <nav className="pas-pagination" aria-label="资源分页">
              <button type="button" disabled={safePage <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>{t('page.previous', '上一页')}</button>
              <span>{t('page.current', `第 ${safePage} / ${pageCount} 页`).replace('{page}', String(safePage)).replace('{count}', String(pageCount))}</span>
              <button type="button" disabled={safePage >= pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>{t('page.next', '下一页')}</button>
            </nav>}
          </>}
        </>}
      </main>
    </div>
  </div></TextContext.Provider>;
}

function FilterSelect({ label, name, value, options, onChange }: { label: string; name: string; value: string; options: [string, string][]; onChange: (value: string) => void }) {
  const t = useText();
  return <label className="pas-filter"><span>{label}</span><select name={name} value={value} onChange={(event) => onChange(event.target.value)}><option value="">{t('filter.all', '全部')}</option>{options.map(([id, text]) => <option key={id} value={id}>{text}</option>)}</select></label>;
}

function isImagePreview(preview: Resource['previews'][number]) {
  return ['image', 'carousel', 'screenshot'].includes(preview.kind.toLowerCase()) || /\.(png|jpe?g|webp|gif)(?:\?|$)/i.test(preview.url);
}

function ProfileFileList({ files, onHostLink }: { files: ProfileFile[]; onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const t = useText();
  return <ul className="pas-profile-files">{files.map((file) => <li key={`${file.role}:${file.path}:${file.url}`}>
    <span>{t(`fileRole.${file.role}`, human(file.role))}</span><code>{file.path}</code>
    {safeExternalUrl(file.url) ? <a href={file.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, file.url)}>{t('source.openFile', '查看文件 ↗')}</a> : <span>{t('source.invalidLink', '无法打开此来源地址')}</span>}
  </li>)}</ul>;
}

function TemplateProfile({ profile, onHostLink }: { profile?: TemplateProfile; onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const t = useText();
  if (!profile) return <MetaSection title={t('template.framework', '内容与代码框架')}><p>{t('template.pending', '文件角色待补充')}</p></MetaSection>;
  const frameworkFiles = profile.files.filter((file) => file.role !== 'example');
  const examples = profile.files.filter((file) => file.role === 'example');
  const statusKey = `template.${profile.style.upstream_status}`;
  const statusLabel = t(statusKey, profile.style.upstream_status === 'mixed' ? '上游框架与风格待拆分' : profile.style.upstream_status === 'independent' ? '上游框架与风格已独立' : '上游框架与风格关系未知');
  return <section className="pas-profile-section" data-template-profile>
    <MetaSection title={t('template.framework', '内容与代码框架')}>
      {frameworkFiles.length ? <ProfileFileList files={frameworkFiles} onHostLink={onHostLink} /> : <p>{t('template.pending', '文件角色待补充')}</p>}
      <p><b>{t('template.policy', '风格策略')}</b> {t(`template.policy.${profile.style.policy}`, human(profile.style.policy))}</p>
      <p><b>{statusLabel}</b></p>
      {profile.style.note && <p><b>{t('template.note', '来源说明')}</b> {profile.style.note}</p>}
    </MetaSection>
    {examples.length > 0 && <MetaSection title={t('template.examples', '参考示例（样式不属于模板）')}><ProfileFileList files={examples} onHostLink={onHostLink} /></MetaSection>}
  </section>;
}

function DesignSystemProfile({ profile, onHostLink }: { profile?: DesignSystemProfile; onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const t = useText();
  const coreRoles = ['manifest', 'rules', 'tokens-css'];
  const files = profile?.files ?? [];
  const missing = coreRoles.filter((role) => !files.some((file) => file.role === role));
  return <MetaSection title={t('designSystem.files', '设计系统文件')}>
    {files.length ? <ProfileFileList files={files} onHostLink={onHostLink} /> : <p>{t('template.pending', '文件角色待补充')}</p>}
    {missing.length > 0 && <p className="pas-profile-missing">{t('designSystem.missing', '缺少核心文件角色：{roles}').replace('{roles}', missing.map((role) => t(`designSystem.role.${role}`, role)).join('、'))}</p>}
  </MetaSection>;
}

function ImageCarousel({ resource, previews, onHostLink }: { resource: Resource; previews: Resource['previews']; onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const [index, setIndex] = useState(0);
  const [mediaError, setMediaError] = useState(false);
  const current = previews[index]!;
  const url = externalRawUrl(current.url);
  const t = useText();
  return <section className="pas-gallery" aria-label={t('preview.gallery', `${resource.title} 图片轮播`).replace('{title}', resource.title)}>
    <div className="pas-gallery-stage">
      <button type="button" aria-label={t('preview.previous', '上一张')} onClick={() => { setIndex((value) => (value + previews.length - 1) % previews.length); setMediaError(false); }}>‹</button>
      {mediaError || !safeExternalUrl(url) ? <p className="pas-inline-error" role="alert">{t('preview.mediaFailed', '媒体加载失败，请打开原始来源。')}</p> : <a href={url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, url)}><img src={url} alt={t('preview.image', `${resource.title} 图片 ${index + 1}`).replace('{title}', resource.title).replace('{number}', String(index + 1))} onError={() => setMediaError(true)} /></a>}
      <button type="button" aria-label={t('preview.next', '下一张')} onClick={() => { setIndex((value) => (value + 1) % previews.length); setMediaError(false); }}>›</button>
    </div>
    <p role="status">{t('preview.imageCount', '{number} / {count}').replace('{number}', String(index + 1)).replace('{count}', String(previews.length))} · {current.status === 'verified' ? t('source.verified', '已核实') : t('source.reference', '来源引用')}</p>
    <a href={url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, url)}>{t('preview.openSource', '查看原始来源 ↗')}</a>
  </section>;
}

function ResourceCard({ resource, categories, onLinkClick }: { resource: Resource; categories: Catalog['categories']['categories']; onLinkClick: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const t = useText();
  const preview = resource.previews.find((item) => isImagePreview(item) && safeExternalUrl(item.url));
  return <article className="pas-card" data-resource-card data-resource-id={resource.id} data-category={resource.classification.category}>
    <div className="pas-card-top">{preview ? <a className="pas-card-image" href={externalRawUrl(preview.url)} target="_blank" rel="noreferrer" onClick={(event) => onLinkClick(event, preview.url)} aria-label={`打开 ${resource.title} 预览`}><img src={externalRawUrl(preview.url)} alt="" loading="lazy" /></a> : <span className={`pas-type-mark pas-type-${resource.classification.category}`} aria-hidden="true">{resource.classification.category.slice(0, 1).toUpperCase()}</span>}
      <div className="pas-card-tags"><span className="pas-pill">{t(`category.${resource.classification.category}`, categories.find((item) => item.id === resource.classification.category)?.label ?? human(resource.classification.category))}</span><span className="pas-pill pas-muted-pill">{t(`lifecycle.${resource.lifecycle.state}`, human(resource.lifecycle.state))}</span></div>
    </div>
    <h3><a href={stableRoute('resource', resource.id)}>{resource.title}</a></h3>
    <p className="pas-card-summary">{resource.summary}</p>
    <div className="pas-card-meta"><span>{resource.provenance.content_source}</span><span>{t(`verification.${resource.verification.level}`, human(resource.verification.level))}</span></div>
  </article>;
}

function ResourceDetail({ resource, sourceRecords, host, availableForHost, catalog, operationError, onOperation, onLoadPreview, previewState, previewText, onHostLink }: {
  resource: Resource; sourceRecords: Catalog['sources']['sources']; host?: HostAdapter; availableForHost: boolean; catalog: Catalog; operationError: string;
  onOperation: (action: 'add' | 'install' | 'apply' | 'configure', resource: Resource) => Promise<void>;
  onLoadPreview: (resource: Resource, index: number, preview: Resource['previews'][number]) => Promise<void>;
  previewState: Record<string, 'loading' | 'error' | 'ready'>; previewText: Record<string, string>;
  onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void;
}) {
  const t = useText();
  const [assetState, setAssetState] = useState<{ added: boolean; installed: boolean; applied: boolean; builtIn: boolean; requiresConfiguration: boolean } | null>(null);
  const [accountState, setAccountState] = useState<'signed-in' | 'signed-out' | 'loading' | 'error'>('loading');
  const [hostStatusError, setHostStatusError] = useState('');
  const [accountError, setAccountError] = useState('');
  useEffect(() => {
    let current = true;
    if (host) Promise.all([host.assetStatus(resource.id), host.account.status()]).then(([state, account]) => {
      if (current) { setAssetState(state); setAccountState(account); setHostStatusError(''); }
    }).catch((cause: unknown) => {
      if (current) { setAssetState(null); setAccountState('error'); setHostStatusError(`宿主状态读取失败：${cause instanceof Error ? cause.message : String(cause)}`); }
    });
    return () => { current = false; };
  }, [host, resource.id]);
  const category = resource.classification.category;
  const categoryLabel = t(`category.${category}`, catalog.categories.categories.find((item) => item.id === category)?.label ?? human(category));
  const subtypeLabel = resource.classification.subtype ? t(`subtype.${resource.classification.subtype}`, catalog.categories.categories.find((item) => item.id === category)?.subtypes.find((item) => item.id === resource.classification.subtype)?.label ?? human(resource.classification.subtype)) : '';
  const domainLabel = (id: string) => t(`domain.${id}`, catalog.categories.dimensions.domains.find((item) => item.id === id)?.label ?? human(id));
  const formatLabel = (id: string) => t(`format.${id}`, catalog.categories.dimensions.formats.find((item) => item.id === id)?.label ?? human(id));
  const componentTypeLabel = (id: string) => t(`component.${id}`, catalog.categories.dimensions.plugin_component_types.find((item) => item.id === id)?.label ?? human(id));
  const withdrawn = resource.lifecycle.state === 'withdrawn';
  async function login() {
    if (!host) return;
    setAccountError('');
    try { await host.account.login(); setAccountState(await host.account.status()); }
    catch (cause) { setAccountError(cause instanceof Error ? cause.message : String(cause)); }
  }
  const canInstall = availableForHost && !assetState?.installed && !withdrawn;
  const canApply = availableForHost && !assetState?.applied && !withdrawn;
  const canConfigure = Boolean(assetState?.requiresConfiguration) && !withdrawn;
  async function invokeOperation(action: 'add' | 'install' | 'apply' | 'configure') {
    await onOperation(action, resource);
    if (!host) return;
    try {
      const [nextAsset, nextAccount] = await Promise.all([host.assetStatus(resource.id), host.account.status()]);
      setAssetState(nextAsset);
      setAccountState(nextAccount);
    } catch (cause) { setHostStatusError(`宿主状态读取失败：${cause instanceof Error ? cause.message : String(cause)}`); }
  }
  const source = sourceRecords.find((item) => item.id === resource.provenance.content_source);
  const templateProfile = resource.template;
  const designSystemProfile = resource.design_system;
  const profiledUrls = new Set([...(templateProfile?.files ?? []), ...(designSystemProfile?.files ?? [])].map((file) => file.url));
  const detailPreviews = [...resource.previews];
  const sourceFileEvidence = resource.verification.evidence.map((item) => item.locator);
  const sourceFiles = [resource.provenance.upstream.url, ...sourceFileEvidence]
    .filter((url): url is string => Boolean(url) && !profiledUrls.has(url) && safeExternalUrl(url) && /\.(md|markdown|json|css)(?:\?|$)/i.test(url));
  if (['skills', 'prompts', 'design-systems'].includes(category)) {
    for (const url of sourceFiles) {
      if (detailPreviews.some((item) => item.url === url)) continue;
      const extension = new URL(url).pathname.split('.').pop()?.toLowerCase();
      const kind = extension === 'css' ? 'css' : extension === 'json' ? 'json' : 'markdown';
      detailPreviews.push({ kind, url, status: 'reference', evidence: [] });
    }
  }
  const imagePreviews = detailPreviews.filter(isImagePreview);
  const listedPreviews = imagePreviews.length > 1 ? detailPreviews.filter((preview) => !isImagePreview(preview)) : detailPreviews;
  return <article data-resource-detail className="pas-detail">
    <a className="pas-back-link" href="#/">{t('detail.back', '← 返回资源目录')}</a>
    <header className="pas-detail-heading"><div><p className="pas-eyebrow">{categoryLabel}{subtypeLabel ? ` / ${subtypeLabel}` : ''}</p>
      <h2>{resource.title}</h2><p className="pas-detail-summary">{resource.purpose || resource.summary}</p></div>
      <div className="pas-detail-badges"><span className={`pas-lifecycle pas-lifecycle-${resource.lifecycle.state}`}>{t(`lifecycle.${resource.lifecycle.state}`, human(resource.lifecycle.state))}</span>
        <span className="pas-verification-badge" data-verification-badge>{t(`verification.${resource.verification.level}`, human(resource.verification.level))}</span>
      </div>
    </header>
    {resource.lifecycle.state === 'withdrawn' && <div className="pas-notice" role="status"><strong>{t('detail.withdrawn', '此资源已撤回')}</strong><p>{resource.lifecycle.reason}</p></div>}
    {host && !withdrawn && <div className="pas-host-actions" aria-label={t('detail.hostActions', '宿主操作')}>
      <span className="pas-host-state">{accountState === 'signed-in' ? (assetState?.builtIn ? t('detail.builtIn', '宿主内置') : assetState?.added ? t('detail.added', '已添加') : t('detail.notAdded', '未添加')) : accountState === 'signed-out' ? t('detail.notSignedIn', '未登录') : accountState === 'loading' ? t('detail.hostLoading', '读取宿主状态…') : hostStatusError}
        {assetState?.installed && <span className="pas-state-chip">{t('detail.installed', '已安装')}</span>}
        {assetState?.applied && <span className="pas-state-chip">{t('detail.applied', '已应用')}</span>}
        {assetState?.requiresConfiguration && <span className="pas-state-chip">{t('detail.needsConfiguration', '需要配置')}</span>}
      </span>
      {accountState === 'signed-out' ? <button type="button" data-action="login" onClick={() => void login()}>{t('detail.signIn', '登录宿主')}</button> : <>
        <button type="button" data-action="add" disabled={accountState !== 'signed-in' || assetState?.added || assetState?.builtIn} onClick={() => void invokeOperation('add')}>{t('action.add', linkButtonLabel('add'))}</button>
        {canInstall && <button type="button" data-action="install" disabled={accountState !== 'signed-in'} onClick={() => void invokeOperation('install')}>{t('action.install', linkButtonLabel('install'))}</button>}
        {canApply && <button type="button" data-action="apply" disabled={accountState !== 'signed-in'} onClick={() => void invokeOperation('apply')}>{t('action.apply', linkButtonLabel('apply'))}</button>}
        {canConfigure && <button type="button" data-action="configure" disabled={accountState !== 'signed-in'} onClick={() => void invokeOperation('configure')}>{t('action.configure', linkButtonLabel('configure'))}</button>}
      </>}
      {accountState === 'signed-in' && !availableForHost && !assetState?.installed && <span className="pas-host-availability">{t('detail.hostUnavailable', '尚未满足此宿主的使用验证条件')}</span>}
    </div>}
    {(hostStatusError || accountError) && <p className="pas-inline-error" role="alert">{accountError || hostStatusError}</p>}
    {operationError && <p className="pas-inline-error" role="alert">{operationError}</p>}
    {category === 'templates' && <TemplateProfile profile={templateProfile} onHostLink={onHostLink} />}
    {category === 'design-systems' && <DesignSystemProfile profile={designSystemProfile} onHostLink={onHostLink} />}
    <section className="pas-preview-section"><div className="pas-section-title"><div><p className="pas-eyebrow">{t('preview.eyebrow', '预览与来源文件')}</p><h3>{category === 'templates' ? t('template.examples', '参考示例（样式不属于模板）') : t('preview.title', '资源内容')}</h3></div>{detailPreviews.length > 0 && <span>{detailPreviews.length} 个来源条目</span>}</div>
      {imagePreviews.length > 1 && <ImageCarousel resource={resource} previews={imagePreviews} onHostLink={onHostLink} />}
      {detailPreviews.length === 0 ? <div className="pas-preview-empty">{t('preview.empty', '暂无可内嵌预览；请使用下方原始来源入口。')}</div> : listedPreviews.length > 0 && <div className="pas-preview-list">{listedPreviews.map((preview) => {
        const index = detailPreviews.indexOf(preview);
        return <Preview key={`${preview.url}-${index}`} resource={resource} preview={preview} index={index} state={previewState[`${resource.id}:${index}`]} text={previewText[`${resource.id}:${index}`]} onLoad={() => void onLoadPreview(resource, index, preview)} onHostPreview={host ? () => host.preview.open(resource, preview.url) : undefined} onHostLink={onHostLink} />;
      })}</div>}
    </section>
    <section className="pas-detail-grid">
      <div className="pas-detail-main"><MetaSection title={t('section.classification', '分类与用途')}><p>{resource.summary}</p><p>{resource.purpose}</p><p><b>{t('field.domains', '领域')}</b> {resource.classification.domains.map(domainLabel).join(' · ')}</p><p><b>{t('field.formats', '格式')}</b> {resource.classification.formats.map(formatLabel).join(' · ')}</p></MetaSection>
        <MetaSection title={t('section.sourceRights', '原始来源与获取')}>
          <p><b>{t('source.content', '内容来源')}</b> <a href={stableRoute('source', resource.provenance.content_source)}>{source?.name ?? resource.provenance.content_source}</a>{source && ` · ${source.access === 'public' ? t('source.public', '公开来源') : source.access === 'restricted' ? t('source.restricted', '受限来源') : t('source.unknown', '访问状态未知')}`}</p>
          <div className="pas-acquisition"><b>{t('source.acquisition', '获取入口')}</b>
            {resource.distribution.length > 0 ? <ul className="pas-link-list">{resource.distribution.map((item) => <li key={`${item.kind}-${item.url}`}>{safeExternalUrl(item.url) ? <a href={item.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, item.url)}>{t('source.distribution', '打开分发来源 ↗')}</a> : <span>{t('source.invalidLink', '无法打开此来源地址')}</span>}<span>{item.kind}</span></li>)}</ul>
              : resource.provenance.upstream.url && safeExternalUrl(resource.provenance.upstream.url) ? <p><a href={resource.provenance.upstream.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, resource.provenance.upstream.url)}>{t('source.original', '打开上游文件 ↗')}</a></p> : <p>{t('source.noAcquisitionLink', '暂无公开获取链接')}</p>}
          </div>
          {source && source.access !== 'public' && <p className="pas-caution">{t('source.accessWarning', '来源访问受限或尚未确认公开。页面只展示已登记的公开元数据，不承诺来源内容可获取。')}</p>}
          {(resource.license.status !== 'verified' || resource.license.redistribution !== 'allowed') && <p className="pas-caution">{t('source.noLicense', '获取、安装或再分发前，请在来源确认许可范围与权利状态。')} · {t(`redistribution.${resource.license.redistribution}`, resource.license.redistribution)}</p>}
          <DisclosureSection id="source-metadata" title={t('source.metadataDetails', '作者、许可与来源版本')}>
            {resource.provenance.upstream.url && safeExternalUrl(resource.provenance.upstream.url) && <p><b>{t('source.location', '原始位置')}</b> <a href={resource.provenance.upstream.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, resource.provenance.upstream.url)}>{t('source.original', '打开上游文件 ↗')}</a></p>}
            {resource.provenance.upstream.path && <p><b>{t('source.path', '文件路径')}</b> {resource.provenance.upstream.path}</p>}
            {resource.provenance.upstream.selector && <p><b>{t('source.selector', '选择器')}</b> {resource.provenance.upstream.selector}</p>}
            {resource.provenance.upstream.ref.value && <p><b>{t('source.version', '来源版本')}</b> {resource.provenance.upstream.ref.kind}: {resource.provenance.upstream.ref.value}</p>}
            <p><b>{t('source.relation', '来源关系')}</b> {t(`relation.${resource.provenance.relation}`, human(resource.provenance.relation))}{resource.provenance.changes && ` · ${resource.provenance.changes}`}</p>
            <p><b>{t('source.author', '作者')}</b> {resource.authors.identities.length ? resource.authors.identities.map((person, index) => <React.Fragment key={`${person.name}-${index}`}>{index > 0 && ' · '}{person.url && safeExternalUrl(person.url) ? <a href={person.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, person.url!)}>{person.name}</a> : person.name}</React.Fragment>) : t('source.unknown', '未知')}</p>
            <p><b>{t('source.license', '许可')}</b> {resource.license.expression ?? t('source.unknown', '未知')} · {t('source.redistribution', '再分发')}：{t(`redistribution.${resource.license.redistribution}`, resource.license.redistribution)}</p>
            {resource.license.scope && <p>{resource.license.scope}</p>}
            {resource.license.evidence.length > 0 && <ul>{resource.license.evidence.map((item, index) => <li key={`${item.locator}-${index}`}>{item.claim}{/^https?:\/\//i.test(item.locator) && <> · <a href={item.locator} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, item.locator)}>{t('source.openFile', '查看文件 ↗')}</a></>}</li>)}</ul>}
          </DisclosureSection>
        </MetaSection>
      </div>
      <aside className="pas-detail-aside"><DisclosureSection id="verification-details" title={t('source.verificationDetails', '验证详情')}>
          <MetaSection title={t('section.verification', '验证状态')}><p>{resource.verification.checked_at ? `${t('field.checkedAt', '检查日期')}：${resource.verification.checked_at}` : t('source.noCheckDate', '尚无检查日期')}</p>
            <p><b>{t('source.testedHost', '检验宿主')}</b> {resource.verification.tested_hosts.join(' · ') || t('source.noTestedHost', '无')}</p>
            {resource.verification.limits.length > 0 && <ul>{resource.verification.limits.map((item) => <li key={item}>{item}</li>)}</ul>}
          </MetaSection>
          {resource.verification.evidence.length > 0 && <MetaSection title={t('section.evidence', '核查文件与证据')}><ul className="pas-link-list">{resource.verification.evidence.map((item, index) => <li key={`${item.locator}-${index}`}><span>{item.claim}</span>{/^https?:\/\//i.test(item.locator) && <a href={item.locator} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, item.locator)}>{t('source.openFile', '查看文件 ↗')}</a>}</li>)}</ul></MetaSection>}
        </DisclosureSection>
        {(resource.compatibility.runtimes.length > 0 || resource.compatibility.dependencies.length > 0 || resource.compatibility.constraints.length > 0) && <DisclosureSection id="compatibility-details" title={t('source.compatibilityDetails', '运行环境、依赖与限制')}>
          {resource.compatibility.runtimes.length > 0 && <MetaSection title={t('section.runtimes', '运行环境')}><ul>{resource.compatibility.runtimes.map((runtime) => <li key={`${runtime.name}-${runtime.version ?? ''}`}>{runtime.name}{runtime.version ? ` ${runtime.version}` : ''} · {t(`runtime.${runtime.status}`, human(runtime.status))}</li>)}</ul></MetaSection>}
          {resource.compatibility.dependencies.length > 0 && <MetaSection title={t('section.dependencies', '依赖')}><ul>{resource.compatibility.dependencies.map((dep) => <li key={`${dep.kind}:${dep.name}`}>{dep.name}{dep.version ? ` ${dep.version}` : ''}{dep.source_id && <> · <a href={stableRoute('source', dep.source_id)}>{t('source.archive', '来源')}</a></>}</li>)}</ul></MetaSection>}
          {resource.compatibility.constraints.length > 0 && <MetaSection title={t('section.constraints', '适配限制')}><ul>{resource.compatibility.constraints.map((item) => <li key={item}>{item}</li>)}</ul></MetaSection>}
        </DisclosureSection>}
        {resource.components.length > 0 && <MetaSection title={t('section.components', '插件组成')}><ul className="pas-component-list">{resource.components.map((component) => <li key={component.id}><b>{component.id}</b><span>{t(`delivery.${component.delivery}`, human(component.delivery))}</span><small>{componentTypeLabel(component.type)}{component.subtype ? ` · ${human(component.subtype)}` : ''}</small>{component.resource_id && <a href={stableRoute('resource', component.resource_id)}>{t('source.viewResource', '查看关联资源 ↗')}</a>}{component.upstream.url && safeExternalUrl(component.upstream.url) && <a href={component.upstream.url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, component.upstream.url)}>{component.delivery === 'host-provided' ? t('source.hostProvided', '宿主提供 · 查看声明 ↗') : t('source.componentSource', '组件来源 ↗')}</a>}</li>)}</ul></MetaSection>}
        {resource.compatibility.constraints.length > 0 && <MetaSection title={t('section.constraints', '适配限制')}><ul>{resource.compatibility.constraints.map((item) => <li key={item}>{item}</li>)}</ul></MetaSection>}
      </aside>
    </section>
  </article>;
}

function Preview({ resource, preview, index, state, text, onLoad, onHostPreview, onHostLink }: { resource: Resource; preview: Resource['previews'][number]; index: number; state?: 'loading' | 'error' | 'ready'; text?: string; onLoad: () => void; onHostPreview?: () => void; onHostLink: (event: React.MouseEvent<HTMLAnchorElement>, url: string) => void }) {
  const t = useText();
  const [mediaError, setMediaError] = useState(false);
  const url = externalRawUrl(preview.url);
  const kind = preview.kind.toLowerCase();
  const isImage = ['image', 'carousel', 'screenshot'].includes(kind) || /\.(png|jpe?g|webp|gif)(?:\?|$)/i.test(url);
  const isVideo = kind === 'video' || /\.mp4(?:\?|$)/i.test(url);
  const isHtml = kind === 'html' || /\.html?(?:\?|$)/i.test(url);
  const isText = ['text', 'markdown', 'skill', 'prompt', 'design-md', 'json', 'css'].includes(kind) || /\.(md|txt|json|css)(?:\?|$)/i.test(url);
  const externalNotice = <p className="pas-external-note">{t('preview.external', '预览来自外部来源，浏览器会向该来源请求内容。预览状态：{status}。').replace('{status}', preview.status === 'verified' ? t('source.verified', '已核实') : t('source.reference', '来源引用'))}</p>;
  return <article className="pas-preview-card"><div className="pas-preview-title"><span>{human(kind)}</span><span>{preview.status === 'verified' ? '已核实' : '引用'}</span></div>
    {isImage && safeExternalUrl(url) && !mediaError && <a href={url} target="_blank" rel="noreferrer" aria-label={t('preview.openImage', `打开 ${resource.title} 的图片预览`).replace('{title}', resource.title)} onClick={(event) => onHostLink(event, url)}><img src={url} alt={t('preview.imageAlt', `${resource.title} 外部预览`).replace('{title}', resource.title)} loading="lazy" onError={() => setMediaError(true)} /></a>}
    {isVideo && safeExternalUrl(url) && !mediaError && <video controls preload="none" src={url} onError={() => setMediaError(true)}><track kind="captions" /></video>}
    {mediaError && <p className="pas-inline-error" role="alert">{t('preview.mediaFailed', '媒体加载失败，请打开原始来源。')}</p>}
    {(isHtml || isText) && <>
      {state === 'ready' && isHtml && <iframe title={`${resource.title} 隔离预览 ${index + 1}`} sandbox="allow-scripts" referrerPolicy="no-referrer" srcDoc={text ?? ''} />}
      {state === 'ready' && isText && <pre className="pas-source-text">{text}</pre>}
      {state !== 'ready' && <button type="button" data-preview-load={kind} disabled={state === 'loading'} onClick={onLoad}>{state === 'loading' ? t('preview.loading', '正在读取…') : isHtml ? t('preview.readHtml', '加载隔离预览') : t('preview.readText', '读取来源文本')}</button>}
      {state === 'error' && <p className="pas-inline-error" role="alert">{t('preview.failed', '读取失败。你可以直接打开原始来源。')}</p>}
    </>}
    {!isImage && !isVideo && !isHtml && !isText && <p>{t('preview.unsupported', '当前不支持此预览格式。')}</p>}
    {externalNotice}
    {onHostPreview && <button type="button" onClick={onHostPreview}>{t('preview.openHost', '在宿主中打开预览')}</button>}
    {safeExternalUrl(url) && <a className="pas-source-link" href={url} target="_blank" rel="noreferrer" onClick={(event) => onHostLink(event, url)}>{t('preview.openSource', '查看原始来源 ↗')}</a>}
  </article>;
}

function MetaSection({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="pas-meta-section"><h3>{title}</h3><div>{children}</div></section>;
}

function DisclosureSection({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return <details className="pas-meta-disclosure" data-disclosure={id}><summary>{title}</summary><div className="pas-disclosure-content">{children}</div></details>;
}

function SourceDetail({ source, catalog }: { source?: Catalog['sources']['sources'][number]; catalog: Catalog }) {
  const t = useText();
  if (!source) return <div className="pas-state" role="status">{t('source.notFound', '找不到这个来源。')}<a href="#/">{t('detail.back', '返回目录')}</a></div>;
  const sourceResources = catalog.resources.resources.filter((resource) => resource.provenance.content_source === source.id);
  return <article data-source-detail className="pas-detail pas-source-detail"><a className="pas-back-link" href="#/">{t('detail.back', '← 返回资源目录')}</a><p className="pas-eyebrow">{t('source.archive', '来源档案')}</p><h2>{source.name}</h2>
    <p>{t('source.access', '访问状态')}：{source.access === 'public' ? t('source.public', '公开') : source.access === 'restricted' ? t('source.restricted', '受限') : t('source.unknown', '未知')}</p><p>{t('source.roles', '来源角色')}：{source.roles.join(' · ') || t('source.unknown', '未说明')}</p>
    {source.access !== 'public' && <div className="pas-notice" role="note">{t('source.accessWarning', '来源访问受限或尚未确认公开。页面只展示已登记的公开元数据，不承诺来源内容可获取。')}</div>}
    {source.url && /^https?:\/\//i.test(source.url) && <p><a href={source.url} target="_blank" rel="noreferrer">{t('source.openWebsite', '打开来源网站 ↗')}</a></p>}
    <section className="pas-meta-section"><h3>{t('source.tracking', '来源追踪')}</h3><dl>{Object.entries(source.tracking).map(([key, value]) => <React.Fragment key={key}><dt>{key}</dt><dd>{Array.isArray(value) ? value.join(', ') : value ?? '—'}</dd></React.Fragment>)}</dl></section>
    <section className="pas-meta-section"><h3>{t('source.resources', '目录中的资源')}</h3>{sourceResources.length === 0 ? <p>{t('source.noResources', '当前目录没有关联资源。')}</p> : <ul className="pas-source-resource-list">{sourceResources.map((resource) => <li key={resource.id}><a href={stableRoute('resource', resource.id)}>{resource.title}</a><span>{t(`lifecycle.${resource.lifecycle.state}`, human(resource.lifecycle.state))} · {t(`verification.${resource.verification.level}`, human(resource.verification.level))}</span></li>)}</ul>}</section>
  </article>;
}
