import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { createRequire } from "node:module";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { compile } from "@tailwindcss/node";
import { Scanner } from "@tailwindcss/oxide";
import { build } from "esbuild";

const root = fileURLToPath(new URL("../", import.meta.url));
const require = createRequire(import.meta.url);
const manifest = JSON.parse(readFileSync(join(root, "manifest.json"), "utf8"));
const dist = join(root, "dist");
mkdirSync(dist, { recursive: true });
const common = {
  absWorkingDir: root,
  bundle: true,
  jsx: "automatic",
  logLevel: "silent",
  target: "es2022",
};
await build({
  ...common,
  entryPoints: ["src/index.ts"],
  outfile: join(dist, "index.js"),
  format: "esm",
  packages: "external",
});
execFileSync(
  process.execPath,
  [require.resolve("typescript/bin/tsc"), "-p", join(root, "tsconfig.json")],
  { stdio: "inherit" }
);
const bundle = await build({
  ...common,
  entryPoints: ["standalone/entry.tsx"],
  write: false,
  minify: true,
  format: "iife",
  platform: "browser",
  metafile: true,
  define: { "process.env.NODE_ENV": '"production"' },
});
const css = await compile(
  readFileSync(join(root, "standalone/style.css"), "utf8"),
  {
    base: root,
    onDependency() {
      /* A one-shot build has no file watcher. */
    },
  }
);
const scanner = new Scanner({
  sources: [
    { base: root, pattern: "{src,standalone}/**/*.{ts,tsx}", negated: false },
  ],
});
const sheet = css.build(scanner.scan());
const javascript = bundle.outputFiles[0].text.replace(
  /<\/script/gi,
  "<\\/script"
);

for (const template of manifest.templates) {
  const sample = JSON.parse(readFileSync(join(root, template.example), "utf8"));
  const json = JSON.stringify(sample, null, 2).replaceAll("<", "\\u003c");
  const html = `<!doctype html>
<html lang="${sample.language}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Learning Studio</title><style>${sheet}</style></head>
<body><main id="learning-root"></main>
<script type="application/json" id="learning-artifact">${json}</script>
<script>${javascript}</script></body></html>\n`;
  writeFileSync(join(root, template.preview), html);
}

// Preserve the license notices for code actually included in the standalone HTML.
const licenseFilename = /^licen[cs]e(?:\..*)?$/i;
const packages = new Map();
for (const filename of [
  ...Object.keys(bundle.metafile.inputs),
  require.resolve("tailwindcss"),
]) {
  const file = resolve(root, filename);
  if (!file.includes("/node_modules/")) {
    continue;
  }
  let dir = dirname(file);
  while (dir !== dirname(dir)) {
    const infoFile = join(dir, "package.json");
    if (existsSync(infoFile)) {
      const info = JSON.parse(readFileSync(infoFile, "utf8"));
      if (info.name && info.version) {
        const name = `${info.name}@${info.version}`;
        if (!packages.has(name)) {
          const license = readdirSync(dir).find((entry) =>
            licenseFilename.test(entry)
          );
          const path = license
            ? join(dir, license)
            : join(
                root,
                "standalone/licenses",
                `${info.name}-${info.version}.txt`
              );
          if (!existsSync(path)) {
            throw new Error(`Missing distribution license for ${name}`);
          }
          packages.set(name, readFileSync(path, "utf8").trim());
        }
        break;
      }
    }
    dir = dirname(dir);
  }
}
const notices = `${[...packages]
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([name, license]) => `${name}\n${license}`)
  .join("\n\n")}\n`;
writeFileSync(join(dist, "THIRD-PARTY-NOTICES.txt"), notices);
const licenseText =
  `${readFileSync(join(root, "LICENSE"), "utf8")}\n${notices}`.replace(
    /<\/script/gi,
    "<\\/script"
  );
for (const template of manifest.templates) {
  const path = join(root, template.preview);
  const html = readFileSync(path, "utf8");
  writeFileSync(
    path,
    html.replace(
      "</body></html>",
      `<script type="text/plain" id="learning-licenses">${licenseText}</script></body></html>`
    )
  );
}
console.log(
  `Built ${manifest.name} ${manifest.version} in ${basename(dist)} with ${packages.size} dependency notices.`
);
