import type { BrowseResource, Catalog, DiscoveryEntry, Resource } from './contracts.js';

export interface CatalogFilters {
  category?: string;
  subtype?: string;
  domain?: string;
  source?: string;
  lifecycle?: string;
  verification?: string;
  query?: string;
}
export interface BrowseFilters extends CatalogFilters { origin?: string; channel?: string }

export interface Page<T> { items: T[]; page: number; pageSize: number; total: number; pageCount: number }
export interface RelatedComponent { component: Resource['components'][number]; resource: Resource | undefined }

export function filterResources(catalog: Catalog, filters: CatalogFilters = {}): Resource[] {
  const query = filters.query?.trim().toLocaleLowerCase();
  return catalog.resources.resources.filter((resource) => {
    const c = resource.classification;
    return (!filters.category || c.category === filters.category)
      && (!filters.subtype || c.subtype === filters.subtype)
      && (!filters.domain || c.domains.some((domain) => domain === filters.domain))
      && (!filters.source || resource.provenance.content_source === filters.source)
      && (!filters.lifecycle || resource.lifecycle.state === filters.lifecycle)
      && (!filters.verification || resource.verification.level === filters.verification)
      && (!query || [resource.id, resource.title, resource.summary, resource.purpose].some((text) => text.toLocaleLowerCase().includes(query)));
  });
}

export function getResource(catalog: Catalog, id: string): Resource | undefined {
  return catalog.resources.resources.find((resource) => resource.id === id);
}

function projectDiscovery(entry: DiscoveryEntry): BrowseResource {
  const reason = entry.missing.length ? entry.missing.join('; ') : '待审核发现线索；尚未核实来源、许可与可用性。';
  return {
    id: entry.id, title: entry.title, summary: entry.summary, purpose: entry.summary,
    classification: entry.classification,
    directory_origin: 'discovery', discovery: entry,
    provenance: { relation: 'curated', content_source: null, discovered_via: [], upstream: null, derives_from: [], changes: null },
    authors: { status: 'unknown', identities: [], evidence: [] }, publisher: { status: 'unknown', identities: [], evidence: [] },
    license: { status: 'unknown', expression: null, scope: null, evidence: [], redistribution: 'unknown' },
    distribution: [], previews: [], compatibility: { hosts: [], runtimes: [], dependencies: [], constraints: [] }, components: [],
    lifecycle: { state: 'candidate', reason, replacement_id: null },
    review: { status: 'pending', by: null, at: null, evidence: [] },
    verification: { level: 'unverified', tested_hosts: [], checked_at: null, by: null, evidence: [], limits: [...entry.missing] },
  };
}

export function getBrowseResources(catalog: Catalog): BrowseResource[] {
  const represented = new Set(catalog.resources.resources.map((resource) => resource.id));
  const aliases = new Map<string, DiscoveryEntry[]>();
  for (const entry of catalog.discovery?.entries ?? []) {
    if (!entry.mapped_resource_id || !represented.has(entry.mapped_resource_id)) continue;
    const current = aliases.get(entry.mapped_resource_id) ?? [];
    current.push(entry);
    aliases.set(entry.mapped_resource_id, current);
  }
  const canonical = catalog.resources.resources.map((resource): BrowseResource => ({
    ...resource,
    directory_origin: 'catalog',
    ...(aliases.has(resource.id) ? { discovery_aliases: aliases.get(resource.id)! } : {}),
  }));
  const discoveries = (catalog.discovery?.entries ?? [])
    .filter((entry) => (!entry.mapped_resource_id || !represented.has(entry.mapped_resource_id)) && !represented.has(entry.id))
    .map(projectDiscovery);
  return [...canonical, ...discoveries];
}

export function getBrowseResource(catalog: Catalog, id: string): BrowseResource | undefined {
  const resources = getBrowseResources(catalog);
  const direct = resources.find((resource) => resource.id === id);
  if (direct) return direct;
  const mappedId = catalog.discovery?.entries.find((entry) => entry.id === id)?.mapped_resource_id;
  return mappedId ? resources.find((resource) => resource.id === mappedId) : undefined;
}

export function filterBrowseResources(catalog: Catalog, filters: BrowseFilters = {}): BrowseResource[] {
  const query = filters.query?.trim().toLocaleLowerCase();
  return getBrowseResources(catalog).filter((resource) => {
    const c = resource.classification;
    const discovery = resource.discovery;
    const aliases = resource.discovery_aliases ?? [];
    return (!filters.category || c.category === filters.category)
      && (!filters.subtype || c.subtype === filters.subtype)
      && (!filters.domain || c.domains.includes(filters.domain as never))
      && (!filters.source || resource.provenance.content_source === filters.source || discovery?.channel_source === filters.source || aliases.some((entry) => entry.channel_source === filters.source))
      && (!filters.lifecycle || resource.lifecycle.state === filters.lifecycle)
      && (!filters.verification || resource.verification.level === filters.verification)
      && (!filters.origin || resource.directory_origin === filters.origin || (filters.origin === 'discovery' && aliases.length > 0))
      && (!filters.channel || discovery?.channel_source === filters.channel || aliases.some((entry) => entry.channel_source === filters.channel))
      && (!query || [resource.id, resource.title, resource.summary, resource.purpose, ...(discovery?.legacy_keys ?? []), ...aliases.flatMap((entry) => [entry.id, entry.title, entry.summary, entry.source_url ?? '', ...entry.legacy_keys, entry.legacy.category, entry.legacy.subcat ?? '', entry.legacy.platform ?? '', entry.legacy.source_label ?? ''])].some((text) => text.toLocaleLowerCase().includes(query)));
  });
}

