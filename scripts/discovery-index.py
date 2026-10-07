#!/usr/bin/env python3
"""Build a deterministic, read-only browse projection of the historical queue."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, unquote, urlsplit, urlunsplit

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

SOURCE_ID = "discover.awesome-agent-ecosystem"
CATEGORY_MAP = {
    "skills": ("skills", None),
    "mcp": ("plugins", None),
    "plugins": ("plugins", None),
    "cli": ("plugins", None),
    "prompts": ("prompts", None),
    "design-docs": ("design-systems", None),
}


def _plain(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def normalized_url(url):
    """Normalize GitHub branch/commit links while retaining specific paths."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    path = re.sub(r"/+", "/", unquote(parts.path)).rstrip("/")
    query = parts.query
    fragment = parts.fragment
    if host == "github.com":
        path = re.sub(r"/(tree|blob)/[^/]+(/.*)$", r"/\1/*\2", path)
        path = re.sub(r"/(tree|blob)/[^/]+$", r"/\1/*", path)
    else:
        query = urlencode([(key, value) for key, value in parse_qsl(query, keep_blank_values=True) if not key.lower().startswith("utm_")])
    return urlunsplit((parts.scheme.lower(), host, path, query, fragment))


def _legacy_key(category, name, occurrence=1):
    base = f"{category}/{name}"
    return base if occurrence == 1 else f"{base}#{occurrence}"


def _content_kind(category, name, note, url):
    text = f"{name} {note} {url}".lower()
    if category == "prompts":
        if "模板：" in name or "其余 5 套" in note or any(word in text for word in ("cookbook", "教程", "指南", "papers", "论文", "awesome-", "索引", "合集", "教科书", "对比指南")):
            return "collection"
        if any(word in text for word in ("agents.md", "原则", "规范文本", "design.md", "design token", "w3c")):
            return "specification"
        if any(word in text for word in ("generator", "生成器", "提取服务", "平台", "管理平台", "优化框架", "结构化生成控制库")):
            return "reference"
        return "asset"
    if category == "design-docs":
        if any(word in text for word in ("cli", "工具", "stitch")):
            return "reference"
        if any(word in text for word in ("w3c", "规范", "标准", "design.md")):
            return "specification"
        return "reference"
    return "asset"


def _classification(category, name, note, url, override):
    if override:
        return dict(override)
    mapped_category, subtype = CATEGORY_MAP[category]
    text = f"{name} {note} {url}".lower()
    domains = []
    for terms, domain in [
        (("design", "frontend", "ui", "css", "visual", "品牌", "界面", "设计"), "visual-design"),
        (("video", "motion", "remotion", "动画", "视频", "剪辑"), "motion-video"),
        (("3d", "three", "blender", "模型", "三维"), "three-d"),
        (("dashboard", "chart", "data", "数据", "图表"), "data-visualization"),
        (("document", "docs", "report", "文档", "报告"), "documents"),
        (("research", "paper", "论文", "研究"), "research"),
        (("marketing", "social", "营销", "广告"), "marketing"),
        (("audio", "music", "voice", "音频", "音乐", "语音"), "audio"),
        (("code", "coding", "developer", "programming", "test", "api", "cli", "mcp", "工程", "测试", "开发", "编程"), "software-engineering"),
    ]:
        if any((re.search(rf"\b{re.escape(term)}\b", text) if term.isascii() else term in text) for term in terms):
            domains.append(domain)
    if not domains:
        domains = ["general"]
    if category == "prompts":
        if any(term in text for term in ("agents.md", "原则", "规范文本", "design.md", "design token", "w3c")):
            subtype = "principle"
        elif any(term in text for term in ("image prompt", "图片提示", "图片生成", "图像生成")):
            subtype = "image"
        elif any(term in text for term in ("video prompt", "视频提示", "视频生成")):
            subtype = "video"
    rationale = f"历史条目“{name}”的用途概述为：{note}；此分类仅用于发现浏览，未据此确认上游组件、许可或可运行性。"
    return {
        "category": mapped_category,
        "subtype": subtype,
        "domains": domains,
        "formats": [],
        "conventions": [],
        "rationale": rationale,
    }


