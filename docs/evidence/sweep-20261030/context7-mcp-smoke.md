# context7-mcp smoke (2026-10-30 Asia/Shanghai)

- Upstream tag `@upstash/context7-mcp@4.4.4` → commit `c7f80ce5af1ff1403d167579b76784482cf7f3e2`
- npm: `@upstash/context7-mcp@4.4.4`
- License: MIT (root LICENSE + package.json)
- Host: box Node / `npx -y @upstash/context7-mcp@4.4.4`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing)
- Outcome: initialize OK (`serverInfo.name=Context7` version 4.4.4); tools/list returned 2 tools: `resolve-library-id`, `query-docs`
- Uninstall: removed `~/.npm/_npx` cache for this pass; no persistent global install
- Limits: no live Context7 API query; no Cursor/Claude Desktop host config
