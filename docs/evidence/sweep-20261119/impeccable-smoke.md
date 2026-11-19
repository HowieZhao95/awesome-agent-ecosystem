# pbakaus/impeccable smoke (2026-11-19 Asia/Shanghai)

- Upstream tag `cli-v4.10.0` → commit `ab3617920fcdb5009163a725ba8ff59927a63474` (annotated tag “CLI 4.10.0”, tagger 2026-11-19 05:27 CST)
- npm: `impeccable@4.10.0` (published 2026-11-19 05:57 CST, gitHead null; package.json name impeccable, license Apache-2.0, bin impeccable). npm version command reported `4.10.0`.
- Previous intended pin (11-16/18): tag `cli-v4.9.2` / `bba37e8ff05a099ae8f72db929453b31c82bef20` / npm `impeccable@4.9.2`
- Same-day sibling tags (NOT this row's pin): `skill-v4.10.0` peels to tip `b49177d32788f2dc585c42831d845dacf1ebed2c` (2026-11-19 05:58 CST); `engine-v0.1.27` / `645925acd71b18558488c5b8d8f263404cb68db8`; `loop-v0.2.0`. Pin the CLI release, not tip or the skill/engine/loop tags.
- License: Apache-2.0 (package.json; repository license Apache-2.0)
- Host: box Node v24.22.1 / `npx -y impeccable@4.10.0`
- Commands: `--version` → `4.10.0`; `--help` lists detect/ignores/help/install/link/update/check/telemetry/login/logout/whoami/status/walkthrough/world/health/foundations
- Outcome: CLI starts and reports the pinned version. Did **not** run `impeccable install` (would write skills into a project/harness).
- Uninstall: removed this pass's `~/.npm/_npx` cache dirs; no global install.
- Limits: no detect scan of a real UI, no account login, no skill-harness install.
