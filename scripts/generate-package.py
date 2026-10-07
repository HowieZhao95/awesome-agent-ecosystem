#!/usr/bin/env python3
"""Generate public literal unions from the catalog YAML sources."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    executable = os.environ.get("PYTHON", sys.executable)
    script = "import yaml, json, pathlib; root=pathlib.Path('.')"
    command = [executable, "-c", script + "; c=yaml.safe_load((root/'data/categories.yaml').read_text()); d=c['dimensions']; vals={'CategoryId':[x['id'] for x in c['categories']], 'SubtypeId':[s['id'] for x in c['categories'] for s in x.get('subtypes',[])], 'DomainId':[x['id'] for x in d['domains']], 'FormatId':[x['id'] for x in d['formats']], 'ConventionId':[x['id'] for x in d['conventions']], 'ComponentTypeId':[x['id'] for x in d['plugin_component_types']]}; print(json.dumps(vals, ensure_ascii=False))"]
    try:
        output = subprocess.check_output(command, cwd=ROOT, text=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        if "No module named 'yaml'" not in error.stderr:
            raise
        fallback = "/Applications/Xcode.app/Contents/Developer/usr/bin/python3"
        output = subprocess.check_output([fallback, *command[1:]], cwd=ROOT, text=True)
    import json
    values = json.loads(output)
    lines = ["// Generated from data/categories.yaml; do not edit."]
    for name, items in values.items():
        lines.append(f"export const {name[0].upper() + name[1:]}Values = {json.dumps(items, ensure_ascii=False)} as const;")
        lines.append(f"export type {name} = typeof {name[0].upper() + name[1:]}Values[number];")
    target = ROOT / "src/generated/enums.ts"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
