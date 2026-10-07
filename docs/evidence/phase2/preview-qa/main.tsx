import React from 'react';
import { createRoot } from 'react-dom/client';
import type { Catalog, Resource, Source } from '@public-agent-store/catalog/contracts';
import { CatalogApp } from '@public-agent-store/catalog/ui';
import '@public-agent-store/catalog/ui/styles.css';
import canonical from '../../../../site/catalog.json';
import './qa.css';

const fixtureRoot = 'http://127.0.0.1:3001';
const mediaId = 'phase2-qa.video-carousel';
const withdrawnId = 'phase2-qa.withdrawn';
const sourceId = 'phase2-qa.local-fixtures';
const catalog = createFixtureCatalog(canonical as unknown as Catalog);

function createFixtureCatalog(base: Catalog): Catalog {
  const original = base.resources.resources[0];
  if (!original) throw new Error('Canonical catalog has no resource to use as a QA shape template.');
  const evidence = [{ locator: 'docs/evidence/phase2/preview-qa/README.md', claim: 'Locally generated QA-only media; not a public asset or rights claim.' }];
  const source: Source = {
    id: sourceId,
    name: 'Phase 2 local QA fixtures',
    url: null,
    roles: ['specification'],
    access: 'public',
    tracking: {
      scope: 'Generated local SVG and test video fixtures only.',
      exclude: [],
      baseline: 'QA-only, generated locally for browser preview checks.',
      cadence: 'none',
      method: 'No source synchronization; discard these fixtures after visual QA.',
      promotion: 'Never promote QA fixtures into the public resource catalog.',
      last_checked: null,
      limitations: ['This record exists only to render the isolated browser QA page.'],
    },
  };
  const fixture = (id: string, title: string, lifecycle: Resource['lifecycle']): Resource => ({
    ...structuredClone(original),
    id,
    title,
    summary: '仅验收夹具：本地生成的短视频与 SVG 图片，用于预览组件浏览器检查。',
    purpose: '仅用于阶段 2 浏览器验收，不是正式目录资源。',
    classification: {
      category: 'templates', subtype: 'prototype', domains: ['general'], formats: ['media'], conventions: [],
      rationale: 'QA-only shape required to exercise the shared resource detail component.',
    },
    provenance: {
      relation: 'curated',
      content_source: sourceId,
      discovered_via: [],
      upstream: { kind: 'web', url: `${fixtureRoot}/qa-fixture`, path: null, selector: id, ref: { kind: 'unknown', value: null } },
      derives_from: [],
      changes: null,
    },
    authors: { status: 'unknown', identities: [], evidence },
    publisher: { status: 'unknown', identities: [], evidence },
    license: { status: 'unknown', expression: null, scope: 'QA-only generated fixtures; no redistribution rights are asserted.', evidence, redistribution: 'unknown' },
    distribution: [],
    previews: id === mediaId ? [
      { kind: 'video', url: `${fixtureRoot}/qa-preview.mp4`, status: 'reference', evidence },
      { kind: 'carousel', url: `${fixtureRoot}/qa-a.svg`, status: 'reference', evidence },
      { kind: 'carousel', url: `${fixtureRoot}/qa-b.svg`, status: 'reference', evidence },
    ] : [],
    compatibility: { hosts: [], runtimes: [], dependencies: [], constraints: ['QA fixture only; no host integration or account state is connected.'] },
    components: [],
    lifecycle,
    review: { status: 'pending', by: null, at: null, evidence: [] },
    verification: { level: 'unverified', tested_hosts: [], checked_at: null, by: null, evidence: [], limits: ['Preview fixture only; not a real asset review or usage verification.'] },
  });
  const result = structuredClone(base);
  result.availability = {};
  result.sources.sources = [source];
  result.resources.meta.catalog_version = '0.0.0-preview-qa-only';
  result.resources.meta.review = { status: 'pending', by: null, at: null, evidence: [] };
  result.resources.resources = [
    fixture(mediaId, 'QA fixture — video and image carousel', { state: 'candidate', reason: 'QA-only fixture; never a catalog recommendation.', replacement_id: null }),
    fixture(withdrawnId, 'QA fixture — withdrawn state', { state: 'withdrawn', reason: 'QA-only fixture to verify withdrawn messaging; this is not a real withdrawn asset.', replacement_id: null }),
  ];
  return result;
}

function FixturePage() {
  if (!window.location.hash) window.location.hash = `#/resource/${encodeURIComponent(mediaId)}`;
  return <>
    <header className="qa-banner">
      <strong>仅验收夹具 · 非正式资源</strong>
      <span>本页只检查视频、图片轮播和撤回状态。没有账号、安装或宿主操作。</span>
      <nav aria-label="QA fixture routes">
        <a href={`#/resource/${encodeURIComponent(mediaId)}`}>Video + carousel</a>
        <a href={`#/resource/${encodeURIComponent(withdrawnId)}`}>Withdrawn state</a>
      </nav>
    </header>
    <CatalogApp catalog={catalog} status="ready" locale="en" theme="light" accent="#276f64" messages={{ brand: 'QA only — not catalog content' }} />
  </>;
}

createRoot(document.getElementById('qa-root')!).render(<React.StrictMode><FixturePage /></React.StrictMode>);
