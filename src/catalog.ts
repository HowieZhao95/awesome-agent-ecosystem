import type { Catalog, Resource } from './contracts.js';

export interface CatalogFilters {
  category?: string;
  subtype?: string;
  domain?: string;
  source?: string;
  lifecycle?: string;
  verification?: string;
  query?: string;
}

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
