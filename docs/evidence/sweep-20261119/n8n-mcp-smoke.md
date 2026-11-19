# n8n-mcp smoke (2026-11-19 Asia/Shanghai)

- Upstream tag `v2.103.1` / npm gitHead `c0400c1c209b305482ee0cef6eaa234f4e611224` (tag peels to the same commit; tip equals the pin)
- npm: `n8n-mcp@2.103.1` (published 2026-11-18 20:47 CST)
- Previous intended pin (11-18, not yet on catalog main): tag `v2.103.0` / `54744be2c4fe9f1451d597e556d2628adc2b6c47`
- Catalog main pin still: commit `09611fd663f17fe6976a0e027178421abbb2f041` / `n8n-mcp@2.99.2`
- Release commit message: `chore: sync skills pack to n8n-skills 1.38.0 (2.103.1) (#1240)`
- License: MIT
- Host: box Node v24.22.1 / `npx -y n8n-mcp@2.103.1`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (ndjson)
- Outcome: initialize OK (`serverInfo.name=n8n-documentation-mcp`, version `2.103.1`); documentation-mode tools/list still **7** tools: `tools_documentation`, `search_nodes`, `get_node`, `validate_node`, `get_template`, `search_templates`, `validate_workflow`. `n8n_manage_variables` (added in 2.103.0) is still not listed without a live n8n API config; not exercised.
- JSON: `smoke/n8n-mcp-2.103.1.json`
- Uninstall: removed this pass's `~/.npm/_npx` cache dirs. No global install.
- Limits: documentation mode only; no live n8n instance.
