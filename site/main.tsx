import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { loadCatalog } from '../src/catalog.js';
import type { Catalog } from '../src/contracts.js';
import { CatalogApp } from '../src/ui/index.js';
import '../src/ui/styles.css';

const catalogUrl = new URL('./catalog.json', import.meta.url).toString();

function Site() {
  const [catalog, setCatalog] = useState<Catalog>();
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let current = true;
    setStatus('loading');
    loadCatalog(catalogUrl, { expectedSchemaVersion: 3 }).then((value) => {
      if (current) { setCatalog(value); setStatus('ready'); setError(''); }
    }).catch((cause: unknown) => {
      if (current) { setStatus('error'); setError(cause instanceof Error ? cause.message : String(cause)); }
    });
    return () => { current = false; };
  }, [attempt]);
  return <CatalogApp catalog={catalog} status={status} error={error} onRetry={() => setAttempt((value) => value + 1)} locale="zh-CN" theme="system" accent="#6850c9" messages={{ brand: 'Agent 创作资源' }} />;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><Site /></React.StrictMode>);
