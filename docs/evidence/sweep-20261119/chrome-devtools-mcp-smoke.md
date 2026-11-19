# chrome-devtools-mcp smoke (2026-11-16 Asia/Shanghai)

- Upstream release tag `chrome-devtools-mcp-v1.13.0` / npm gitHead `b1e35e3ab1774664dfc66a2cb813a392535fe160`
- npm: `chrome-devtools-mcp@1.13.0` (GitHub release published 2026-11-11T12:40:09Z)
- Previous catalog pin: commit `bc0d93ee2df6f2410d9e9704903c3547acae7c9a` / `chrome-devtools-mcp@1.12.0`
- Tip `main` at check: `8ba2ac945ebaf1adb92208c29f3a30e73a920956` (2026-11-13, ahead of the release tag; not used as pin)
- License: Apache-2.0 (package.json / GitHub SPDX)
- Host: box Node v24.22.1 / `npx -y chrome-devtools-mcp@1.13.0`
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing)
- Outcome: initialize OK (`serverInfo.name=chrome_devtools`, version `1.13.0`); tools/list returned 33 tools including `click`, `navigate_page`, `take_snapshot`, `get_css_styles`, `lighthouse_audit`
- Uninstall: removed this pass's `~/.npm/_npx` cache dirs and `~/.cache/chrome-devtools-mcp`; no global install.
- Limits: MCP handshake only; no live Chrome DevTools session. Tip may move past this pin. Server notes performance tools may call Google CrUX unless `--no-performance-crux`; file tools restricted without MCP roots (`--allow-unrestricted-paths` restores prior behavior).

## 2026-11-17 reconfirm

- npm latest still `chrome-devtools-mcp@1.13.0` / gitHead `b1e35e3ab1774664dfc66a2cb813a392535fe160` (tag `chrome-devtools-mcp-v1.13.0` peels to the same commit). Pin unchanged; 2026-11-16 smoke still applies; not re-run today.
- Tip `main` at check (NOT the pin): `dc0055828a9fcdcf8c3e65f7ecd1847c53fd972a` (2026-11-17 01:14 CST). Yesterday's tip-ahead `8ba2ac94…` has moved.

## 2026-11-18 reconfirm

- 2026-11-18: latest release still tag chrome-devtools-mcp-v1.13.0 / commit b1e35e3ab1774664dfc66a2cb813a392535fe160; npm chrome-devtools-mcp@1.13.0 gitHead unchanged. Pin unchanged; 2026-11-16 smoke still applies; not re-run today.
- Tip at check (NOT the pin): 4b9acc9961a081f462d6a30040b8af729b1d7dc3 (2026-11-18 04:32 CST), 30 commits ahead of the pin (moved from 11-17 tip dc005582).

## 2026-11-19 reconfirm

- 2026-11-19 11:10 CST: latest release still tag `chrome-devtools-mcp-v1.13.0` / commit `b1e35e3ab1774664dfc66a2cb813a392535fe160`; npm `chrome-devtools-mcp@1.13.0` gitHead unchanged. Pin unchanged; 2026-11-16 smoke still applies; not re-run today (未重测).
- Tip `main` at check (NOT the pin): `cf98d8b88d74bfaa684412625fc89b58626919a5` (2026-11-19 06:20 CST, feat: include computed styles in get_css_styles #3538), 41 commits ahead of the 1.13.0 pin (11-18 tip was `4b9acc9961a081f462d6a30040b8af729b1d7dc3`, +30).
