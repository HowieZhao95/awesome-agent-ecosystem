import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { loadCatalog } from '@public-agent-store/catalog/catalog';
import type { Catalog } from '@public-agent-store/catalog/contracts';
import { CatalogApp } from '@public-agent-store/catalog/ui';
import '@public-agent-store/catalog/ui/styles.css';
import { demoHostAdapter } from './host-adapter.js';

function HostExample() {
  const [catalog, setCatalog] = useState<Catalog>();
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [error, setError] = useState('');
  useEffect(() => {
    let current = true;
    loadCatalog('/catalog.json', { expectedSchemaVersion: 3 }).then((value) => {
      if (current) { setCatalog(value); setStatus('ready'); }
    }).catch((cause: unknown) => {
      if (current) { setError(cause instanceof Error ? cause.message : String(cause)); setStatus('error'); }
    });
    return () => { current = false; };
  }, []);
  return <>
    <aside className="pas-demo-note" role="note">宿主接入示例：账户和资源操作回调尚未连接实际服务；此页面不会登录、安装或更改资源。</aside>
    <CatalogApp catalog={catalog} status={status} error={error} host={demoHostAdapter} theme="system" accent="#276f64" locale="zh-CN" messages={{ brand: '宿主资源目录示例' }} />
  </>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><HostExample /></React.StrictMode>);