def _resource_lookup(resources):
    by_upstream = {}
    by_host_title = {}
    for resource in resources:
        upstream = resource.get("provenance", {}).get("upstream") or {}
        candidates = [upstream.get("url", "")]
        if upstream.get("path") and upstream.get("url"):
            base = upstream["url"].split("/blob/", 1)[0].split("/tree/", 1)[0]
            candidates.append(f"{base}/tree/{upstream['path']}")
        for candidate in candidates:
            if candidate:
                by_upstream.setdefault(normalized_url(candidate), resource["id"])
        host = normalized_url(upstream.get("url", ""))
        title = re.sub(r"[^a-z0-9]+", "", resource.get("title", "").lower())
        if host and title:
            by_host_title[(host, title)] = resource["id"]

    def match(url, name):
        needle = normalized_url(url)
        if not needle:
            return None
        if needle in by_upstream:
            parts = urlsplit(needle)
            path_parts = [part for part in parts.path.split("/") if part]
            # A GitHub repository homepage is shared by many separately named
            # packages. Require a package title match unless the URL locates a path.
            if parts.netloc != "github.com" or len(path_parts) > 2:
                return by_upstream[needle]
        # Homepage-only URLs can match by exact package title, never by repo alone.
        name_key = re.sub(r"[^a-z0-9]+", "", name.lower())
        return by_host_title.get((needle, name_key)) if name_key else None

    return match


