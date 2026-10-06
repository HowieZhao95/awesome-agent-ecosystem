#!/usr/bin/env python3
"""Sample-based link checker for the legacy discovery queue."""
import argparse
import random
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "discovery" / "legacy-v2.yaml"


def check_links(data=DATA, sample=0):
    with Path(data).open(encoding="utf-8") as handle:
        doc = yaml.safe_load(handle)
    entries = [(category["id"], entry) for category in doc["categories"] for entry in category["entries"]]
    if sample and sample < len(entries):
        entries = random.Random(42).sample(entries, sample)
    dead = []
    for category_id, entry in entries:
        url = entry.get("url", "")
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "link-check"})
            with urllib.request.urlopen(req, timeout=15) as response:
                code = response.status
        except Exception as exc:
            code = str(getattr(exc, "code", "ERR"))
        if code != 200:
            dead.append(f"[{category_id}] {entry['name']} -> {url} ({code})")
    return len(entries), dead


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument("--data", type=Path, default=DATA)
    args = parser.parse_args()
    try:
        checked, dead = check_links(args.data, args.sample)
    except (OSError, yaml.YAMLError) as exc:
        parser.exit(1, f"ERROR: cannot read discovery queue: {exc}\n")
    print(f"checked {checked} urls, dead: {len(dead)}")
    for line in dead:
        print(" DEAD:", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
