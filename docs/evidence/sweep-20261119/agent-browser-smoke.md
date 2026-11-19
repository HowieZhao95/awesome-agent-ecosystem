# vercel-labs/agent-browser smoke (2026-11-16 Asia/Shanghai)

- Upstream tag `v0.43.0` → commit `1cc19526f3641c8543d55aa6700e7c55b37ac356`
- npm: `agent-browser@0.43.0` (Apache-2.0, bin agent-browser)
- Tip at check may be ahead of this release tag; pin the tag, not tip
- License: Apache-2.0 (npm + repo)
- Host: box Node v24.22.1 / `npx -y agent-browser@0.43.0`
- Commands: `--version` → `agent-browser 0.43.0`; `--help` OK; `skills list` returned bundled skills (core, electron, slack, …) without installing Chrome; MCP `agent-browser mcp` initialize OK (`serverInfo.name=agent-browser` version 0.43.0) and tools/list returned 33 tools (`agent_browser_open`, `agent_browser_snapshot`, …)
- Outcome: CLI + MCP are one distribution unit (do not add a second row). Handshake did not require `agent-browser install`.
- Uninstall: removed this pass's `~/.npm/_npx` cache; no `agent-browser install` / no Chrome for Testing download; no global install.
- Limits: no page-open or browser automation scenario; no Chrome binary installed this pass. Distinct from Playwright MCP and Chrome DevTools MCP.

## 2026-11-17 reconfirm

- 2026-11-17: npm latest still `agent-browser@0.43.0`; tag `v0.43.0` still `1cc19526f3641c8543d55aa6700e7c55b37ac356`. Tip `b06e2533ba9b3823b8a96c859d455cb55f4d7893` (2026-11-17 05:12 CST, docs og:video) is ahead — pin the release, not tip.

## 2026-11-18 reconfirm

- 2026-11-18: latest release still tag v0.43.0 / 1cc19526f3641c8543d55aa6700e7c55b37ac356 / npm agent-browser@0.43.0. Pin unchanged; 2026-11-16 smoke still applies; not re-run today.
- Tip at check (NOT the pin): f85ed4d620c53ace7733a3b7eeef51e5f2532c83 (2026-11-18 09:18 CST), ahead of the pin (moved from 11-17 tip b06e2533).

## 2026-11-19 reconfirm

- 2026-11-19 11:10 CST: latest still tag `v0.43.0` / `1cc19526f3641c8543d55aa6700e7c55b37ac356`; npm `agent-browser@0.43.0` unchanged. Pin unchanged; prior MCP handshake (33 tools) not re-run (未重测). Still did not run `agent-browser install` / download Chrome.
- Tip at check (NOT the pin): `a897b24d7e6624ed7e5d6ef1eed836f7200f4b40` (2026-11-19 10:39 CST, Reject unknown command flags #2665), 22 commits ahead of the pin (11-18 tip was `f85ed4d6…`).
