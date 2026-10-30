# chrome-devtools-mcp smoke (2026-10-29 Asia/Shanghai)

- Upstream tip `main`: `bc0d93ee2df6f2410d9e9704903c3547acae7c9a`
- npm: `chrome-devtools-mcp@1.12.0`
- License: Apache-2.0 (package.json / GitHub SPDX)
- Host: box Node 20 / `npx -y chrome-devtools-mcp@1.12.0`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio
- Outcome: initialize OK (`serverInfo.name=chrome_devtools`, version 1.12.0); tools/list returned click/close_page/...
- Uninstall: removed verify dirs and `~/.npm/_npx` cache for this pass
