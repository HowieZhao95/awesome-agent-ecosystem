#!/usr/bin/env python3
"""Quality gate: schema & curation-rule validation for data/resources.yaml.

Rules (fail CI on violation):
  1. required fields present: name / url / source / platform / note
  2. source in {official, vendor, community}; vmethod in {manual, automated} when present
  3. name globally unique (case-insensitive)
  4. asset categories must not link to known collection/blacklist repos
  5. platforms category is exempt from rule 4

Exit 0 = pass, 1 = violations found.
"""
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "resources.yaml")

REQUIRED = ["name", "url", "source", "platform", "note"]
SOURCES = {"official", "vendor", "community"}
VMETHODS = {"manual", "automated"}

# 合集黑名单：资产类条目不得指向这些（发现渠道归 platforms）
COLLECTION_BLACKLIST = [
    "github.com/hesreallyhim/awesome-claude-code",
    "github.com/punkpeye/awesome-mcp-servers",
    "github.com/ComposioHQ/awesome-claude-skills",
    "github.com/travisvn/awesome-claude-skills",
    "github.com/kyrolabs/awesome-agents",
    "github.com/quemsah/awesome-claude-plugins",
    "github.com/rohitg00/awesome-claude-code-toolkit",
    "github.com/f/awesome-chatgpt-prompts",
    "github.com/PatrickJS/awesome-cursorrules",
    "github.com/ItamarZand88/awesome-agent-conventions",
    "github.com/VoltAgent/awesome-design-md",  # 合集本身；具体规范允许 tree/main/design-md/<brand>
]

doc = yaml.safe_load(open(DATA, encoding="utf-8"))
errors = []
seen = {}

for cat in doc["categories"]:
    is_platform = cat["id"] == "platforms"
    for i, e in enumerate(cat["entries"]):
        where = f"[{cat['id']}] #{i} {e.get('name', '?')}"

        for f in REQUIRED:
            if not e.get(f):
                errors.append(f"{where}: missing required field '{f}'")

        if e.get("source") not in SOURCES:
            errors.append(f"{where}: bad source '{e.get('source')}'")

        if e.get("vmethod") and e["vmethod"] not in VMETHODS:
            errors.append(f"{where}: bad vmethod '{e['vmethod']}'")

        key = (e.get("name") or "").strip().lower()
        if key in seen:
            errors.append(f"{where}: duplicate name (also in [{seen[key]}])")
        else:
            seen[key] = cat["id"]

        if not is_platform:
            url = e.get("url") or ""
            for bad in COLLECTION_BLACKLIST:
                # 指向合集内具体子路径（/tree/...、/blob/...）视为合法资产链接
                if bad in url and "/tree/" not in url and "/blob/" not in url:
                    errors.append(f"{where}: URL points to collection ({bad}), move to platforms or fix link")

if errors:
    print(f"FAIL: {len(errors)} violation(s)")
    for line in errors[:50]:
        print(" -", line)
    sys.exit(1)

total = sum(len(c["entries"]) for c in doc["categories"])
print(f"PASS: {total} entries, all rules satisfied")
