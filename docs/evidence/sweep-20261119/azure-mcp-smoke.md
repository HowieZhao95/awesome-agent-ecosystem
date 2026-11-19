# @azure/mcp smoke (2026-11-18 Asia/Shanghai)

- Upstream tag `Azure.Mcp.Server-3.0.0` → commit `61715e6a9054d7922809b01e08a2efa85e032a6d` (tag peel; GitHub release published 2026-10-13 06:22 CST). MIT.
- npm: `@azure/mcp@3.0.0` (published 2026-10-13 06:37 CST). npm `dist-tag latest` is `4.0.0-beta.9` and was **not** installed. Installed platform package was `@azure/mcp-linux-x64@3.0.0`. npm `gitHead` is not published on this packument.
- CLI `--version` on this exact npm pin reports `3.0.0+6369a8a7a9822e804f4986f67619dfcd28fc815b`. That informational SHA is a same-day follow-up commit on `microsoft/mcp` (2026-10-13 04:22 CST, changelog for the 3.0.0 release) after the tag commit (2026-10-13 02:30 CST). Handshake `serverInfo.version` is `3.0.0`.
- Host: box Node v24.22.1 / `npx -y @azure/mcp@3.0.0 server start` (transport default stdio). No `az login`, no Azure credentials, no `--cloud` override. `az` / `azd` are not installed.
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing) via `mcp_smoke.py` (`smoke/azure-mcp-3.0.0.json`). Timeout 60s.
- Outcome: **smoke_ok**. initialize OK (`serverInfo.name=Azure MCP Server` version `3.0.0`, protocol `2024-11-05`); tools/list returned **69** tools, including `documentation`, `subscription_list`, `group_list`, `storage`, `keyvault`, `monitor`, and `get_azure_bestpractices` (full list in the JSON). No Azure API calls were made beyond the handshake. Credentials were not required to initialize.
- Uninstall: removed this pass's `~/.npm/_npx/cbca79aed338c74f` cache dir (wrapper depended only on `@azure/mcp@3.0.0`). No global npm or dotnet tool install. No `~/.azure` / `~/.nuget` leftover.
- Limits: no live Azure resource operations; no Cursor/Claude Desktop host config. This is the 3.0.0 pin, not the 4.0.0 beta.

## 2026-11-19 reconfirm

- 2026-11-19: no newer non-beta Azure MCP Server release. Tag `Azure.Mcp.Server-3.0.0` still peels to `61715e6a9054d7922809b01e08a2efa85e032a6d`. Tags 3.0.1 and 3.1.0 do not exist. npm `@azure/mcp@3.0.0` still published (not deprecated). Pin unchanged; 2026-11-18 smoke (69 tools, no az login) still applies; 未重测.
- Do NOT pin npm dist-tag `latest`, which is `4.0.0-beta.9` (2026-11-18 09:41 CST). GitHub release `Azure.Mcp.Server-4.0.0-beta.9` is marked `prerelease=false` on GitHub but the name is beta — still not the pin.
- Tip at check (NOT the pin): `0e0945a19be7efd99ffe0ae17625e70f1b8f221d` (2026-11-19 04:34 CST), 167 commits ahead of 3.0.0 (6 commits ahead of the beta.9 tag).
