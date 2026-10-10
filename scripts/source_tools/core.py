"""Metadata-only snapshots and review diffs for locked public source inputs."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import tarfile
from pathlib import Path, PurePosixPath
import yaml


class SnapshotError(RuntimeError):
    pass


LOCKED_SOURCES = {
    "opendesign": {"repo": "nexu-io/open-design"},
    "remotion": {"repo": "remotion-dev/skills"},
    "legacy": {"repo": "HowieZhao95/awesome-agent-ecosystem"},
}


def validate_locked_ref(ref: str) -> str:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", ref or ""):
        raise SnapshotError("public snapshots require a full 40-character commit SHA")
    return ref.lower()


def _selected(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) or (pattern.endswith("/**") and path.startswith(pattern[:-3] + "/")) for pattern in patterns)


def _metadata(path: str, content: bytes) -> tuple[dict, str | None]:
    text = content.decode("utf-8", errors="replace")
    metadata: dict = {}
    identity = None
    if path.endswith("open-design.json") or path.endswith(".json"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                for key in ("id", "name", "title", "version", "description", "author", "license", "type"):
                    if key in parsed:
                        metadata[key] = parsed[key]
                identity = str(parsed.get("id") or "") or None
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            if path.endswith("open-design.json"):
                raise SnapshotError("invalid OpenDesign manifest JSON") from exc
    elif path.endswith("SKILL.md"):
        match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
        if match:
            try:
                parsed = yaml.safe_load(match.group(1)) or {}
                if isinstance(parsed, dict):
                    metadata = {key: parsed[key] for key in ("name", "description", "license", "compatibility", "metadata") if key in parsed}
                    identity = str(parsed.get("name") or "") or None
            except yaml.YAMLError as exc:
                raise SnapshotError(f"invalid SKILL.md frontmatter: {type(exc).__name__}") from exc
    elif path.endswith((".yaml", ".yml")):
        try:
            parsed = yaml.safe_load(text)
            if isinstance(parsed, dict):
                metadata = {key: parsed[key] for key in ("id", "name", "title", "version", "description", "author", "license", "type") if key in parsed}
                identity = str(parsed.get("id") or parsed.get("name") or "") or None
        except yaml.YAMLError as exc:
            raise SnapshotError(f"invalid YAML metadata: {type(exc).__name__}") from exc
    return metadata, identity


def file_record(path: str, content: bytes) -> dict:
    metadata, identity = _metadata(path, content)
    canonical = json.dumps(metadata, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return {
        "sha256": hashlib.sha256(content).hexdigest(),
        "size": len(content),
        "identity": identity,
        "metadata": metadata,
        "metadata_fingerprint": hashlib.sha256(canonical).hexdigest(),
    }


def _new_snapshot(source: str, ref: str) -> dict:
    if source not in LOCKED_SOURCES:
        raise SnapshotError(f"unsupported source: {source}")
    return {"schema_version": 1, "source": source, "repository": LOCKED_SOURCES[source]["repo"], "ref": validate_locked_ref(ref), "files": {}, "failures": []}


def snapshot_directory(root: Path, source: str, ref: str, selected: list[str]) -> dict:
    root = Path(root)
    if not root.is_dir():
        raise SnapshotError(f"source directory does not exist: {root}")
    result = _new_snapshot(source, ref)
    patterns = selected
    for file in sorted(root.rglob("*")):
        if not file.is_file() or file.is_symlink():
            continue
        relative = file.relative_to(root).as_posix()
        if not _selected(relative, patterns):
            continue
        try:
            result["files"][relative] = file_record(relative, file.read_bytes())
        except (OSError, SnapshotError) as exc:
            result["failures"].append({"path": relative, "error": type(exc).__name__})
    for path in selected:
        if not any(char in path for char in "*?[") and path not in result["files"]:
            result["failures"].append(path)
    return result


def snapshot_archive(archive: Path, source: str, ref: str, selected: list[str]) -> dict:
    archive = Path(archive)
    if not archive.is_file():
        raise SnapshotError(f"archive does not exist: {archive}")
    result = _new_snapshot(source, ref)
    patterns = selected
    try:
        with tarfile.open(archive, "r:*") as tar:
            expected_root = f"{LOCKED_SOURCES[source]['repo'].rsplit('/', 1)[-1]}-{validate_locked_ref(ref)}"
            roots = {PurePosixPath(member.name).parts[0] for member in tar.getmembers() if PurePosixPath(member.name).parts}
            if roots != {expected_root}:
                raise SnapshotError(f"archive root does not match repository and locked SHA: expected {expected_root}")
            members = sorted((m for m in tar.getmembers() if m.isfile()), key=lambda m: m.name)
            # GitHub archives have one generated top-level directory; strip only that component.
            for member in members:
                parts = PurePosixPath(member.name).parts
                if len(parts) < 2:
                    continue
                relative = PurePosixPath(*parts[1:]).as_posix()
                if not _selected(relative, patterns):
                    continue
                stream = tar.extractfile(member)
                if stream is None:
                    result["failures"].append({"path": relative, "error": "UnreadableArchiveMember"})
                    continue
                try:
                    result["files"][relative] = file_record(relative, stream.read())
                except (OSError, SnapshotError) as exc:
                    result["failures"].append({"path": relative, "error": type(exc).__name__})
    except SnapshotError:
        raise
    except (tarfile.TarError, OSError) as exc:
        raise SnapshotError(f"unable to read archive: {type(exc).__name__}") from exc
    return result


def snapshot_discovery(path: Path, ref: str, selected_ids: list[str]) -> dict:
    if not selected_ids:
        raise SnapshotError("legacy discovery requires one or more explicit category/name selectors")
    try:
        import yaml
        source_bytes = Path(path).read_bytes()
        document = yaml.safe_load(source_bytes.decode("utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SnapshotError(f"unable to read legacy discovery queue: {type(exc).__name__}") from exc
    result = _new_snapshot("legacy", ref)
    selected = set(selected_ids)
    available = set()
    for category in document.get("categories", []):
        category_id = str(category.get("id", ""))
        for entry in category.get("entries", []):
            name = str(entry.get("name", ""))
            identity = f"{category_id}/{name}"
            available.add(identity)
            if identity not in selected:
                continue
            public_metadata = {key: entry[key] for key in ("name", "url", "source", "platform", "note", "subcat") if key in entry}
            raw = json.dumps(public_metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
            result["files"][identity] = {
                "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw), "identity": identity,
                "metadata": public_metadata, "metadata_fingerprint": hashlib.sha256(raw).hexdigest(),
            }
    result["failures"] = sorted(selected - available)
    result["selection"] = sorted(selected)
    result["input_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    return result


def diff_snapshots(baseline: dict, candidate: dict) -> dict:
    old, new = baseline.get("files", {}), candidate.get("files", {})
    removed, added = set(old) - set(new), set(new) - set(old)
    changes = []
    # Identity is the strongest rename signal; equal content hash is the fallback.
    pairs = []
    for left in sorted(removed):
        old_id = old[left].get("identity")
        match = next((right for right in sorted(added) if old_id and new[right].get("identity") == old_id), None)
        if match is None:
            match = next((right for right in sorted(added) if old[left].get("sha256") == new[right].get("sha256")), None)
        if match is not None:
            pairs.append((left, match))
            added.remove(match)
    for left, right in pairs:
        removed.remove(left)
        changes.append({"kind": "rename", "from": left, "to": right, "content_changed": old[left].get("sha256") != new[right].get("sha256"), "old_metadata": old[left].get("metadata", {}), "new_metadata": new[right].get("metadata", {})})
    for path in sorted(set(old) & set(new)):
        if old[path].get("sha256") != new[path].get("sha256"):
            changes.append({"kind": "changed", "path": path, "old_metadata": old[path].get("metadata", {}), "new_metadata": new[path].get("metadata", {})})
    changes.extend({"kind": "removed", "path": path, "old_metadata": old[path].get("metadata", {})} for path in sorted(removed))
    changes.extend({"kind": "added", "path": path, "new_metadata": new[path].get("metadata", {})} for path in sorted(added))
    return {"source": candidate.get("source"), "from_ref": baseline.get("ref"), "to_ref": candidate.get("ref"), "changes": changes, "failures": candidate.get("failures", [])}


def review_diff(baseline: dict, candidate: dict) -> dict:
    difference = diff_snapshots(baseline, candidate)
    difference["complete"] = not candidate.get("failures") and candidate.get("complete", True)
    if not difference["complete"]:
        difference["suppressed_incomplete_removals"] = [
            change for change in difference["changes"] if change["kind"] in {"removed", "rename"}
        ]
        difference["changes"] = [
            change for change in difference["changes"] if change["kind"] not in {"removed", "rename"}
        ]
    return difference
