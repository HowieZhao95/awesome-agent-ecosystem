import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { cp, mkdir, mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const qaRoot = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(qaRoot, '../../../../');
const webRoot = resolve(repoRoot, 'web-dist');
const pageRoot = resolve(webRoot, 'qa-preview');
const manifestPath = resolve(repoRoot, 'docs/evidence/phase2/qa-manifest.json');
const tempRoot = await mkdtemp(resolve(tmpdir(), 'public-assets-preview-qa-'));
const buildRoot = resolve(tempRoot, 'bundle');
const fixtureVideo = resolve(tempRoot, 'qa-preview.mp4');
const previewOrigin = 'http://127.0.0.1:3001';

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { cwd: repoRoot, encoding: 'utf8', ...options });
  if (result.status !== 0) throw new Error(`${command} ${args.join(' ')} failed:\n${result.stdout ?? ''}\n${result.stderr ?? ''}`);
  return result.stdout ?? '';
}

async function sha256(path) {
  return createHash('sha256').update(await readFile(path)).digest('hex');
}

async function exists(path) {
  try { await stat(path); return true; } catch { return false; }
}

try {
  if (!(await exists(webRoot))) throw new Error('web-dist must exist from the completed public site build.');
  const oldManifest = await exists(manifestPath) ? JSON.parse(await readFile(manifestPath, 'utf8')) : undefined;
  if (oldManifest) {
    for (const item of oldManifest.qa_outputs ?? []) {
      const target = resolve(webRoot, item.path);
      if (await exists(target) && await sha256(target) !== item.sha256) throw new Error(`Existing QA output changed after manifest creation; preserving it: ${item.path}`);
    }
  }
  const formalHtmlPath = resolve(webRoot, 'index.html');
  const catalogPaths = (await readdir(resolve(webRoot, 'assets'))).filter((name) => /^catalog-.*\.json$/.test(name));
  if (catalogPaths.length !== 1) throw new Error(`Expected one formal hashed catalog asset; found ${catalogPaths.length}.`);
  const formal = [
    { path: 'index.html', sha256: await sha256(formalHtmlPath) },
    { path: `assets/${catalogPaths[0]}`, sha256: await sha256(resolve(webRoot, 'assets', catalogPaths[0])) },
  ];

  const vitePath = resolve(repoRoot, 'node_modules/vite/bin/vite.js');
  run(process.execPath, [vitePath, 'build', '--config', resolve(qaRoot, 'vite.config.mjs')], {
    env: { ...process.env, PREVIEW_QA_OUT_DIR: buildRoot },
  });
  run('ffmpeg', [
    '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=12',
    '-t', '1.5', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', fixtureVideo,
  ]);

  const priorQaFiles = oldManifest?.qa_outputs?.map((item) => item.path) ?? [];
  const intendedPaths = [
    'qa-preview/index.html',
    'qa-a.svg',
    'qa-b.svg',
    'qa-preview.mp4',
  ];
  const builtAssets = (await readdir(resolve(buildRoot, 'assets'))).map((name) => `qa-preview/assets/${name}`);
  intendedPaths.push(...builtAssets);
  const ownedPreviously = new Set(priorQaFiles);
  for (const path of intendedPaths) {
    if (await exists(resolve(webRoot, path)) && !ownedPreviously.has(path)) throw new Error(`Refusing to overwrite an unregistered web-dist file: ${path}`);
  }

  await mkdir(pageRoot, { recursive: true });
  await cp(resolve(buildRoot, 'index.html'), resolve(pageRoot, 'index.html'));
  await cp(resolve(buildRoot, 'assets'), resolve(pageRoot, 'assets'), { recursive: true });
  await cp(resolve(qaRoot, 'qa-a.svg'), resolve(webRoot, 'qa-a.svg'));
  await cp(resolve(qaRoot, 'qa-b.svg'), resolve(webRoot, 'qa-b.svg'));
  await cp(fixtureVideo, resolve(webRoot, 'qa-preview.mp4'));

  const qaOutputs = [];
  for (const path of intendedPaths) qaOutputs.push({ path, sha256: await sha256(resolve(webRoot, path)) });
  await writeFile(manifestPath, `${JSON.stringify({
    purpose: 'Temporary, isolated Phase 2 preview QA fixtures. Remove only qa_outputs paths after review.',
    entry_url: `${previewOrigin}/qa-preview/`,
    preview_urls: [`${previewOrigin}/qa-preview.mp4`, `${previewOrigin}/qa-a.svg`, `${previewOrigin}/qa-b.svg`],
    protected_formal_outputs: formal,
    qa_outputs: qaOutputs,
  }, null, 2)}\n`);
  console.log(`QA fixture ready at ${previewOrigin}/qa-preview/; ${qaOutputs.length} exact QA-owned output paths recorded.`);
} finally {
  await rm(tempRoot, { recursive: true, force: true });
}
