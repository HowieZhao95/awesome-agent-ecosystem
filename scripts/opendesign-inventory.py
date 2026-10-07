#!/usr/bin/env python3
"""Build a read-only, pinned OpenDesign intake inventory from a source archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

UPSTREAM_COMMIT = "53231d40b778d88eba23f35547bf99485d3ae9fc"
ARCHIVE_ROOT = f"open-design-{UPSTREAM_COMMIT}"
DEFAULT_ARCHIVE = Path.home() / ".codex/backups/opendesign-core/p4-upstream-browser/open-design-53231d40b778d88eba23f35547bf99485d3ae9fc.tar.gz"
DEFAULT_REPO = "nexu-io/open-design"
INPUTS = ("design-templates", "skills")
CODE_SUFFIXES = {".html", ".htm", ".tsx", ".ts", ".jsx", ".js", ".css", ".py", ".sh", ".json"}
FORMAT_IDS = {".md": "markdown", ".markdown": "markdown", ".html": "html", ".htm": "html", ".css": "css", ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript", ".sh": "shell", ".py": "python", ".svg": "svg", ".png": "media", ".jpg": "media", ".jpeg": "media", ".webp": "media", ".gif": "media", ".mp4": "media", ".mov": "media", ".webm": "media", ".wav": "media", ".mp3": "media", ".pdf": "binary-project", ".pptx": "binary-project", ".docx": "binary-project"}
STYLE_MARKERS = re.compile(r"\b(style|taste|visual identity|palette|typography|aesthetic|brand|theme|colour|color|editorial|minimalist|brutalist)\b", re.I)
METHOD_MARKERS = re.compile(r"\b(workflow|steps?|process|review|audit|research|generate|create|build|write|produce|apply|validate|checklist|guide|skill|method|procedure|use when)\b", re.I)
PRINCIPLE_MARKERS = re.compile(r"\b(always|never|must|should|principles?|guidelines?|rules?|constraints?|standards?|heuristics?)\b", re.I)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_tar(archive_path: Path) -> tuple[dict[str, bytes], str, str]:
    archive_bytes = archive_path.read_bytes()
    archive_hash = sha256(archive_bytes)
    files: dict[str, bytes] = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        roots = {PurePosixPath(m.name).parts[0] for m in members if PurePosixPath(m.name).parts}
        if len(roots) != 1:
            raise ValueError(f"expected one archive root, found {len(roots)}")
        root = next(iter(roots))
        if root != ARCHIVE_ROOT:
            raise ValueError(f"archive root mismatch: expected pinned source {ARCHIVE_ROOT!r}, found {root!r}")
        prefix = root + "/"
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe archive path: {member.name}")
            if not member.name.startswith(prefix):
                continue
            relative = member.name[len(prefix):]
            if relative:
                stream = archive.extractfile(member)
                if stream:
                    files[relative] = stream.read()
    return files, root, archive_hash


def _frontmatter(body: str) -> dict[str, str]:
    if not body.startswith("---"):
        return {}
    end = body.find("\n---", 3)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    current = ""
    for line in body[3:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current, value = match.groups()
            result[current] = value.strip().strip("\"'")
        elif current and (line.startswith("  ") or line.startswith("\t")):
            result[current] += " " + line.strip().strip("|>").strip()
    return result


def _entry_title(slug: str, body: str) -> str:
    meta = _frontmatter(body)
    for key in ("title", "en_name", "name"):
        value = meta.get(key)
        if value and value.lower() != "null":
            return value
    return slug.replace("-", " ").title()


def _description(slug: str, body: str) -> str:
    meta = _frontmatter(body)
    value = meta.get("description", "").strip().strip("|>").strip()
    if value and value not in {">", "|"}:
        return value[:500]
    lines = [re.sub(r"\s+", " ", line).strip(" #\t") for line in body.splitlines()]
    for line in lines:
        if line and not line.startswith(("name:", "description:", "---")) and len(line) > 28:
            return line[:500]
    return f"OpenDesign source entry {slug}; inspect its pinned instructions and linked files before use."


def _role(path: str, body: bytes) -> str:
    name = PurePosixPath(path).name.lower()
    parts = PurePosixPath(path).parts
    suffix = PurePosixPath(path).suffix.lower()
    if name == "skill.md":
        return "instructions"
    if name in {"open-design.json", "manifest.json"}:
        return "manifest"
    if "example" in name or ("examples" in parts and name not in {"readme.md", "readme.txt"}):
        return "example"
    if parts[0] in {"references", "reference", "docs"} or any(x in name for x in ("checklist", "layout", "component", "guide", "schema")):
        return "support"
    if suffix != ".json" and suffix in CODE_SUFFIXES and (parts[0] in {"assets", "templates", "template", "src", "runtime", "components", "layouts"} or (parts[0] == "scripts" and (name.startswith("compose.") or name.startswith("render."))) or "template" in name or name in {"index.html", "scene.ts", "main.ts"}):
        return "framework"
    return "support"


def _entry_files(slug: str, paths: list[str], file_bytes: dict[str, bytes], source_root: str) -> list[dict[str, Any]]:
    prefix = f"{source_root}/{slug}/"
    result = []
    for path in sorted(paths):
        if not path.startswith(prefix):
            continue
        relative = path
        data = file_bytes[path]
        entry_prefix = f"{source_root}/{slug}/"
        result.append({"path": relative, "sha256": sha256(data), "size_bytes": len(data), "role": _role(relative[len(entry_prefix):], data), "url": f"https://github.com/{DEFAULT_REPO}/blob/{UPSTREAM_COMMIT}/{relative}"})
    return result


def _content_signal(slug: str, body: str, files: list[dict[str, Any]], file_bytes: dict[str, bytes], source_root: str) -> tuple[str, str | None, str, list[str], str]:
    """Classify by instruction and artifact evidence, retaining a quote-sized signal."""
    entry_files = [item for item in files if item["path"].startswith(source_root + "/" + slug + "/")]
    skill = next((item for item in entry_files if item["role"] == "instructions"), None)
    evidence: list[str] = [skill["path"]] if skill else []
    content = body.casefold()
    code_text = "\n".join(file_bytes[item["path"]].decode("utf-8", "replace") for item in entry_files if item["role"] in {"framework", "example"}).casefold()
    summary = _description(slug, body)
    signal = re.sub(r"\s+", " ", summary).strip()[:180]
    has_seed = any(item["role"] == "framework" for item in entry_files)
    has_example = any(item["role"] == "example" for item in entry_files)
    has_support = any(item["role"] == "support" for item in entry_files)
    style_text = bool(STYLE_MARKERS.search(summary + " " + body[:1800]))

    # Style-only design entrypoints are references to the shared framework, never new templates.
    if slug.startswith("html-ppt-taste-") or slug.startswith("html-ppt-zhangzara-") or slug.startswith("web-prototype-taste-"):
        parent = "opendesign.html-ppt" if slug.startswith("html-ppt-") else "opendesign.web-prototype"
        return "reference", None, f"Style variant: the actual Skill describes visual direction while its sibling tree has no independent content/code seed; relates to shared framework {parent}.", evidence, signal

    # A skill that explicitly routes to a shared framework remains a recipe/reference.
    route_match = re.search(r"(?:html-ppt|web-prototype|live-dashboard|mobile-app|open-design-landing|simple-deck)", content)
    if route_match and not has_seed and ("framework" in content or "template" in content or "master" in content or slug.startswith("html-ppt-")):
        parent_slug = route_match.group(0)
        parent = f"opendesign.{parent_slug}"
        return "reference", None, f"Task/content recipe calls or points to shared {parent_slug} instructions; no independent reusable seed/code framework is present in this entry directory.", evidence, signal

    lower = (summary + " " + body[:2600] + " " + code_text[:6000]).casefold()
    subtype: str | None = None
    rationale = ""
    if has_seed and has_example and has_support:
        purpose_text = (summary + " " + body[:1400]).casefold()
        direct_purpose = summary.casefold()
        checks = [
            ("deck", ("presentation", "slide", "pitch deck", "ppt", "reveal.js", "presenter", "keynote")),
            ("three-d", ("three.js", "threejs", "webgl", "webgpu", "shader", "3d", "camera", "scene")),
            ("dashboard", ("dashboard", "analytics", "data table", "chart", "filter", "metric")),
            ("motion-graphics", ("animation", "keyframe", "timeline", "motion", "video", "remotion", "fps", "requestanimationframe")),
            ("document", ("report", "document", "article", "invoice", "newsletter", "guide", "resume", "runbook")),
        ]
        direct_checks = [
            ("motion-graphics", ("motion overlay", "motion overlays", "short-form video", "video template", "video-ready", "html-to-mp4", "animated video")),
            ("dashboard", ("dashboard", "analytics dashboard", "data dashboard")),
            ("deck", ("presentation", "slide deck", "pitch deck", "ppt", "keynote")),
            ("motion-graphics", ("motion graphic", "animation composition", "video template", "animated frame")),
            ("three-d", ("3d", "three.js", "threejs", "webgl", "webgpu", "shader")),
            ("document", ("report", "document", "article", "invoice", "newsletter", "guide", "resume", "runbook")),
            ("prototype", ("web page", "website", "web prototype", "mobile-app", "mobile app", "app ui", "landing site", "landing page", "waitlist", "interface")),
        ]
        for candidate, terms in direct_checks:
            if any(term in direct_purpose for term in terms):
                subtype = candidate
                break
        mode_values = {value.casefold() for value in re.findall(r"(?m)^\s+(?:mode|surface|type|category):\s*['\"]?([^\s#'\"]+)", body[:12000])}
        if "deck" in mode_values or "presentation" in mode_values:
            subtype = "deck"
        elif mode_values & {"video", "hyperframes", "animation-motion"}:
            subtype = "motion-graphics"
        for candidate, terms in checks if subtype is None else []:
            if any(term in purpose_text for term in terms):
                subtype = candidate
                break
        if subtype is None and any(term in purpose_text for term in ("web", "mobile", "app", "landing", "prototype", "interface", "ui", "page", "site")):
            subtype = "prototype"
        if subtype is None and any(term in lower for term in ("<button", "<nav", "<input", "<select")):
            subtype = "prototype"
        if subtype is None:
            subtype = "custom"
        framework = next(item for item in entry_files if item["role"] == "framework")
        example = next(item for item in entry_files if item["role"] == "example")
        support = next(item for item in entry_files if item["role"] == "support")
        evidence.extend([framework["path"], example["path"], support["path"]])
        layout_signals = []
        if "<nav" in code_text or "sidebar" in code_text or "rail" in lower:
            layout_signals.append("navigation/sidebar layout")
        if "<button" in code_text or "<input" in code_text or "<select" in code_text:
            layout_signals.append("interactive controls");
        if "<canvas" in code_text or "<svg" in code_text:
            layout_signals.append("visualization/scene surface")
        if "@keyframes" in code_text or "requestanimationframe" in code_text or "timeline" in lower:
            layout_signals.append("time-based motion")
        detail = ", ".join(layout_signals) if layout_signals else "actual reusable code seed plus layout/support references"
        rationale = f"Reusable {subtype} framework confirmed by the instruction body and real files {framework['path']}, {example['path']}, and {support['path']}; inspected artifact structure shows {detail}."
        return "resource_proposal", subtype, rationale, evidence, signal

    # Principle-only guides stay principles; task procedures remain Skill candidates.
    prose = re.sub(r"^---.*?---", "", body, flags=re.S).strip()
    has_task_procedure = bool(METHOD_MARKERS.search(summary + " " + prose)) and bool(re.search(r"\b(when|input|output|step|workflow|command|run|create|build|write|review|use)\b", prose, re.I))
    if PRINCIPLE_MARKERS.search(summary + " " + prose) and not has_task_procedure and not has_seed:
        return "resource_proposal", None, f"Content is mainly reusable principles/guidelines: the body states constraints or standards without an execution workflow or independent artifact framework. Evidence: {signal}", evidence, signal
    if len(prose) < 120 or len(re.findall(r"\w+", prose)) < 24:
        return "reference", None, f"Thin metadata or pointer text does not define an independent task method or reusable artifact; preserve the actual source path as a browsable reference. Evidence: {signal}", evidence, signal
    if not has_seed and ("api" in lower or "sdk" in lower or "model" in lower or "install" in lower) and not has_task_procedure:
        return "reference", None, f"The body points to an external tool/model/software surface but this entry contains no implementation or substantive task workflow; retain it as a source reference, not a fabricated plugin. Evidence: {signal}", evidence, signal
    if not has_seed and style_text and not has_task_procedure:
        return "reference", None, f"The body provides style/visual guidance without a distinct task method or reusable framework; keep it as a style reference, not a duplicate template or design-system identity. Evidence: {signal}", evidence, signal
    category = "prompts" if PRINCIPLE_MARKERS.search(summary + " " + prose) and not has_task_procedure else "skills"
    rationale = f"Substantive task guidance in the actual instructions body; classified as {category} because it describes a reusable method and contains no separate framework seed. Evidence: {signal}"
    return "resource_proposal", None, rationale, evidence, signal


def _manifest_claims(slug: str, entry_paths: list[str], file_bytes: dict[str, bytes], source_root: str) -> dict[str, Any]:
    candidates = [p for p in entry_paths if p.endswith(("/open-design.json", "/manifest.json"))]
    for path in sorted(candidates):
        try:
            data = json.loads(file_bytes[path])
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        prefix = source_root + "/" + slug + "/"
        if not path.startswith(prefix):
            continue
        author = data.get("author")
        if isinstance(author, dict) and isinstance(author.get("name"), str) and author["name"].strip():
            author_value: dict[str, Any] | None = {"name": author["name"].strip(), "evidence_path": path}
            if isinstance(author.get("url"), str):
                author_value["url"] = author["url"]
        else:
            author_value = None
        license_value = data.get("license") if isinstance(data.get("license"), str) and data["license"].strip() else None
        return {"author": author_value, "license": license_value, "manifest_path": path, "plugin_identity": data.get("$schema", "").endswith("plugin.v1.json") and isinstance(data.get("name"), str) and isinstance(data.get("od"), dict)}
    return {"author": None, "license": None, "manifest_path": None, "plugin_identity": False}


def _domains(slug: str, text: str) -> list[str]:
    lower = (text + " " + slug.replace("-", " ")).casefold()
    terms = [
        ("software-engineering", (r"\bcode\b", r"\bfrontend\b", r"\bdeveloper\b", r"\bsoftware\b", r"\bapi\b", r"\bsdk\b", r"\btool\b", r"\bbuild\b", r"\bengineering\b", r"\bapp\b", r"\bweb\b")),
        ("visual-design", (r"\bdesign\b", r"\bvisual\b", r"\bui\b", r"\bux\b", r"\blayout\b", r"\bbrand\b", r"\bstyle\b", r"\btypography\b", r"\binterface\b", r"\bpalette\b", r"\bdesign system\b")),
        ("motion-video", (r"\bvideo\b", r"\bmotion\b", r"\banimation\b", r"\bframe\b", r"\bclip\b", r"\bremotion\b", r"\bhyperframes\b", r"\bmp4\b", "视频", "动画", "动效")),
        ("three-d", (r"\b3d\b", r"\bthree\.js\b", r"\bthreejs\b", r"\bwebgl\b", r"\bwebgpu\b", r"\bshader\b", "三维")),
        ("data-visualization", (r"\bdashboard\b", r"\bchart\b", r"\banalytics\b", r"\bdata visualization\b", r"\bmetric\b", "仪表盘", "图表", "数据可视化")),
        ("documents", (r"\bdeck\b", r"\bslides?\b", r"\bdocument\b", r"\breport\b", r"\barticle\b", r"\binvoice\b", r"\bpdf\b", r"\bpptx?\b", r"\bnewsletter\b", r"\bguide\b", "文档", "报告", "文章", "演示")),
        ("research", (r"\bresearch\b", r"\breview\b", r"\baudit\b", r"\binvestigat(?:e|ion)\b", r"\bsource\b", "研究", "调研")),
        ("marketing", (r"\bmarketing\b", r"\bsocial\b", r"\blaunch\b", r"\bcampaign\b", r"\bconversion\b", r"\badvertis(?:e|ing)\b", "营销", "社交", "发布")),
        ("audio", (r"\baudio\b", r"\bmusic\b", r"\bvoiceover\b", r"\bspeech\b", r"\bjingle\b", r"\bsound effects?\b", "音乐", "音频", "声音", "语音")),
        ("spatial-design", (r"\barchitecture\b", r"\binterior\b", r"\blandscape\b", "建筑", "室内", "景观")),
    ]
    result = [domain for domain, patterns in terms if any(re.search(pattern, lower) for pattern in patterns)]
    return result or ["general"]


def _resource_proposal(entry: dict[str, Any]) -> dict[str, Any]:
    classification = entry["classification"]
    category = classification["category"]
    subtype = classification["subtype"]
    base = {"id": entry["target"].get("resource_id"), "title": entry["title"], "summary": entry["summary"], "purpose": entry["summary"],
            "classification": {"category": category, "subtype": subtype, "domains": classification["domains"], "formats": classification["formats"], "conventions": ["skill-md"], "rationale": classification["rationale"]},
            "provenance": {"relation": "curated", "content_source": "opendesign", "discovered_via": [], "upstream": {"kind": "git", "url": entry["source_url"], "path": entry["source_path"], "selector": entry["manifest_path"], "ref": {"kind": "commit", "value": UPSTREAM_COMMIT}}, "derives_from": [], "changes": None},
            "authors": {"status": "known" if entry["rights"]["author"] else "unknown", "identities": ([{"name": entry["rights"]["author"]["name"], "url": entry["rights"]["author"].get("url")}] if entry["rights"]["author"] else []), "evidence": ([{"locator": entry["rights"]["author"]["evidence_path"], "claim": "该具体 manifest 明确声明 author.name；此声明只映射到该 asset。"}] if entry["rights"]["author"] else [])},
            "publisher": {"status": "unknown", "identities": [], "evidence": []},
            "license": {"status": "verified" if entry["rights"]["license"] else "unknown", "expression": entry["rights"]["license"], "scope": entry["manifest_path"] if entry["rights"]["license"] else None, "evidence": ([{"locator": entry["manifest_path"], "claim": "此具体 asset 的 manifest 明确声明 license；不继承仓库根许可证。"}] if entry["rights"]["license"] else []), "redistribution": "unknown"},
            "distribution": [{"kind": "repository", "channel_source": "discover.github", "url": entry["source_url"].replace("/blob/", "/tree/").rsplit("/", 1)[0]}],
            "previews": ([{"kind": "html", "url": item["url"], "status": "reference", "evidence": [{"locator": item["path"], "claim": "上游示例文件，只登记可浏览的引用路径；未执行或独立渲染。"}]} for item in entry["files"] if item["role"] == "example"][:3]),
            "compatibility": {"hosts": [], "runtimes": [], "dependencies": [], "constraints": ["上游固定 commit 的源文件入口；本记录不代表可安装、可执行或经过宿主实测。"]},
            "components": [], "lifecycle": {"state": "candidate", "reason": "OpenDesign 固定快照来源盘点候选，待人工审核内容、来源和许可范围。", "replacement_id": None},
            "review": {"status": "pending", "by": None, "at": None, "evidence": []},
            "verification": {"level": "source-inspected", "tested_hosts": [], "checked_at": "2026-10-07", "by": "OpenDesign inventory", "evidence": [{"locator": entry["source_path"], "claim": f"固定上游归档中逐项读取实际 SKILL.md；SHA-256={entry['body_sha256']}。"}], "limits": ["未执行该 Skill、未渲染或运行模板、未测试宿主；许可和再分发范围仍待审核。"]},
            }
    if category == "templates":
        base["template"] = {"files": [{"role": item["role"], "path": item["path"], "url": item["url"]} for item in entry["files"] if item["role"] in {"instructions", "framework", "example", "support"}], "style": {"policy": "external-design-system", "upstream_status": entry["style_status"], "note": "视觉风格属于独立输入；本条只定义框架结构、行为与支持文件。上游风格耦合待人工复核。"}}
    return base


def _parse_existing_resource_paths(resource_data: Path | None) -> dict[str, str]:
    if not resource_data or not resource_data.exists():
        return {}
    result: dict[str, str] = {}
    blocks = re.split(r"(?m)^- id:\s*", resource_data.read_text(encoding="utf-8"))[1:]
    for block in blocks:
        resource_id = block.splitlines()[0].strip()
        provenance = re.search(r"(?ms)^  provenance:\n(.*?)(?=^  authors:)", block)
        upstream_path = re.search(r"(?m)^      path:\s*['\"]?([^\s'\"]+)", provenance.group(1)) if provenance else None
        if upstream_path and resource_id.startswith("opendesign."):
            result.setdefault(upstream_path.group(1), resource_id)
    return result


def _parse_existing_resource_ids(resource_data: Path | None) -> set[str]:
    if not resource_data or not resource_data.exists():
        return set()
    return set(re.findall(r"(?m)^- id:\s*(\S+)\s*$", resource_data.read_text(encoding="utf-8")))


def _inspect_artifacts(entry_paths: list[str], file_bytes: dict[str, bytes], summary: str, rationale: str) -> dict[str, Any]:
    source_files = [item for item in entry_paths if item["role"] in {"framework", "example"}]
    text = "\n".join(file_bytes[item["path"]].decode("utf-8", "replace") for item in source_files).casefold()
    tags = sorted(set(re.findall(r"<(nav|header|main|aside|section|article|footer|form|button|input|select|canvas|svg|video|audio|iframe)\b", text)))
    layout = []
    for label, marker in (("grid", "grid"), ("flex", "flex"), ("sidebar", "sidebar"), ("slide/page sequence", "slide"), ("timeline", "timeline"), ("card/frame composition", "frame"), ("responsive breakpoints", "@media")):
        if marker in text:
            layout.append(label)
    interactions = []
    for label, marker in (("form controls", ("<form", "<input", "<select", "<textarea")), ("buttons/actions", ("<button", "onclick", "addEventListener")), ("navigation", ("<nav", "href=", "location.hash")), ("keyboard controls", ("keydown", "keyup", "keyboard")), ("drag/pointer", ("pointerdown", "pointermove", "draggable", "dragstart")), ("live data", ("fetch(", "websocket", "eventsource", "refresh")), ("playback/animation", ("requestanimationframe", "@keyframes", "playback", "setinterval"))):
        if any(marker_item in text for marker_item in marker):
            interactions.append(label)
    return {"inspected_paths": [{"path": item["path"], "role": item["role"], "sha256": item["sha256"], "size_bytes": item["size_bytes"]} for item in source_files], "purpose": summary, "layout_signals": layout, "html_elements": tags, "interaction_signals": interactions, "classification_basis": rationale}


def _shared_video_structure_alias(slug: str, input_name: str, file_bytes: dict[str, bytes]) -> bool:
    """Require actual three-scene markup and matching navigation behavior before style aliasing."""
    if input_name != "skills" or slug != "after-hours-editorial-template":
        return False
    def load_template(name: str) -> str:
        path = f"skills/{name}/assets/template.html"
        return file_bytes.get(path, b"").decode("utf-8", "replace").casefold()
    alias = load_template(slug)
    base = load_template("8-bit-orbit-video-template")
    if not alias or not base:
        return False
    scene_pattern = re.compile(r"<section\b[^>]*class=[\"'][^\"']*\bscene\b")
    alias_scenes = len(scene_pattern.findall(alias))
    base_scenes = len(scene_pattern.findall(base))
    if alias_scenes != 3 or base_scenes != 3:
        return False
    interaction_markers = ("keydown", "pager", "addeventlistener")
    return all(marker in alias and marker in base for marker in interaction_markers)


def inventory_archive(archive_path: str | Path, expected_entry_counts: dict[str, int] | None = None, resource_data: str | Path | None = None, resource_data_ref: str | None = None) -> dict[str, Any]:
    archive_path = Path(archive_path)
    file_bytes, archive_root, archive_hash = _read_tar(archive_path)
    # _read_tar strips the single archive root; all later paths are repo-relative.
    source_root = ""
    by_input: dict[str, dict[str, Any]] = {}
    all_paths = sorted(file_bytes)
    existing_paths = _parse_existing_resource_paths(Path(resource_data) if resource_data else None)
    existing_ids = _parse_existing_resource_ids(Path(resource_data) if resource_data else None)
    existing_hash_ids: dict[str, str] = {}
    for source_path, resource_id in existing_paths.items():
        if source_path in file_bytes:
            existing_hash_ids.setdefault(sha256(file_bytes[source_path]), resource_id)
    proposals: list[dict[str, Any]] = []
    related_entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for input_name in INPUTS:
        prefix = f"{input_name}/"
        skill_paths = [path for path in all_paths if path.startswith(prefix) and path.endswith("/SKILL.md")]
        entries: list[dict[str, Any]] = []
        for skill_path in skill_paths:
            rel = skill_path
            slug = rel.split("/")[1]
            folder_prefix = f"{input_name}/{slug}/"
            paths = [path for path in all_paths if path.startswith(folder_prefix)]
            body_bytes = file_bytes[skill_path]
            body = body_bytes.decode("utf-8", "replace")
            summary = _description(slug, body)
            source_entries = _entry_files(slug, paths, file_bytes, input_name)
            disposition, subtype, rationale, evidence, signal = _content_signal(slug, body, source_entries, file_bytes, input_name)
            slug_resource_id = f"opendesign.{slug}"
            exact_path_id = existing_paths.get(rel)
            exact_body_id = existing_hash_ids.get(sha256(body_bytes))
            matched_resource_id = exact_path_id or exact_body_id
            match_basis = "exact-upstream-path" if exact_path_id else ("identical-skill-sha256" if exact_body_id else None)
            target_id = matched_resource_id or slug_resource_id
            if _shared_video_structure_alias(slug, input_name, file_bytes):
                disposition = "shared_framework_reference"
                subtype = None
                target_id = "opendesign.8-bit-orbit-video-template"
                rationale = "The fixed Skill describes a dark editorial HyperFrames look. Its real seed and the 8-bit sibling both contain three `section.scene` stages and the same pager/keyboard/addEventListener controls, while no separate schema or interaction model appears; treat the palette/type treatment as a source-linked style variant, not another template identity."
                evidence = [f"skills/{slug}/SKILL.md", f"skills/{slug}/assets/template.html", "skills/8-bit-orbit-video-template/SKILL.md", "skills/8-bit-orbit-video-template/assets/template.html"]
            if disposition == "reference" and slug == "html-ppt-pitch-deck" and slug_resource_id in existing_ids:
                target_id = slug_resource_id
                disposition = "existing_resource"
                matched_resource_id = target_id
                match_basis = "stable-resource-id-same-source-folder"
                rationale = f"Preserve canonical ID {slug_resource_id} for the same OpenDesign source-family folder. This folder-level identity match is not a content-equivalence claim; compare the recorded SKILL SHA-256 and source path. " + rationale
            elif disposition == "reference" and (slug.startswith("html-ppt-") or slug.startswith("web-prototype-taste-")):
                target_id = "opendesign.html-ppt" if slug.startswith("html-ppt-") else "opendesign.web-prototype"
                disposition = "shared_framework_reference"
            elif matched_resource_id:
                disposition = "existing_resource"
                target_id = matched_resource_id
            elif slug_resource_id in existing_ids and disposition != "shared_framework_reference":
                disposition = "existing_resource"
                target_id = slug_resource_id
                matched_resource_id = slug_resource_id
                match_basis = "stable-resource-id-same-source-folder"
                rationale = f"Preserve canonical ID {slug_resource_id} for the same OpenDesign source-family folder. This folder-level identity match is not a content-equivalence claim; compare the recorded SKILL SHA-256 and source path. " + rationale
            if disposition == "resource_proposal" and (target_id in existing_ids or target_id in seen_ids):
                target_id = f"opendesign.{input_name}.{slug}"
                rationale = f"Keep this source-unit candidate under a distinct ID because the current canonical ID belongs to another entry or a previous inventory row. " + rationale
            if disposition in {"resource_proposal", "existing_resource"}:
                seen_ids.add(target_id)
            # Avoid reusing an existing ID when no same-path or same-body evidence supports identity.
            if target_id in existing_ids and not matched_resource_id and disposition == "resource_proposal":
                target_id = f"opendesign.{input_name}.{slug}"
                rationale = f"A same-named canonical ID exists but the fixed source path and SKILL body hash do not match; keep this candidate distinct pending human review. " + rationale
            category = "templates" if subtype and input_name == "design-templates" else ("templates" if disposition == "resource_proposal" and subtype else ("prompts" if "principles/guidelines" in rationale or "principles" in rationale else "skills"))
            if category == "prompts":
                subtype = "principle"
            if disposition == "existing_resource":
                target_id = matched_resource_id or target_id
            # References may point at a shared framework by exact observed filename/link content.
            if disposition == "reference" and target_id == f"opendesign.{slug}":
                if slug.startswith("html-ppt-"):
                    target_id = "opendesign.html-ppt"
                elif slug.startswith("web-prototype-taste-"):
                    target_id = "opendesign.web-prototype"
            manifest = _manifest_claims(slug, paths, file_bytes, input_name)
            files = [{"path": item["path"], "role": item["role"], "sha256": item["sha256"], "size_bytes": item["size_bytes"], "url": item["url"]} for item in source_entries]
            missing = []
            roles = {item["role"] for item in files}
            if "instructions" not in roles: missing.append("SKILL.md instructions not found")
            if "framework" not in roles: missing.append("No reusable framework seed/code file found by role and content path")
            if "example" not in roles: missing.append("No example file found")
            if "support" not in roles: missing.append("No supporting references/layout/checklist file found")
            if len(re.sub(r"^---.*?---", "", body, flags=re.S).split()) < 24 and disposition != "existing_resource": missing.append("Thin metadata/body; substantive task method was not established")
            ext = sorted({FORMAT_IDS[PurePosixPath(item["path"]).suffix.lower()] for item in files if PurePosixPath(item["path"]).suffix.lower() in FORMAT_IDS})
            classification = {"category": category, "subtype": subtype, "domains": _domains(slug, summary[:240]), "formats": ext, "conventions": ["skill-md"], "rationale": rationale, "evidence_paths": evidence, "body_evidence": signal}
            source_url = f"https://github.com/{DEFAULT_REPO}/blob/{UPSTREAM_COMMIT}/{rel}"
            artifact_inspection = _inspect_artifacts(files, file_bytes, summary, rationale)
            entry = {"id": f"od:{input_name}:{slug}", "input": input_name, "slug": slug, "title": _entry_title(slug, body), "summary": summary, "source_path": rel, "source_url": source_url,
                     "body_sha256": sha256(body_bytes), "body_bytes": len(body_bytes), "manifest_path": manifest["manifest_path"], "matched_existing": {"resource_id": matched_resource_id, "basis": match_basis, "upstream_path": next((path for path, rid in existing_paths.items() if rid == matched_resource_id), None), "body_sha256_equal": bool(matched_resource_id and match_basis in {"exact-upstream-path", "identical-skill-sha256"})} if matched_resource_id else None, "rights": {"author": manifest["author"], "license": manifest["license"], "manifest_path": manifest["manifest_path"], "redistribution": "unknown"}, "classification": classification,
                     "disposition": disposition, "target": {"resource_id": target_id if disposition in {"existing_resource", "shared_framework_reference", "resource_proposal"} or (disposition == "reference" and target_id != f"opendesign.{slug}") else None, "browse_target": "existing-framework" if disposition == "shared_framework_reference" else ("resource" if disposition in {"existing_resource", "resource_proposal"} else "discovery-reference"), "reason": rationale},
                     "artifact_inspection": artifact_inspection,
                     "files": files, "missing": missing, "review": {"status": "pending"}, "verification": {"level": "source-inspected", "tested_hosts": []}, "style_status": "mixed" if STYLE_MARKERS.search(body + " " + signal) else "unknown"}
            # Explicit style aliases point to their framework rather than create a second template identity.
            if disposition == "reference" and target_id.startswith("opendesign.html-ppt") or disposition == "reference" and target_id == "opendesign.web-prototype":
                entry["disposition"] = "shared_framework_reference"
                entry["target"]["browse_target"] = "existing-framework"
            if entry["disposition"] == "resource_proposal":
                entry["target"]["resource_id"] = target_id
                entry["classification"]["category"] = category
                proposals.append(_resource_proposal(entry))
            if entry["disposition"] in {"shared_framework_reference", "reference", "existing_resource"}:
                related_entries.append({"id": entry["id"], "entry_id": entry["id"], "title": entry["title"], "summary": entry["summary"], "content_kind": "reference", "category": entry["classification"]["category"], "subtype": entry["classification"]["subtype"], "domains": entry["classification"]["domains"], "source_url": entry["source_url"], "mapped_resource_id": entry["target"]["resource_id"], "target_resource_id": entry["target"]["resource_id"], "relationship": "style-variant-or-content-recipe" if entry["disposition"] == "shared_framework_reference" else entry["disposition"], "reason": rationale, "evidence_paths": evidence, "input_key": rel, "legacy_keys": [rel], "source_path": rel, "body_sha256": entry["body_sha256"]})
            entries.append(entry)
        by_input[input_name] = {"source_prefix": f"{input_name}/", "entry_count": len(entries), "entries": entries}
    expected_entry_counts = expected_entry_counts or {"design-templates": 114, "skills": 163}
    mismatches = {name: {"expected": expected_entry_counts.get(name), "actual": by_input[name]["entry_count"]} for name in INPUTS if expected_entry_counts.get(name) is not None and expected_entry_counts[name] != by_input[name]["entry_count"]}
    all_entries = [entry for section in by_input.values() for entry in section["entries"]]
    dispositions: dict[str, int] = {}
    categories: dict[str, int] = {}
    for entry in all_entries:
        dispositions[entry["disposition"]] = dispositions.get(entry["disposition"], 0) + 1
        category = entry["classification"]["category"]
        categories[category] = categories.get(category, 0) + 1
    representative_frames = []
    for entry in all_entries:
        if entry["slug"].startswith("frame-") or any(f["role"] == "framework" for f in entry["files"]):
            code_items = [f for f in entry["files"] if f["role"] == "framework"]
            example_items = [f for f in entry["files"] if f["role"] == "example"]
            inspected_items = code_items or example_items
            if inspected_items:
                representative_frames.append({"entry_id": entry["id"], "source_path": entry["source_path"], "purpose": entry["artifact_inspection"]["purpose"], "subtype": entry["classification"]["subtype"], "framework_paths": [f["path"] for f in code_items], "example_paths": [f["path"] for f in example_items], "code_sha256": [f["sha256"] for f in inspected_items], "layout_signals": entry["artifact_inspection"]["layout_signals"], "interaction_signals": entry["artifact_inspection"]["interaction_signals"], "html_elements": entry["artifact_inspection"]["html_elements"], "classification_reason": entry["classification"]["rationale"]})
    resource_data_path = Path(resource_data) if resource_data else None
    resource_data_hash = sha256(resource_data_path.read_bytes()) if resource_data_path and resource_data_path.exists() else None
    return {"schema_version": 1, "upstream": {"repository": DEFAULT_REPO, "commit": UPSTREAM_COMMIT, "archive_sha256": archive_hash, "archive_root": archive_root}, "existing_resource_data": {"path": "data/resources.yaml" if resource_data_path else None, "ref": resource_data_ref, "sha256": resource_data_hash, "resource_count": len(existing_ids), "read_only": True},
            "inputs": by_input, "coverage": {"expected_counts": expected_entry_counts, "actual_counts": {name: by_input[name]["entry_count"] for name in INPUTS}, "entry_total": len(all_entries), "unaccounted_entries": 0 if not mismatches else sum(abs(v["expected"] - v["actual"]) for v in mismatches.values()), "count_mismatches": mismatches, "dispositions": dispositions, "classification_categories": categories, "all_entries_have_body_hash": all(bool(re.fullmatch(r"[0-9a-f]{64}", e["body_sha256"])) for e in all_entries), "all_entries_have_target_reason": all(bool(e["target"]["reason"]) for e in all_entries), "all_proposals_pending": all(p["review"]["status"] == "pending" and p["lifecycle"]["state"] == "candidate" and p["verification"]["tested_hosts"] == [] for p in proposals)},
            "proposals": {"resources": proposals, "related_entries": related_entries}, "representative_framework_inspections": representative_frames}


def render_coverage(report: dict[str, Any]) -> str:
    upstream = report["upstream"]
    lines = ["# OpenDesign 目录覆盖", "", f"固定来源：`{upstream['repository']}@{upstream['commit']}`；归档 SHA-256：`{upstream['archive_sha256']}`。", "", "该清单逐项记录每个 SKILL.md 的正文哈希、实际文件、分类理由、来源定位和浏览去向。资源候选一律 pending；未知作者/许可/再分发保持 unknown。文件与媒体仅引用固定上游路径，不复制正文。", "", "| 入口 | 数量 | 去向分布 |", "|---|---:|---|"]
    for name, section in report["inputs"].items():
        counts: dict[str, int] = {}
        for entry in section["entries"]:
            counts[entry["disposition"]] = counts.get(entry["disposition"], 0) + 1
        lines.append(f"| `{name}/` | {section['entry_count']} | " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + " |")
    lines.extend(["", f"总计 `{report['coverage']['entry_total']}` 项；候选资源 `{len(report['proposals']['resources'])}` 项；显式关联/参考 `{len(report['proposals']['related_entries'])}` 项。当前资源正本包含 `{report['existing_resource_data']['resource_count']}` 条；本盘点只读该正本。", "", "分类与审核边界：模板候选须在实际 Skill 之外找到可复用框架代码、独立示例和辅助文件；主题/风格入口映射共享框架。没有框架的任务 Skill 作为 Skills/原则提示候选或原址发现线索。HTML/PPT 只是实现格式，不能单独决定模板身份。此自动提案没有批准任何条目的公开、安装、执行或再分发。", "", "## 逐项覆盖", ""])
    for input_name, section in report["inputs"].items():
        lines.extend([f"### `{input_name}/`", "", "| 上游入口 | 分类 | 去向 | 目标 | 内容/代码证据与理由 | 正文 SHA-256 | 固定来源 |", "|---|---|---|---|---|---|---|"])
        for entry in section["entries"]:
            category = entry["classification"]["category"]
            subtype = entry["classification"]["subtype"] or "—"
            target = entry["target"]["resource_id"] or "独立发现线索"
            evidence = "; ".join(entry["classification"]["evidence_paths"] or [entry["source_path"]])
            reason = entry["target"]["reason"].replace("|", "\\|").replace("\n", " ")
            source = f"[SKILL.md]({entry['source_url']})"
            lines.append(f"| `{entry['source_path']}` | {category}/{subtype} | {entry['disposition']} | `{target}` | `{evidence}` — {reason} | `{entry['body_sha256']}` | {source} |")
        lines.append("")
    lines.extend(["逐项结构化证据、文件角色/hash、rights 与候选 Resource 草案：`docs/evidence/complete-directory/opendesign-inventory.json`。该 JSON 是 UI 接线的机器输入；`proposals.related_entries` 为无独立资源身份的风格、配方和发现线索提供原始名称、摘要、固定 URL、目标 ID 与正文哈希。", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--resource-data", type=Path, help="Read-only Resource YAML override; use --resource-data-ref for a Git snapshot by default.")
    parser.add_argument("--resource-data-ref", help="Optional Git revision providing a read-only Resource YAML baseline.")
    parser.add_argument("--json", type=Path, default=Path(__file__).resolve().parents[1] / "docs/evidence/complete-directory/opendesign-inventory.json")
    parser.add_argument("--coverage", type=Path, default=Path(__file__).resolve().parents[1] / "docs/opendesign-directory-coverage.md")
    args = parser.parse_args()
    try:
        if args.resource_data_ref:
            snapshot = subprocess.run(["git", "show", f"{args.resource_data_ref}:data/resources.yaml"], cwd=Path(__file__).resolve().parents[1], check=True, capture_output=True)
            with tempfile.TemporaryDirectory(prefix="opendesign-resource-baseline-") as temp_dir:
                snapshot_path = Path(temp_dir) / "resources.yaml"
                snapshot_path.write_bytes(snapshot.stdout)
                report = inventory_archive(args.archive, resource_data=snapshot_path, resource_data_ref=args.resource_data_ref)
        elif args.resource_data:
            report = inventory_archive(args.archive, resource_data=args.resource_data, resource_data_ref=None)
        else:
            working_resource_data = Path(__file__).resolve().parents[1] / "data/resources.yaml"
            report = inventory_archive(args.archive, resource_data=working_resource_data)
    except (OSError, tarfile.TarError, ValueError) as error:
        parser.error(str(error))
    write_outputs(report, args.json, args.coverage)
    print(json.dumps(report["coverage"], ensure_ascii=False, sort_keys=True))
    return 1 if report["coverage"]["count_mismatches"] else 0


def write_outputs(report: dict[str, Any], json_path: Path, coverage_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(render_coverage(report), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
