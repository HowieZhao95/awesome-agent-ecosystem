# anthropics document-skills smoke (2026-11-17 Asia/Shanghai)

- Upstream: https://github.com/anthropics/skills path unit `.claude-plugin/marketplace.json` plugin `document-skills` (skills `./skills/xlsx`, `./skills/docx`, `./skills/pptx`, `./skills/pdf`)
- Pin: repo commit `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` (2026-11-16 22:22 CST, “Update docx, pptx and xlsx skills: zipfile unpack, zip -y, validate.py and soffice.py fixes (#2221)”)
- Compared to previous unlanded pin `1780c5e5a552fd4d1c9d6a7b0cab26b0c2bef064`: ahead by 1 commit, 8 files. Changed: `skills/docx/SKILL.md` (+7), `skills/pptx/SKILL.md` (+4), and `scripts/office/soffice.py` + `validate.py` under docx/pptx/xlsx. `skills/pdf/` unchanged in this commit.
- marketplace.json still lists one `document-skills` plugin (xlsx/docx/pptx/pdf) plus sibling plugins (`example-skills`, etc.). Do not split into four skill rows. `metadata.version` remains 1.0.0 (not used as a release pin).
- License: Apache-2.0 via per-skill `LICENSE.txt` (confirmed `skills/docx/LICENSE.txt` header “Apache License Version 2.0”). Repo has no root LICENSE. Frontmatter names: docx / pptx / xlsx / pdf; license line points at LICENSE.txt.
- Verification: source-inspected at the new tip (fetched SKILL.md + marketplace.json + LICENSE header). Not loaded into a host; office scripts were not executed.
- Limits: source inspection only. Sibling official skills (frontend-design, mcp-builder, skill-creator) did not change in this commit and stay pinned at `1780c5e5…`.

## 2026-11-18 reconfirm

- 2026-11-18: tip still e4bb5d960d87126ff3b3a8af1a104b7db67560ba. document-skills paths (docx/pptx/xlsx last commit equals this tip; pdf last 1780c5e5) unchanged. Keep pin e4bb5d96.

## 2026-11-19 reconfirm

- 2026-11-19: tip still equals the document-skills pin `e4bb5d960d87126ff3b3a8af1a104b7db67560ba`. Keep as ONE plugin row (xlsx/docx/pptx/pdf), never four rows. No new tag/release. 未重测.
