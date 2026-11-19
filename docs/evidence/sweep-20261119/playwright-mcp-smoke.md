# playwright-mcp smoke (2026-11-19 Asia/Shanghai)

- Upstream release tag `v0.0.86` / npm gitHead `2337aff0213d28db41d3e3daf48cee19b3d0bd82` (tag peels to the same commit; tip equals the pin)
- npm: `@playwright/mcp@0.0.86` (published 2026-11-19 02:54 CST)
- Previous intended pin (11-18, not yet on catalog main): tag `v0.0.85` / `4e0794dd0a0176519830a5ed27b491137cf9338f`
- Catalog main pin still: commit `0c4107acbecb75472b23c05c0e42471a0011874f` / `@playwright/mcp@0.0.83`
- License: Apache-2.0 (repository-root; unchanged)
- Host: box Node v24.22.1 / `npx -y @playwright/mcp@0.0.86`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (content-length then ndjson; ndjson succeeded)
- Outcome: initialize OK (`serverInfo.name=Playwright`, version `1.66.0-alpha-2026-11-18`); tools/list returned **25** tools including `browser_navigate`, `browser_snapshot`, `browser_click`, and `browser_run_code_unsafe` (same 25-name set as the 0.0.85 smoke)
- JSON: `smoke/playwright-mcp-0.0.86.json`
- Uninstall: removed this pass's `~/.npm/_npx` cache dirs (before-snapshot was empty). No global install. Did not touch `~/.cache/ms-playwright`.
- Limits: MCP handshake only; no page open or `browser_*` scenario.
