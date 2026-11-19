# github-mcp-server smoke (2026-11-17 Asia/Shanghai)

- Upstream release tag `v2.2.0` → commit `67d4dc489700ec955ad255d098396dd86c729523` (published 2026-11-16T23:30:46Z = 2026-11-17 07:30 CST). Binary `--version` reports the same commit and Build Date 2026-11-16T23:14:14Z.
- Distribution: official Linux x86_64 binary `github-mcp-server_Linux_x86_64.tar.gz` from the GitHub release (sha256 `157c5664b273e5070126d414f88cbab765630acde588f75dafdf9998c2235c51`). Official remote MCP is the same unit.
- Previous lead (2026-11-16, not landed): v2.1.0 / `4bcdcdf8d7beee98c9448e73e257308280924cc4`
- Tip `main` at check equals the release commit (commit date 2026-11-16 20:36 CST, message “Add public agent automation tools (#3719)”). Still record that tip may move; do not treat moving main as the pin.
- License: MIT (LICENSE in the release tarball; first line “MIT License”, Copyright (c) 2025 GitHub)
- Host: box Linux x86_64 / `./github-mcp-server stdio` (no GitHub token supplied)
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing)
- Outcome: initialize OK (`serverInfo.name=github-mcp-server`, version `2.2.0`); tools/list returned 46 default-toolset tools (issues/PRs/repos/users etc.), including write tools such as `create_pull_request` and `merge_pull_request`. Tool count matches the 2.1.0 smoke.
- Uninstall: deleted the downloaded tarball, extracted binary, LICENSE, and README from the sweep workdir; no global install. Kept only `release.json` metadata and the smoke JSON.
- Limits: handshake only; no live GitHub API tool call. Official remote server and OAuth/PAT are the usual host path. Prefer `--read-only` unless write tools are required.

## 2026-11-18 reconfirm

- 2026-11-18: latest release still tag v2.2.0 / commit 67d4dc489700ec955ad255d098396dd86c729523. Pin unchanged; 2026-11-17 smoke still applies; not re-run today.
- Tip at check (NOT the pin): 4e6e6c053e48aac182f7768162fef2ad42fe7d5f (2026-11-18 05:41 CST), 1 commit ahead of the release (on 11-17 tip equaled the release).

## 2026-11-19 reconfirm

- 2026-11-19 11:10 CST: latest stable still tag `v2.2.0` / `67d4dc489700ec955ad255d098396dd86c729523`. Do not pin v2.1.0. Pin unchanged; 2026-11-17 smoke still applies; not re-run today (未重测).
- Tip at check (NOT the pin): `df32d7ec5786e0e71932767fce9982409cbaec40` (2026-11-18 23:33 CST, Add experimental pull request artifact tools #3843), 2 commits ahead of the pin (11-18 tip was `4e6e6c05…`, +1).
