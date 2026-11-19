# context7-mcp smoke (2026-11-18 Asia/Shanghai)

- Upstream npm `@upstash/context7-mcp@4.7.3` → commit `c36522f3d4446288a272aedd727d665f7b8175f2` (`packages/mcp/package.json` version 4.7.3 at this commit; tags `mcpb-v4.7.3` and `@upstash/context7-mcp@4.7.3` both peel to this SHA; npm published 2026-11-17 21:56 CST; GitHub release published 2026-11-17 21:51 CST). Do not pin 4.7.0, 4.7.1, or 4.7.2.
- Previous catalog pin (main): commit `c7f80ce5af1ff1403d167579b76784482cf7f3e2` / `@upstash/context7-mcp@4.4.4`
- Previous evaluated but unlanded pin (2026-11-17): `@upstash/context7-mcp@4.7.1` / `72844e51c4f039b9ef14e980da3f0f84ab89331e`
- Tip equals this pin: `c36522f3d4446288a272aedd727d665f7b8175f2` (2026-11-17 21:50 CST, `chore(release): version packages (#3850)`).
- License: MIT (package.json license=MIT; installed LICENSE is The MIT License (MIT), Copyright (c) 2021 Upstash, Inc.)
- Host: box Node v24.22.1 / `npx -y @upstash/context7-mcp@4.7.3`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing) via `mcp_smoke.py` (`smoke/context7-4.7.3.json`)
- Outcome: initialize OK (`serverInfo.name=Context7` version `4.7.3`); tools/list returned 2 tools: `resolve-library-id`, `query-docs`. Same tool set as 4.7.1 / 4.7.0. stderr: `Context7 Documentation MCP Server v4.7.3 running on stdio`.
- Uninstall: removed this pass's `~/.npm/_npx/096c425e3a4cd48f` cache dir (wrapper depended only on `@upstash/context7-mcp@4.7.3`); no persistent global install.
- Limits: no live Context7 docs API query; no Cursor/Claude Desktop host config. Tip currently equals this pin.

## 2026-11-19 reconfirm

- 2026-11-19 11:10 CST: latest npm still `@upstash/context7-mcp@4.7.3` (2026-11-17 21:56 CST, gitHead null). GitHub tags `mcpb-v4.7.3` and `@upstash/context7-mcp@4.7.3` still peel to `c36522f3d4446288a272aedd727d665f7b8175f2`. Do NOT pin 4.7.0, 4.7.1, or 4.7.2. Pin unchanged; 2026-11-18 smoke still applies; not re-run today (未重测).
- Tip `master` at check (NOT the pin): `018a603bc99d4cd21feaac1021501185d092ac09` (2026-11-18 20:02 CST). Tip moved past the 4.7.3 pin (on 11-18 tip equaled the pin).
