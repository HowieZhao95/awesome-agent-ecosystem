import { defineConfig } from 'vite';
import { resolve } from 'node:path';

const output = process.env.PREVIEW_QA_OUT_DIR;
if (!output) throw new Error('Set PREVIEW_QA_OUT_DIR to a unique temporary output directory.');

export default defineConfig({
  root: import.meta.dirname,
  base: './',
  publicDir: false,
  build: { outDir: resolve(output), emptyOutDir: true },
});
