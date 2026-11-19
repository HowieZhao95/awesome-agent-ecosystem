# agent-desktop smoke (2026-11-18 Asia/Shanghai)

- Upstream tag `v1.3.1` → commit `b0b7277bea09b770ef9d1fb45aad667bc432cd57`. GitHub release published 2026-11-14 05:02 CST. Apache-2.0.
- npm: `agent-desktop@1.3.1` (published 2026-11-14 05:15 CST). npm `gitHead` equals the pin: `b0b7277bea09b770ef9d1fb45aad667bc432cd57`. Distinct from already-scored **agent-browser**; not merged.
- Host: box Node v24.22.1 / `npx -y agent-desktop@1.3.1`. `DISPLAY=:9` is set on this box (X sockets present); this was not a display-less environment, but the MCP handshake itself did not require a desktop login or extra secrets.
- Commands:
  - `npx -y agent-desktop@1.3.1 --version` → `agent-desktop 1.3.1` (saved `smoke/agent-desktop-1.3.1-version.txt`).
  - `npx -y agent-desktop@1.3.1 --help` OK; includes an `mcp` subcommand: "Serve every command as an MCP tool over stdio" (saved `smoke/agent-desktop-1.3.1-help.txt`).
  - JSON-RPC `initialize` then `tools/list` via `mcp_smoke.py` on `npx -y agent-desktop@1.3.1 mcp` (`smoke/agent-desktop-1.3.1.json`). Timeout 60s.
- Outcome: **smoke_ok** (CLI and MCP handshake). initialize OK (`serverInfo.name=agent-desktop` version `1.3.1`, protocol `2024-11-05`); tools/list returned **75** tools (`desktop_snapshot`, `desktop_click`, `desktop_status`, `desktop_version`, sandbox/session/skills tools, etc.; full list in the JSON). No desktop UI actions were invoked after the handshake. This is not a partial/headless-failure result.
- Uninstall: removed this pass's `~/.npm/_npx/6ff9600ef29ffc97` cache dir (wrapper depended only on `agent-desktop@1.3.1`). No `~/.agent-desktop` leftover. No global npm install.
- Limits: no live window/click operations; accessibility permission / headed input was not exercised. Do not merge this row with agent-browser.

## 2026-11-19 reconfirm

- 2026-11-19: latest still tag `v1.3.1` / `b0b7277bea09b770ef9d1fb45aad667bc432cd57`; npm `agent-desktop@1.3.1` gitHead matches. Pin unchanged; 2026-11-18 smoke (CLI + MCP 75 tools) still applies; 未重测. Not the same row as agent-browser.
- Tip at check (NOT the pin): still `e8934a5e95e1d212c74ead95cd3e4701c04eca31` (2026-11-18 07:25 CST), 6 commits ahead — unchanged since 11-18.
