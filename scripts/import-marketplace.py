#!/usr/bin/env python3
"""Import legacy plugin candidates into the discovery queue.

Sources:
  1. anthropics/claude-plugins-official marketplace.json (Anthropic-vetted, import all)
  2. claude-plugins.dev API top downloads (community side, import downloads >= MIN_DOWNLOADS)

Rerunnable: dedupes against existing entries by normalized name.
The result remains a legacy discovery candidate. It is not promoted by build.py.

Usage:
    python3 scripts/import-marketplace.py
"""
import json
import os
import sys
import urllib.request
import datetime
import urllib.error
from urllib.parse import urlsplit, urlunsplit

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "data", "discovery", "legacy-v2.yaml")

OFFICIAL_URL = "https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json"
CPD_API = "https://claude-plugins.dev/api/plugins?limit=100&offset={}"
CPD_PAGES = 3
MIN_DOWNLOADS = 100
VERIFIED = str(datetime.date.today())
NOTE_MAX = 90

# claude-plugins.dev 的 category 字段 → 中文子类
CATEGORY_MAP = {
    "development": "开发", "productivity": "生产力", "database": "数据/数据库",
    "ai": "AI/记忆", "ai-agents": "AI/记忆", "design": "前端/设计",
    "devops": "云/运维", "security": "安全", "marketing": "营销/社媒",
    "docs": "文档/办公", "documentation": "文档/办公", "finance": "金融/商业",
    "search": "搜索/抓取", "communication": "协作/通讯", "media": "媒体/内容",
    "languages": "开发", "workflow": "生产力", "testing": "开发",
}

HEADER = """# Awesome Agent Ecosystem 历史发现队列（legacy v2）
# 批量导入只添加候选线索；旧 source/platform/vmethod 不表示新许可、审阅或运行验证。
# 新公共目录由 categories.yaml、sources.yaml、resources.yaml 单独定义。
# 本文件由 import-*.py 和 update-stars.py 维护，不由新目录 build.py 发布。
"""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-agent-ecosystem"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def trunc(text, n=NOTE_MAX):
    text = " ".join((text or "").split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0] + "…"


def norm(name):
    return (name or "").strip().lower()


def url_key(url):
    parts = urlsplit((url or "").strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    cats = {c["id"]: c for c in doc["categories"]}
    plugins_cat = cats["plugins"]
    existing = {norm(e["name"]) for c in doc["categories"] for e in c["entries"]}
    existing_urls = {url_key(e.get("url")) for c in doc["categories"] for e in c["entries"]}

    added_official = 0
    for p in fetch(OFFICIAL_URL).get("plugins", []):
        author = (p.get("author") or {}).get("name", "")
        src = p.get("source") or {}
        url = p.get("homepage") or (src.get("url") if isinstance(src, dict) else None) \
            or f"https://github.com/anthropics/claude-plugins-official"
        if norm(p["name"]) in existing or url_key(url) in existing_urls:
            continue
        plugins_cat["entries"].append({
            "name": p["name"],
            "url": url,
            "source": "official" if "anthropic" in author.lower() else "vendor",
            "platform": "官方市场 claude-plugins-official",
            "subcat": CATEGORY_MAP.get((p.get("category") or "").lower(), ""),
            "note": trunc(p.get("description", "")),
            "stars": None,
            "installs": None,
            "last_verified": VERIFIED,
            "vmethod": "automated",
        })
        existing.add(norm(p["name"]))
        existing_urls.add(url_key(url))
        added_official += 1

    added_community = 0
    for i in range(CPD_PAGES):
        try:
            page = fetch(CPD_API.format(i * 100))
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"::warning::claude-plugins.dev skipped: {exc}")
            break
        for p in page.get("plugins", []):
            ns = p.get("namespace") or ""
            if ns.startswith("@anthropics"):
                continue  # 已由官方市场导入
            if (p.get("downloads") or 0) < MIN_DOWNLOADS:
                continue
            url = p.get("gitUrl") or f"https://claude-plugins.dev?q={p['name']}"
            if norm(p["name"]) in existing or url_key(url) in existing_urls:
                continue
            plugins_cat["entries"].append({
                "name": p["name"],
                "url": url,
                "source": "community",
                "platform": ns or "claude-plugins.dev",
                "subcat": CATEGORY_MAP.get((p.get("category") or "").lower(), ""),
                "note": trunc(p.get("description", "")),
                "stars": None,
                "installs": p.get("downloads"),
                "last_verified": VERIFIED,
                "vmethod": "automated",
            })
            existing.add(norm(p["name"]))
            existing_urls.add(url_key(url))
            added_community += 1

    if not (added_official or added_community):
        print("OK  no new plugins")
        return
    doc["meta"]["updated"] = VERIFIED
    body = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n" + body)

    print(f"OK  official market imported:  +{added_official}")
    print(f"OK  community (downloads>={MIN_DOWNLOADS}) imported: +{added_community}")
    print(f"OK  plugins category now: {len(plugins_cat['entries'])} entries")
    print("Discovery queue updated; review and promote candidates through the v3 catalog workflow.")


if __name__ == "__main__":
    main()