def build_index(data_path, resources_path, categories_path, overrides_path):
    raw = Path(data_path).read_bytes()
    document = yaml.safe_load(raw)
    resources_doc = yaml.safe_load(Path(resources_path).read_text(encoding="utf-8"))
    category_doc = yaml.safe_load(Path(categories_path).read_text(encoding="utf-8"))
    override_path = Path(overrides_path) if overrides_path else None
    override_doc = yaml.safe_load(override_path.read_text(encoding="utf-8")) if override_path and override_path.exists() else {}
    allowed_categories = {item["id"] for item in category_doc.get("categories", [])}
    allowed_domains = {item["id"] for item in category_doc.get("dimensions", {}).get("domains", [])}
    allowed_formats = {item["id"] for item in category_doc.get("dimensions", {}).get("formats", [])}
    allowed_conventions = {item["id"] for item in category_doc.get("dimensions", {}).get("conventions", [])}
    override_map = override_doc.get("overrides", {})
    required_override_keys = set()
    key_occurrences = defaultdict(int)
    for category in document.get("categories", []):
        if category["id"] == "platforms":
            continue
        for legacy in category.get("entries", []):
            name = str(legacy.get("name", "")).strip()
            key_occurrences[(category["id"], name)] += 1
            required_override_keys.add(_legacy_key(category["id"], name, key_occurrences[(category["id"], name)]))
    unknown_overrides = set(override_map) - required_override_keys
    if unknown_overrides:
        raise ValueError(f"classification overrides contain unknown legacy keys: {sorted(unknown_overrides)[:5]}")
    resources = resources_doc.get("resources", [])
    match_resource = _resource_lookup(resources)

    platforms = []
    rows = []
    seen_names = defaultdict(int)
    for category in document.get("categories", []):
        category_id = category["id"]
        for legacy in category.get("entries", []):
            name = str(legacy.get("name", "")).strip()
            seen_names[(category_id, name)] += 1
            key = _legacy_key(category_id, name, seen_names[(category_id, name)])
            url = legacy.get("url") or ""
            if category_id == "platforms":
                platforms.append({
                    "id": "discovery.platform." + hashlib.sha256((key + "\0" + normalized_url(url)).encode()).hexdigest()[:16],
                    "name": name,
                    "url": url,
                    "summary": str(legacy.get("note", "")),
                    "legacy_key": key,
                    "source_label": legacy.get("source"),
                })
                continue

            override = override_map.get(key)
            classification = _classification(category_id, name, str(legacy.get("note", "")), url, override)
            if classification["category"] not in allowed_categories:
                raise ValueError(f"{key}: unknown category {classification['category']}")
            if classification.get("subtype") and classification["subtype"] not in {
                item["id"] for item in next((c for c in category_doc["categories"] if c["id"] == classification["category"]), {}).get("subtypes", [])
            }:
                raise ValueError(f"{key}: unknown subtype {classification['subtype']}")
            for field, allowed in (("domains", allowed_domains), ("formats", allowed_formats), ("conventions", allowed_conventions)):
                invalid = set(classification.get(field, [])) - allowed
                if invalid:
                    raise ValueError(f"{key}: unknown {field}: {sorted(invalid)}")
            kind = _content_kind(category_id, name, str(legacy.get("note", "")), url)
            mapped_id = match_resource(url, name)
            missing = ["content source or exact upstream path is unverified", "author and license were not independently verified"]
            expected_components = []
            if category_id in {"mcp", "cli"}:
                expected_components = ["mcp-server" if category_id == "mcp" else "cli"]
                missing.append("component type is only an expectation from the historical category; no real component manifest was verified")
            if category_id == "plugins":
                missing.append("historical entry does not establish a real plugin manifest or install boundary")
            if kind in {"collection", "reference", "specification"}:
                missing.append("historical entry is a collection/reference/specification, not a verified installable asset")
            identity = hashlib.sha256((key + "\0" + normalized_url(url)).encode()).hexdigest()[:16]
            rows.append({
                "id": "discovery.legacy." + identity,
                "title": name,
                "summary": str(legacy.get("note", "")),
                "classification": classification,
                "source_url": url or None,
                "channel_source": SOURCE_ID,
                "legacy_keys": [key],
                "legacy": {
                    "category": category_id,
                    "subcat": legacy.get("subcat"),
                    "platform": legacy.get("platform"),
                    "source_label": legacy.get("source"),
                    "stars": legacy.get("stars"),
                    "installs": legacy.get("installs"),
                    "last_verified": _plain(legacy.get("last_verified")),
                    "vmethod": legacy.get("vmethod"),
                },
                "content_kind": kind,
                "expected_components": expected_components,
                "missing": missing,
                **({"mapped_resource_id": mapped_id} if mapped_id else {}),
            })

    # Merge only identical display names and exact normalized Git object paths/URLs.
    grouped = {}
    for row in rows:
        merge_key = (row["title"].casefold(), normalized_url(row["source_url"]))
        if merge_key[1] and merge_key in grouped:
            grouped[merge_key]["legacy_keys"].extend(row["legacy_keys"])
            continue
        grouped[merge_key] = row
    entries = sorted(grouped.values(), key=lambda item: (item["title"].casefold(), item["id"]))
    outcomes = []
    for entry in entries:
        keys = entry["legacy_keys"]
        disposition = "mapped" if entry.get("mapped_resource_id") else ("merged" if len(keys) > 1 else "discovery")
        reason = "matches an existing canonical resource" if disposition == "mapped" else (
            "same titled entry and exact normalized source URL merged" if disposition == "merged" else
            "retained as a discovery entry with provenance and usability gaps disclosed"
        )
        target = entry.get("mapped_resource_id", entry["id"])
        outcomes.extend({"legacy_key": key, "target_id": target, "disposition": disposition, "reason": reason} for key in keys)
    outcomes.sort(key=lambda item: item["legacy_key"])
    return {
        "schema_version": 1,
        "source_id": SOURCE_ID,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "entries": entries,
        "platforms": sorted(platforms, key=lambda item: (item["name"].casefold(), item["id"])),
        "coverage": {
            "total_assets": len(outcomes),
            "total_platforms": len(platforms),
            "outcomes": outcomes,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--resources", type=Path, required=True)
    parser.add_argument("--categories", type=Path, required=True)
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="Output path; canonical baseline is never overwritten implicitly")
    args = parser.parse_args()
    try:
        index = build_index(args.data, args.resources, args.categories, args.overrides)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, yaml.YAMLError, KeyError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print(f"Wrote {len(index['entries'])} discovery entries; coverage {index['coverage']['total_assets']} assets and {index['coverage']['total_platforms']} platforms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
