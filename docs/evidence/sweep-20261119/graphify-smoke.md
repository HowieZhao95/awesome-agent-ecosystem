# Graphify-Labs/graphify smoke (2026-11-18 Asia/Shanghai)

- Upstream tag `v0.9.112` → commit `340268a70a83588d6b3c6de1fffb05326350ef1d` (commit 2026-11-17 23:21 CST, `chore(release): bump version to 0.9.112`; GitHub published 2026-11-17 23:42 CST). Tip equals the tag.
- PyPI / uv package name is `graphifyy` (double y) version `0.9.112` (uploaded 2026-11-17 23:42 CST, yanked=false). After `uv tool install graphifyy==0.9.112` the executables are `graphify` and `graphify-mcp` (there is no `graphifyy` bin).
- License: Apache-2.0 declared (`License-Expression: Apache-2.0` in METADATA; `LICENSE` is Apache License 2.0). Tree / wheel also ships `LICENSE-MIT` (MIT License, Copyright 2026 Safi Shamsi) and `NOTICE` via `license-files`. Record Apache-2.0 as the declared package license and note the additional MIT file.
- Host: box Python 3.13.5 / uv 0.13.8 / `uv tool install graphifyy==0.9.112`
- Commands: `graphify --version` → `graphify 0.9.112`; `graphify --help` lists install/uninstall/path/explain/section/diagnose/clone/merge-*/add/watch/update/cluster-only/label/query/affected/god-nodes/… Did **not** run `graphify install` (would copy the skill into platform config dirs).
- Optional MCP: default tool install still does **not** include the `mcp` extra (`Provides-Extra: mcp`; `mcp`/`fastmcp` not present in the tool env). `graphify-mcp --help` prints the argparse help from `graphify.serve`, but running `graphify-mcp` exits 1 with `ImportError: mcp not installed. Run: pip install "graphifyy[mcp]"`. Handshake not completed; the extra was not installed.
- Skill path: `graphify/skill.md` (lowercase filename) frontmatter name `graphify`.
- Outcome: CLI install/version/help OK; skill file present. MCP handshake not available on the default install. One unit (CLI + skill).
- Uninstall: `uv tool uninstall graphifyy` (removed `graphify` and `graphify-mcp` from `~/.local/bin`); `uv tool list` empty afterwards; no leftover `~/.local/bin/graphify*`.
- Limits: no graph build over a real repo this pass; MCP extra not installed. Pin v0.9.112, which currently equals tip.

## 2026-11-19 reconfirm

- 2026-11-19: PyPI `graphifyy==0.9.112` still latest (uploaded 2026-11-17 23:42 CST, yanked=false); GitHub tag `v0.9.112` / `340268a70a83588d6b3c6de1fffb05326350ef1d`; tip equals the tag. Pin unchanged; 2026-11-18 CLI smoke still applies; 未重测.
- An older git tag `v1.0.0` / `0a31c0862b600d0755b0b8da41d6cdf99df135df` exists but is not the latest stable release (GitHub latest is v0.9.112). Do not pin v1.0.0. npm package `graphifyy@0.10.0` (2026-06-06) is a different/older registry artifact; official distribution is PyPI `graphifyy`.
