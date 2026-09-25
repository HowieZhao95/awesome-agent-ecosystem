#!/usr/bin/env python3
"""Import concrete skills & MCP servers into data/resources.yaml, with subcategories.

Sources:
  - Skills: GitHub topic:claude-skill (top by stars)
  - MCP:    Smithery registry (top by useCount) + GitHub topic:mcp-server (name must contain mcp)

Rerunnable: dedupes by normalized name. Run scripts/build.py afterwards.

Usage:
    python3 scripts/import-skills-mcp.py
    GITHUB_TOKEN=ghp_xxx python3 scripts/import-skills-mcp.py   # higher rate limit
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
DATA_FILE = os.path.join(ROOT, "data", "resources.yaml")
VERIFIED = str(datetime.date.today())
NOTE_MAX = 90
MIN_STARS_SKILL = 300
MIN_STARS_MCP = 500
MIN_USECOUNT_MCP = 2000
MAX_IMPORT_PER_SOURCE = 120

TOKEN = os.environ.get("GITHUB_TOKEN")

SUBCAT_RULES = [
    ("安全", ["security", "audit", "owasp", "vuln", "secret", "guard", "sanitize", "auth", "pentest"]),
    ("前端/设计", ["frontend", "react", "vue", "css", "tailwind", "ui", "design", "slide", "figma", "web-design", "theme"]),
    ("开发/测试", ["test", "playwright", "debug", "review", "api", "sdk", "git", "lint", "refactor", "code"]),
    ("数据/数据库", ["sql", "postgres", "sqlite", "mysql", "mongo", "database", "db", "analytics", "csv", "duckdb", "redis", "data"]),
    ("文档/办公", ["doc", "pdf", "markdown", "pptx", "docx", "xlsx", "excel", "word", "notion", "obsidian", "slide", "report"]),
    ("营销/社媒", ["marketing", "seo", "social", "twitter", "linkedin", "ads", "xiaohongshu", "content", "copywriting"]),
    ("云/运维", ["aws", "azure", "gcp", "cloud", "deploy", "docker", "kubernetes", "k8s", "devops", "infra", "terraform", "vercel", "supabase"]),
    ("搜索/抓取", ["search", "scrape", "crawl", "fetch", "browser", "brave", "tavily", "exa"]),
    ("协作/通讯", ["slack", "email", "gmail", "calendar", "jira", "linear", "discord", "telegram", "teams", "chat"]),
    ("金融/商业", ["finance", "stripe", "payment", "crypto", "trade", "stock", "invoice", "accounting", "web3"]),
    ("AI/记忆", ["memory", "rag", "vector", "embed", "llm", "agent", "knowledge", "graph"]),
    ("媒体/内容", ["image", "video", "audio", "screenshot", "ocr", "media", "canvas"]),
]

HEADER = """# Awesome Agent Ecosystem 机器可读数据源（唯一事实源）
# 条目 = 具体资产（单个 skill / MCP server / 插件 / CLI / 模板 / prompt 库）
# platform 字段 = 资产的分发渠道；平台目录本身仅收录于 platforms 分类（发现渠道，不计入资产统计）
# 维护方式：只手工编辑本文件；README.md 与 site/data.js 由 scripts/build.py 生成
# stars 由 scripts/update-stars.py 定期刷新；市场/注册表数据由 import-*.py 增量导入
"""


def fetch(url, github=False):
    headers = {"User-Agent": "awesome-agent-ecosystem"}
    if github and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def trunc(text, n=NOTE_MAX):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def norm(name):
    return (name or "").strip().lower()


def url_key(url):
    parts = urlsplit((url or "").strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def subcat_of(*texts):
    blob = " ".join(t for t in texts if t).lower()
    for label, kws in SUBCAT_RULES:
        if any(k in blob for k in kws):
            return label
    return "通用"


def github_search(query):
    """Read up to MAX_IMPORT_PER_SOURCE results across GitHub's 100-item pages."""
    seen = 0
    page = 1
    while seen < MAX_IMPORT_PER_SOURCE:
        page_size = 100
        url = (f"https://api.github.com/search/repositories?q={query}"
               f"&sort=stars&order=desc&per_page={page_size}&page={page}")
        items = fetch(url, github=True).get("items", [])
        yield from items[:MAX_IMPORT_PER_SOURCE - seen]
        seen += len(items)
        if len(items) < page_size:
            break
        page += 1


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    cats = {c["id"]: c for c in doc["categories"]}
    existing = {norm(e["name"]) for c in doc["categories"] for e in c["entries"]}
    existing_urls = {url_key(e.get("url")) for c in doc["categories"] for e in c["entries"]}
    added = {"skills": 0, "mcp": 0}

    # ---- Skills: GitHub topic:claude-skill ----
    for r in github_search("topic:claude-skill"):
        if r["stargazers_count"] < MIN_STARS_SKILL:
            continue
        name = r["name"]
        if "awesome" in name.lower():
            continue  # 合集不入资产类
        if norm(name) in existing or norm(r["full_name"]) in existing or url_key(r["html_url"]) in existing_urls:
            continue
        cats["skills"]["entries"].append({
            "name": name,
            "url": r["html_url"],
            "source": "community",
            "platform": "GitHub (topic:claude-skill)",
            "subcat": subcat_of(name, r.get("description"), " ".join(r.get("topics") or [])),
            "note": trunc(r.get("description") or "Claude/Agent 技能包"),
            "stars": r["stargazers_count"],
            "installs": None,
            "last_verified": VERIFIED,
            "vmethod": "automated",
        })
        existing.add(norm(name))
        existing_urls.add(url_key(r["html_url"]))
        added["skills"] += 1

    # ---- MCP: Smithery registry ----
    page = 1
    imported_smithery = 0
    while imported_smithery < MAX_IMPORT_PER_SOURCE and page <= 5:
        url = f"https://registry.smithery.ai/servers?page={page}&pageSize=50"
        try:
            servers = fetch(url).get("servers", [])
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"::warning::Smithery registry skipped: {exc}")
            break
        if not servers:
            break
        for s in servers:
            if imported_smithery >= MAX_IMPORT_PER_SOURCE:
                break
            if (s.get("useCount") or 0) < MIN_USECOUNT_MCP:
                continue
            name = s.get("displayName") or s.get("qualifiedName")
            url = s.get("homepage") or f"https://smithery.ai/server/{s.get('qualifiedName','')}"
            if norm(name) in existing or norm(s.get("qualifiedName")) in existing or url_key(url) in existing_urls:
                continue
            cats["mcp"]["entries"].append({
                "name": name,
                "url": url,
                "source": "vendor" if s.get("verified") else "community",
                "platform": "Smithery",
                "subcat": subcat_of(name, s.get("description"), s.get("qualifiedName")),
                "note": trunc(s.get("description") or "MCP 服务器"),
                "stars": None,
                "installs": s.get("useCount"),
                "last_verified": VERIFIED,
                "vmethod": "automated",
            })
            existing.add(norm(name))
            existing_urls.add(url_key(url))
            added["mcp"] += 1
            imported_smithery += 1
        page += 1

    # ---- MCP: GitHub topic:mcp-server（名字须含 mcp，过滤泛用 topic 的噪音）----
    for r in github_search("topic:mcp-server+mcp+in:name"):
        if r["stargazers_count"] < MIN_STARS_MCP:
            continue
        name = r["name"]
        if "awesome" in name.lower():
            continue  # 合集不入资产类
        if norm(name) in existing or norm(r["full_name"]) in existing or url_key(r["html_url"]) in existing_urls:
            continue
        cats["mcp"]["entries"].append({
            "name": name,
            "url": r["html_url"],
            "source": "community",
            "platform": "GitHub (topic:mcp-server)",
            "subcat": subcat_of(name, r.get("description"), " ".join(r.get("topics") or [])),
            "note": trunc(r.get("description") or "MCP 服务器"),
            "stars": r["stargazers_count"],
            "installs": None,
            "last_verified": VERIFIED,
            "vmethod": "automated",
        })
        existing.add(norm(name))
        existing_urls.add(url_key(r["html_url"]))
        added["mcp"] += 1

    if not any(added.values()):
        print("OK  no new skills or MCP servers")
        return
    doc["meta"]["updated"] = VERIFIED
    body = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n" + body)

    print(f"OK  skills imported: +{added['skills']}  (now {len(cats['skills']['entries'])})")
    print(f"OK  mcp imported:    +{added['mcp']}  (now {len(cats['mcp']['entries'])})")
    print("Next: python3 scripts/build.py")


if __name__ == "__main__":
    main()
