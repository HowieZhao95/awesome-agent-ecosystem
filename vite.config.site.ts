import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  root: resolve(import.meta.dirname, 'site'),
  base: './',
  build: { outDir: resolve(import.meta.dirname, 'web-dist'), emptyOutDir: true },
  server: { strictPort: true },
});
