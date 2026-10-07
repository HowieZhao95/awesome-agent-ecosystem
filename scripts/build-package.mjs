import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const root = resolve(import.meta.dirname, '..');
function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, stdio: 'inherit' });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
run('npm', ['run', 'generate']);
run('npx', ['tsc', '-p', 'tsconfig.build.json']);
run('npx', ['vite', 'build', '--config', 'vite.config.ts']);
const publicStyles = resolve(root, 'dist/ui/styles.css');
mkdirSync(dirname(publicStyles), { recursive: true });
copyFileSync(resolve(root, 'src/ui/styles.css'), publicStyles);
run('npx', ['vite', 'build', '--config', 'vite.config.site.ts']);
