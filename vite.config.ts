import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  build: {
    emptyOutDir: false,
    lib: {
      cssFileName: 'ui/styles',
      entry: {
        index: resolve(import.meta.dirname, 'src/index.ts'),
        contracts: resolve(import.meta.dirname, 'src/contracts.ts'),
        catalog: resolve(import.meta.dirname, 'src/catalog.ts'),
        'ui/index': resolve(import.meta.dirname, 'src/ui/index.tsx'),
      },
      formats: ['es'],
    },
    rollupOptions: { external: ['react', 'react-dom', 'react/jsx-runtime'] },
  },
});
