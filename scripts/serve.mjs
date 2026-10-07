import { createServer, preview } from 'vite';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const mode = process.argv[2] ?? 'dev';
const args = process.argv.slice(3);
let port = 3001;
for (let index = 0; index < args.length; index += 1) {
  if (args[index] === '--port') port = Number(args[index + 1]);
  else if (args[index].startsWith('--port=')) port = Number(args[index].slice(7));
  else if (args[index] === '--port3000') port = 3000;
  else if (args[index] === '--port3001') port = 3001;
}
if (![3000, 3001].includes(port)) throw new Error('Only ports 3000 and 3001 are permitted.');
if (mode === 'start') {
  await preview({ configFile: resolve(root, 'vite.config.site.ts'), preview: { host: '127.0.0.1', port, strictPort: true } });
} else {
  const server = await createServer({ configFile: resolve(root, 'vite.config.site.ts'), server: { host: '127.0.0.1', port, strictPort: true } });
  await server.listen();
  server.printUrls();
}
