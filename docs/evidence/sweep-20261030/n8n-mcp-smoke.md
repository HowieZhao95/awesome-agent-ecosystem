# n8n-mcp smoke (2026-10-30 Asia/Shanghai)

- Upstream tag `v2.99.2` → commit `09611fd663f17fe6976a0e027178421abbb2f041`
- npm: `n8n-mcp@2.99.2`
- License: MIT (root LICENSE + package.json)
- Host: box Node / `npx -y n8n-mcp@2.99.2`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing)
- Outcome: initialize OK (`serverInfo.name=n8n-documentation-mcp` version 2.99.2); tools/list returned 7 tools including `search_nodes`, `get_node`, `validate_workflow`
- Uninstall: removed `~/.npm/_npx` cache for this pass; no persistent global install
- Limits: documentation MCP only this mode; no live n8n instance API; no full workflow deploy scenario
