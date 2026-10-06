#!/usr/bin/env python3
"""Legacy quality gate for data/discovery/legacy-v2.yaml.

Rules (fail CI on violation):
  1. required fields present: name / url / source / platform / note
  2. source in {official, vendor, community}; vmethod in {manual, automated} when present
  3. name globally unique (case-insensitive)
  4. asset categories must not link to known collection/blacklist repos
  5. platforms category is exempt from rule 4

Exit 0 = pass, 1 = violations found.
"""
import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "discovery" / "legacy-v2.yaml"

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

def validate_discovery(path=DATA):
    with Path(path).open(encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    errors = []
    seen = {}
    for cat in doc["categories"]:
        is_platform = cat["id"] == "platforms"
        for i, entry in enumerate(cat["entries"]):
            where = f"[{cat['id']}] #{i} {entry.get('name', '?')}"
            for field in REQUIRED:
                if not entry.get(field):
                    errors.append(f"{where}: missing required field '{field}'")
            if entry.get("source") not in SOURCES:
                errors.append(f"{where}: bad source '{entry.get('source')}'")
            if entry.get("vmethod") and entry["vmethod"] not in VMETHODS:
                errors.append(f"{where}: bad vmethod '{entry['vmethod']}'")
            key = (entry.get("name") or "").strip().lower()
            if key in seen:
                errors.append(f"{where}: duplicate name (also in [{seen[key]}])")
            else:
                seen[key] = cat["id"]
            if not is_platform:
                url = entry.get("url") or ""
                for bad in COLLECTION_BLACKLIST:
                    if bad in url and "/tree/" not in url and "/blob/" not in url:
                        errors.append(f"{where}: URL points to collection ({bad}), move to platforms or fix link")
    return sum(len(category["entries"]) for category in doc["categories"]), errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    args = parser.parse_args()
    try:
        total, errors = validate_discovery(args.data)
    except (OSError, yaml.YAMLError) as exc:
        parser.exit(1, f"ERROR: cannot read discovery queue: {exc}\n")
    if errors:
        print(f"FAIL: {len(errors)} violation(s)")
        for line in errors[:50]:
            print(" -", line)
        return 1
    print(f"PASS: {total} discovery entries, all rules satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
