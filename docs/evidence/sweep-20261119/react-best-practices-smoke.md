# vercel-labs/agent-skills react-best-practices smoke (2026-11-16 Asia/Shanghai)

- Upstream repo commit `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` (2026-10-27; tip unchanged since the 2026-11-02 lead)
- Path: `skills/react-best-practices/` (SKILL.md, README.md, AGENTS.md, metadata.json, rules/*)
- Frontmatter: `name: vercel-react-best-practices`, `license: MIT`, `metadata.version: 1.0.0`, author vercel
- License: MIT is declared in SKILL.md frontmatter; no repository-root LICENSE file is present at this commit (GitHub `license` field is null). Record as MIT with that limitation; do not invent a LICENSE file.
- Host: box / downloaded GitHub archive at the pinned commit, validated SKILL.md frontmatter and the rules tree (40+ rule files)
- Outcome: skill tree present and well-formed; no runtime host install beyond archive extract
- Uninstall: removed the downloaded archive and extract from the sweep workdir.
- Limits: not exercised inside Cursor/Claude as a loaded skill. Repo tip has not moved since 2026-10-27. The parent repo also publishes a public AGENTS.md (in scope as a prompt convention file, same repo — do not file a second resource for it unless treated as a distinct prompt entry after review).

## 2026-11-17 reconfirm

- 2026-11-17: tip still `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` (unchanged since 2026-10-27). Pin unchanged.

## 2026-11-18 reconfirm

- 2026-11-18: tip still 1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62 (unchanged since 2026-10-27). Pin unchanged.

## 2026-11-19 reconfirm

- 2026-11-19: pack tip still `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62` (identical). There are snapshot GitHub “releases” named `agent-skills-<sha>`; the chronologically later pack commit on default branch is still `1a2c79d4` (published 2026-10-28 05:40 CST). Keep this SHA. MIT declared in SKILL.md frontmatter only; repo has no LICENSE file; do not invent one. Do not also add an AGENTS.md row. 未重测.
