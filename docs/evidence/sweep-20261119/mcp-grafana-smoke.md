# grafana/mcp-grafana smoke (2026-11-18 Asia/Shanghai)

- Upstream tag `v2.3.0` → commit `c8cafb67854c45e79f8f9b5fca7d9b3a403f1771`. GitHub release published 2026-11-11 01:45 CST. Apache-2.0. No official npm package.
- Binary: GitHub release asset `mcp-grafana_Linux_x86_64.tar.gz` (sha256 `f808ea13d236e549a9fffa14b28398d30b5393623141307c916e26f5e7746671`, matches `mcp-grafana_2.3.0_checksums.txt`). `./mcp-grafana --version` → `2.3.0`. Default transport is stdio.
- Host: box x86_64 / `./mcp-grafana` with **no** `GRAFANA_URL`, no API token, no basic auth. `az` / Grafana cloud credentials were not used.
- Commands: JSON-RPC `initialize` then `tools/list` over stdio (newline framing) via `mcp_smoke.py` (`smoke/mcp-grafana-2.3.0.json`). Timeout 60s.
- Outcome: **smoke_ok**. initialize OK (`serverInfo.name=mcp-grafana` version `2.3.0`, protocol `2024-11-05`); tools/list returned **80** tools (full list in the JSON; includes `search_dashboards`, `query_prometheus`, `list_datasources`, `user_info`, etc.). GRAFANA_URL / token were **not** required to initialize. stderr reports `Using Grafana configuration url=http://localhost:3000 api_key_set=false basic_auth_set=false org_id=0`. No live Grafana API queries were issued. stderr also noted anonymous usage statistics to Grafana Labs (opt-out flags `--usage-stats=disabled` / `GRAFANA_USAGE_STATS=disabled`); no Grafana URL, credentials, or tool arguments are said to be sent.
- Uninstall: deleted `smoke-bin/mcp-grafana`, the tarball, checksums, and extracted LICENSE/README/CHANGELOG with the rest of `smoke-bin/`. Binary was never installed to PATH.
- Limits: no live Grafana instance; default URL is localhost:3000 with no API key. Tool calls against Grafana were not exercised.

## 2026-11-19 reconfirm

- Correction: this is grafana/mcp-grafana, not Notion MCP. The 11-18 SHA `c8cafb67854c45e79f8f9b5fca7d9b3a403f1771` / tag `v2.3.0` / 80 tools belongs to Grafana MCP (no official npm). Notion remains a Hold (`@notionhq/notion-mcp-server@2.6.1` / gitHead `cf16e5c20bfbfb98ecec1227f210ef0ae3abebe5`; GitHub “latest” release still stale v2.1.0).
- 2026-11-19: latest stable still `v2.3.0` / `c8cafb67854c45e79f8f9b5fca7d9b3a403f1771`. Pin unchanged; 2026-11-18 binary smoke still applies; 未重测.
- Tip at check (NOT the pin): `70b04944ed598cfa811d168d7b96a797fd3ee291` (2026-11-18 21:34 CST), 50 commits ahead (11-18 tip was `337b187158c4d695965cc1ea4d8723cd9d51b339`).
