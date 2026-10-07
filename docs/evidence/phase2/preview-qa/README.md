# Browser preview QA fixture

This page is an isolated visual test harness for the compiled public UI. The catalog is cloned in memory from the generated catalog JSON, reduced to two explicitly named QA records, and overridden with unknown rights/authorship and pending review. The media files are generated locally and are not catalog records or source material.

- `QA fixture — video and image carousel` exercises native video and carousel rendering.
- `QA fixture — withdrawn state` exercises the withdrawn notice and lack of host actions.
- The page passes no `HostAdapter`; it has no account, install, apply, or configuration service.
- The page imports `@public-agent-store/catalog/ui` and the public stylesheet export, so browser QA covers `dist` rather than a copied UI implementation.

`prepare-qa.mjs` builds into a unique temporary directory, then copies only its HTML and hashed assets plus the generated fixtures into `web-dist`. It records every QA-owned output path and SHA-256 in `docs/evidence/phase2/qa-manifest.json`, alongside hashes of the formal site entry and catalog asset for restoration checks.

To reproduce locally, finish `npm run build`, ensure FFmpeg is available, and prepare the fixture before starting the owned preview server:

```sh
node docs/evidence/phase2/preview-qa/prepare-qa.mjs
npm run start -- --port 3001
```

Open `/qa-preview/`. FFmpeg is only needed for this optional media QA harness, not for normal store setup or its automated tests. After review, stop the preview server you started, compare every QA file with `qa-manifest.json`, remove only those matching paths, and restart the formal preview. Never remove or overwrite the formal entry, catalog, or unrelated files. The completed run's cleanup is recorded in `qa-cleanup.json`.
