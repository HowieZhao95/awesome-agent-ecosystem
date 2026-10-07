import type { CategoryId, ComponentTypeId, ConventionId, DomainId, FormatId, SubtypeId } from './generated/enums.js';
export type { CategoryId, ComponentTypeId, ConventionId, DomainId, FormatId, SubtypeId } from './generated/enums.js';

export type ReviewStatus = 'pending' | 'approved' | 'rejected';
export type LifecycleState = 'reference' | 'candidate' | 'usable' | 'withdrawn';
export type VerificationLevel = 'unverified' | 'source-inspected' | 'usage-tested';
export interface Evidence { locator: string; claim: string }
export interface Identity { name: string; url: string | null }
export interface IdentityRecord { status: 'known' | 'unknown'; identities: Identity[]; evidence: Evidence[] }
export interface Upstream { kind: 'git' | 'web' | 'product' | 'catalog'; url: string; path: string | null; selector: string | null; ref: { kind: string; value: string | null } }
export interface Component { id: string; type: ComponentTypeId; resource_id: string | null; upstream: Upstream; subtype: SubtypeId | null; delivery: 'contained' | 'referenced' | 'host-provided' }
export interface Resource {
  id: string; title: string; summary: string; purpose: string;
  classification: { category: CategoryId; subtype: SubtypeId | null; domains: DomainId[]; formats: FormatId[]; conventions: ConventionId[]; rationale: string };
  provenance: { relation: 'original' | 'adapted' | 'curated'; content_source: string; discovered_via: string[]; upstream: Upstream; derives_from: string[]; changes: string | null };
  authors: IdentityRecord; publisher: IdentityRecord;
  license: { status: 'verified' | 'unknown'; expression: string | null; scope: string | null; evidence: Evidence[]; redistribution: 'allowed' | 'blocked' | 'unknown' };
  distribution: { kind: string; channel_source: string | null; url: string }[];
  previews: { kind: string; url: string; status: 'reference' | 'verified'; evidence: Evidence[] }[];
  compatibility: { hosts: string[]; runtimes: { name: string; version: string | null; status: 'declared' | 'verified' | 'unknown' }[]; dependencies: { kind: string; name: string; version: string | null; source_id: string | null }[]; constraints: string[] };
  components: Component[];
  template?: TemplateProfile;
  design_system?: DesignSystemProfile;
  lifecycle: { state: LifecycleState; reason: string; replacement_id: string | null };
  review: { status: ReviewStatus; by: string | null; at: string | null; evidence: Evidence[] };
  verification: { level: VerificationLevel; tested_hosts: string[]; checked_at: string | null; by: string | null; evidence: Evidence[]; limits: string[] };
}
export type ProfileFile = { role: string; path: string; url: string };
export type TemplateProfile = {
  files: { role: 'instructions' | 'framework' | 'example' | 'support'; path: string; url: string }[];
  style: { policy: 'external-design-system'; upstream_status: 'independent' | 'mixed' | 'unknown'; note: string };
};
export type DesignSystemProfile = {
  files: { role: 'manifest' | 'rules' | 'tokens-css' | 'example' | 'support'; path: string; url: string }[];
};
export interface Category { id: CategoryId; label: string; definition: string; subtypes: { id: SubtypeId; label: string; definition: string }[]; excludes?: string[]; minimum_profile?: string }
export interface Catalog {
  schema_version: number;
  availability?: Record<string, string[]>;
  categories: { schema_version: number; review_status: ReviewStatus; categories: Category[]; classification_rules: string[]; dimensions: { domains: { id: DomainId; label: string; definition: string }[]; formats: { id: FormatId; label: string; definition: string; extensions?: string[] }[]; conventions: { id: ConventionId; label: string; definition: string }[]; plugin_component_types: { id: ComponentTypeId; label: string; definition: string }[] } };
  sources: { schema_version: number; sources: Source[] };
  resources: { schema_version: number; meta: { catalog_version: string; updated: string; review: { status: ReviewStatus; by: string | null; at: string | null; evidence: Evidence[] } }; resources: Resource[] };
  discovery?: DiscoveryCatalog;
}
export interface DiscoveryEntry {
  id: string;
  title: string;
  summary: string;
  classification: { category: CategoryId; subtype: SubtypeId | null; domains: DomainId[]; formats: FormatId[]; conventions: ConventionId[]; rationale: string };
  source_url: string | null;
  channel_source: string | null;
  legacy_keys: string[];
  legacy: { category: string; subcat: string | null; platform: string | null; source_label: string | null; stars: number | null; installs: number | null; last_verified: string | null; vmethod: string | null };
  content_kind: 'asset' | 'reference' | 'collection' | 'specification';
  expected_components: string[];
  missing: string[];
  mapped_resource_id?: string;
}
export interface DiscoveryPlatform {
  id: string;
  name: string;
  url: string | null;
  summary: string;
  legacy_key: string;
  source_label: string | null;
}
export interface DiscoveryCatalog {
  schema_version: 1;
  source_id: string;
  input_sha256: string;
  entries: DiscoveryEntry[];
  platforms: DiscoveryPlatform[];
  additional_sources?: { source_id: string; ref: Upstream["ref"]; entries: number }[];
  coverage: { total_assets: number; total_platforms: number; outcomes: { legacy_key: string; target_id: string; disposition: 'mapped' | 'merged' | 'discovery'; reason: string }[] };
}
export type BrowseResource = Omit<Resource, 'provenance'> & {
  directory_origin: 'catalog' | 'discovery';
  provenance: Omit<Resource['provenance'], 'content_source' | 'upstream'> & { content_source: string | null; upstream: Upstream | null };
  discovery?: DiscoveryEntry;
  discovery_aliases?: DiscoveryEntry[];
};
export interface Source {
  id: string; name: string; url: string | null;
  roles: ('content-upstream' | 'discovery-channel' | 'distribution-channel' | 'specification')[];
  access: 'public' | 'restricted' | 'unknown';
  tracking: { scope: string | string[]; exclude: string[]; baseline: string; cadence: string; method: string; promotion: string; last_checked: string | null; limitations: string[] | string };
}

export interface HostAdapter {
  hostId: string;
  account: { status(): Promise<'signed-out' | 'signed-in'>; login(): Promise<void> };
  assetStatus(resourceId: string): Promise<{ added: boolean; installed: boolean; applied: boolean; builtIn: boolean; requiresConfiguration: boolean }>;
  operations: { add(resource: Resource): Promise<void>; install(resource: Resource): Promise<void>; apply(resource: Resource): Promise<void>; configure(resource: Resource): Promise<void> };
  theme: { get(): 'light' | 'dark' | 'system'; set(theme: 'light' | 'dark' | 'system'): void };
  i18n: { locale: string; translate(key: string, values?: Record<string, string | number>): string };
  links: { open(url: string): void };
  preview: { open(resource: Resource, previewUrl: string): void };
}
