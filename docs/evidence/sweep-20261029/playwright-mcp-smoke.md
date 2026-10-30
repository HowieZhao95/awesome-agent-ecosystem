# playwright-mcp smoke (2026-10-29 Asia/Shanghai)

- Upstream tip `main`: `0c4107acbecb75472b23c05c0e42471a0011874f`
- npm: `@playwright/mcp@0.0.83`
- License: Apache-2.0 (root LICENSE + package.json)
- Host: box Node 20 / `npx -y @playwright/mcp@0.0.83`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio
- Outcome: initialize OK (`serverInfo.name=Playwright`); tools/list returned browser_* tools
- Uninstall: removed verify dirs and `~/.npm/_npx` cache for this pass
