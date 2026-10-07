import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const candidates = [process.env.PYTHON, 'python3', '/Applications/Xcode.app/Contents/Developer/usr/bin/python3'].filter(Boolean);
let python;
for (const candidate of candidates) {
  const probe = spawnSync(candidate, ['-c', 'import yaml'], { cwd: root, stdio: 'ignore' });
  if (probe.status === 0) { python = candidate; break; }
}
if (!python) throw new Error('PyYAML is required for generation. Install requirements.txt or set PYTHON to an interpreter with PyYAML.');
for (const file of ['scripts/build.py', 'scripts/generate-package.py']) {
  const result = spawnSync(python, [file], { cwd: root, stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