export function isAvailableForHost(catalog: Catalog, resourceId: string, hostId: string): boolean {
  return catalog.availability?.[resourceId]?.includes(hostId) ?? false;
}

export function getResourcePageUrl(id: string): string {
  return `#/resource/${encodeURIComponent(id)}`;
}

export function paginateResources<T>(resources: readonly T[], options: { page: number; pageSize: number }): Page<T> {
  const pageSize = Math.max(1, Math.floor(options.pageSize));
  const pageCount = Math.max(1, Math.ceil(resources.length / pageSize));
  const page = Math.min(pageCount, Math.max(1, Math.floor(options.page)));
  return { items: resources.slice((page - 1) * pageSize, page * pageSize), page, pageSize, total: resources.length, pageCount };
}

export function getRelatedComponents(catalog: Catalog, parent: Resource): RelatedComponent[] {
  return parent.components.map((component) => ({
    component: { ...component },
    resource: component.resource_id ? getResource(catalog, component.resource_id) : undefined,
  }));
}

export async function loadCatalog(url: string, options: { fetchImpl?: typeof fetch; expectedSchemaVersion?: number; expectedCatalogVersion?: string } = {}): Promise<Catalog> {
  const response = await (options.fetchImpl ?? fetch)(url);
  if (!response.ok) throw new Error(`Catalog request failed: ${response.status} ${response.statusText}`);
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== 'object' || !('schema_version' in payload) || !('categories' in payload) || !('sources' in payload) || !('resources' in payload)) {
    throw new Error('Catalog response has an invalid shape');
  }
  const catalog = payload as Catalog;
  if (typeof catalog.schema_version !== 'number' || !Array.isArray(catalog.categories.categories)
    || !Array.isArray(catalog.sources.sources) || !Array.isArray(catalog.resources.resources)
    || !catalog.resources.meta || typeof catalog.resources.meta.catalog_version !== 'string') {
    throw new Error('Catalog response has an invalid shape');
  }
  if (catalog.discovery !== undefined) {
    const discovery = catalog.discovery;
    const validOutcome = (outcome: unknown) => Boolean(outcome && typeof outcome === 'object' && !Array.isArray(outcome)
      && 'legacy_key' in outcome && typeof outcome.legacy_key === 'string'
      && 'target_id' in outcome && typeof outcome.target_id === 'string'
      && 'disposition' in outcome && ['mapped', 'merged', 'discovery'].includes(String(outcome.disposition))
      && 'reason' in outcome && typeof outcome.reason === 'string');
    const validAdditionalSource = (source: unknown) => Boolean(source && typeof source === 'object' && !Array.isArray(source)
      && 'source_id' in source && typeof source.source_id === 'string'
      && 'ref' in source && source.ref && typeof source.ref === 'object' && !Array.isArray(source.ref)
      && 'entries' in source && typeof source.entries === 'number' && Number.isFinite(source.entries));
    const validEntry = (entry: unknown) => Boolean(entry && typeof entry === 'object' && !Array.isArray(entry)
      && 'id' in entry && typeof entry.id === 'string'
      && 'title' in entry && typeof entry.title === 'string'
      && 'summary' in entry && typeof entry.summary === 'string'
      && 'classification' in entry && entry.classification !== null && typeof entry.classification === 'object' && !Array.isArray(entry.classification)
      && 'legacy_keys' in entry && Array.isArray(entry.legacy_keys)
      && 'legacy' in entry && entry.legacy !== null && typeof entry.legacy === 'object' && !Array.isArray(entry.legacy)
      && 'missing' in entry && Array.isArray(entry.missing));
    if (!discovery || typeof discovery !== 'object' || Array.isArray(discovery)
      || discovery.schema_version !== 1 || typeof discovery.source_id !== 'string' || typeof discovery.input_sha256 !== 'string'
      || !Array.isArray(discovery.entries) || !discovery.entries.every(validEntry)
      || !Array.isArray(discovery.platforms) || !discovery.platforms.every((platform) => platform && typeof platform.id === 'string' && typeof platform.name === 'string')
      || !discovery.coverage || typeof discovery.coverage.total_assets !== 'number' || typeof discovery.coverage.total_platforms !== 'number'
      || !Array.isArray(discovery.coverage.outcomes) || !discovery.coverage.outcomes.every(validOutcome)
      || (discovery.additional_sources !== undefined && (!Array.isArray(discovery.additional_sources) || !discovery.additional_sources.every(validAdditionalSource)))) {
      throw new Error('Catalog response has an invalid shape');
    }
  }
  if (catalog.availability !== undefined && (!catalog.availability || typeof catalog.availability !== 'object'
    || Object.values(catalog.availability).some((hosts) => !Array.isArray(hosts) || hosts.some((host) => typeof host !== 'string')))) {
    throw new Error('Catalog response has an invalid shape');
  }
  if (options.expectedSchemaVersion !== undefined && catalog.schema_version !== options.expectedSchemaVersion) {
    throw new Error(`Catalog schema version ${catalog.schema_version} does not match expected schema version ${options.expectedSchemaVersion}`);
  }
  if (options.expectedCatalogVersion !== undefined && catalog.resources.meta?.catalog_version !== options.expectedCatalogVersion) {
    throw new Error(`Catalog version ${catalog.resources.meta?.catalog_version ?? 'missing'} does not match expected catalog version ${options.expectedCatalogVersion}`);
  }
  return catalog;
}
