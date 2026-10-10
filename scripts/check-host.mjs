import assert from 'node:assert/strict';
import { cp, mkdtemp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const root = resolve(import.meta.dirname, '..');
const temporary = await mkdtemp(resolve(tmpdir(), 'public-agent-store-host-'));
function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, encoding: 'utf8' });
  if (result.status !== 0) throw new Error(`${command} ${args.join(' ')} failed:\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}

try {
  const packed = JSON.parse(run('npm', ['pack', '--pack-destination', temporary, '--json'], root));
  const tarball = resolve(temporary, packed[0].filename);
  const consumer = resolve(temporary, 'consumer');
  await mkdir(consumer);
  const lock = JSON.parse(await readFile(resolve(root, 'package-lock.json'), 'utf8'));
  const reactVersion = lock.packages['node_modules/react'].version;
  const reactDomVersion = lock.packages['node_modules/react-dom'].version;
  const typeVersions = Object.fromEntries(['typescript', '@types/react', '@types/react-dom', 'vite'].map((name) => [name, lock.packages[`node_modules/${name}`].version]));
  await writeFile(resolve(consumer, 'package.json'), JSON.stringify({
    name: 'public-agent-store-host-check', private: true, type: 'module',
    dependencies: { '@public-agent-store/catalog': `file:${tarball}`, react: reactVersion, 'react-dom': reactDomVersion },
    devDependencies: typeVersions,
  }));
  run('npm', ['install', '--prefer-offline', '--ignore-scripts', '--no-audit', '--no-fund'], consumer);
  await cp(resolve(root, 'examples/host'), consumer, { recursive: true });
  await mkdir(resolve(consumer, 'public'));
  await cp(resolve(root, 'site/catalog.json'), resolve(consumer, 'public/catalog.json'));
  run(process.execPath, [resolve(consumer, 'node_modules/typescript/bin/tsc'), '--noEmit', '--strict', '--skipLibCheck', '--allowSyntheticDefaultImports', '--jsx', 'react-jsx', '--target', 'ES2022', '--module', 'ESNext', '--moduleResolution', 'Bundler', 'main.tsx', 'host-adapter.ts'], consumer);
  run(process.execPath, [resolve(consumer, 'node_modules/vite/bin/vite.js'), 'build', '--outDir', 'host-dist'], consumer);
  const outputFiles = await readdir(resolve(consumer, 'host-dist/assets'));
  assert.ok(outputFiles.some((file) => file.endsWith('.css')), 'host build includes the package stylesheet');
  assert.ok(outputFiles.some((file) => file.endsWith('.js')), 'host build includes the package UI bundle');
  const declarations = await readFile(resolve(consumer, 'node_modules/@public-agent-store/catalog/dist/contracts.d.ts'), 'utf8');
  assert.match(declarations, /HostAdapter/);
  console.log(`Packed package ${basename(tarball)} installed in a temporary consumer; the real host example typechecked and built with the public exports.`);
} finally {
  await rm(temporary, { recursive: true, force: true });
}
