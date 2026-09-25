#!/usr/bin/env python3
"""Sample-based link checker for data/resources.yaml.

Usage:
    python3 scripts/link-check.py --sample 50
    python3 scripts/link-check.py            # full check (slow)

Never blocks the pipeline by itself: exits 0 always, prints a report.
Dead links are reported for human triage in the weekly PR.
"""
import argparse
import os
import random
import sys
import urllib.request

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "resources.yaml")

parser = argparse.ArgumentParser()
parser.add_argument("--sample", type=int, default=0)
args = parser.parse_args()

doc = yaml.safe_load(open(DATA, encoding="utf-8"))
entries = [(c["id"], e) for c in doc["categories"] for e in c["entries"]]
if args.sample and args.sample < len(entries):
    entries = random.Random(42).sample(entries, args.sample)

dead = []
for i, (cid, e) in enumerate(entries):
    url = e.get("url", "")
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "link-check"})
        with urllib.request.urlopen(req, timeout=15) as r:
            code = r.status
    except Exception as ex:
        code = str(getattr(ex, "code", "ERR"))
    if code != 200:
        dead.append(f"[{cid}] {e['name']} -> {url} ({code})")

print(f"checked {len(entries)} urls, dead: {len(dead)}")
for line in dead:
    print(" DEAD:", line)
