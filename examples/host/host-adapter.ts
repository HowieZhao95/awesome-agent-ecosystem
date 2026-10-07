import type { HostAdapter } from '@public-agent-store/catalog/contracts';

/**
 * Deliberately disconnected example adapter. Replace each method with the
 * real host's account, asset-state, install and navigation APIs before use.
 */
export const demoHostAdapter: HostAdapter = {
  hostId: 'demo-host',
  account: {
    status: async () => 'signed-out',
    login: async () => { throw new Error('This example has no account service.'); },
  },
  assetStatus: async () => ({ added: false, installed: false, applied: false, builtIn: false, requiresConfiguration: false }),
  operations: {
    add: async () => { throw new Error('Connect this callback to the host asset library.'); },
    install: async () => { throw new Error('Connect this callback to the host installer.'); },
    apply: async () => { throw new Error('Connect this callback to the host apply flow.'); },
    configure: async () => { throw new Error('Connect this callback to the host configuration UI.'); },
  },
  theme: { get: () => 'system', set: () => {} },
  i18n: { locale: 'zh-CN', translate: (key) => key },
  links: { open: (url) => window.open(url, '_blank', 'noopener,noreferrer') },
  preview: { open: (_resource, previewUrl) => window.open(previewUrl, '_blank', 'noopener,noreferrer') },
};
