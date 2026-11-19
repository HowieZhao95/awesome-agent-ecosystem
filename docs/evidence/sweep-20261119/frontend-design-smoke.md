# anthropics/skills frontend-design smoke (2026-11-16 Asia/Shanghai)

- Upstream repo commit `1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064` (2026-11-14, "Update docx, pptx, xlsx, and pdf skills")
- Path: `skills/frontend-design/` (`SKILL.md` + `LICENSE.txt`)
- Skill file blob SHA `a5333457c414d20d625f307df945842c0952ecc3` (9390 bytes) is unchanged since the earlier lead pin `ca45fc49`
- License: Apache-2.0 (skill `LICENSE.txt` is Apache License 2.0 text; frontmatter says "Complete terms in LICENSE.txt")
- Host: box / downloaded GitHub archive at the pinned commit, validated SKILL.md frontmatter (`name: frontend-design`) and license file presence
- Outcome: skill tree present and well-formed; no runtime host install (copy-the-folder / skills CLI per upstream docs)
- Uninstall: removed the downloaded archive and extract from the sweep workdir.
- Limits: not exercised inside Cursor/Claude as a loaded skill. Pin the repo commit above; do not treat moving `main` as the pin. Skill *content* has not drifted since `ca45fc49`.

## 2026-11-17 reconfirm

- 2026-11-17: repo tip moved to `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`, but compare `1780c5e5…`→tip does not touch `skills/frontend-design/`. SKILL.md still 9390 bytes, frontmatter name `frontend-design`. Keep pin `1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064`. LICENSE.txt still Apache-2.0.

## 2026-11-18 reconfirm

- 2026-11-18: anthropics/skills tip still e4bb5d960d87126ff3b3a8af1a104b7db67560ba. Path skills/frontend-design/ last commit still 41bbe19d; unchanged vs pin 1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064.

## 2026-11-19 reconfirm

- 2026-11-19: anthropics/skills tip still `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` (identical to 11-18). frontend-design path pin remains `1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064` (path unchanged at tip; tip is 1 commit ahead of 1780c5e5 because document-skills changed). No new tag/release. Not re-inspected beyond SHA/tip check (未重测).
