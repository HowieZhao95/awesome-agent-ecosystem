#!/usr/bin/env python3
"""Read a locked public source snapshot and write review-only metadata diffs."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import re

import requests
import yaml

from source_tools.core import LOCKED_SOURCES, SnapshotError, review_diff, snapshot_archive, snapshot_directory, snapshot_discovery, validate_locked_ref


ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_baseline(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value.get("snapshot", value)


def _compare_with_baseline(baseline_path: Path, snapshot: dict) -> dict:
    baseline = _load_baseline(baseline_path)
    snapshot["complete"] = snapshot.get("complete", True)
    return review_diff(baseline, snapshot)


def _validate_output(path: Path, baseline: Path | None) -> None:
    output = path.resolve()
    data_root = (ROOT / "data").resolve()
    canonical = {
        (ROOT / "data/resources.yaml").resolve(), (ROOT / "data/sources.yaml").resolve(),
        (ROOT / "data/categories.yaml").resolve(), (ROOT / "README.md").resolve(),
        (ROOT / "site/data.js").resolve(), (ROOT / "site/catalog.json").resolve(),
    }
    if output in canonical:
        raise SnapshotError("review output cannot target canonical catalog or generated files")
    if output == data_root or data_root in output.parents:
        raise SnapshotError("review output cannot be written under canonical data/")
    if baseline and output == baseline.resolve():
        raise SnapshotError("review output cannot overwrite its baseline")


def catalog_paths(source: str, resources_file: Path) -> list[dict]:
    if source == "legacy":
        return []
    resources = _load_yaml(resources_file)["resources"]
    source_id = {"opendesign": "opendesign", "remotion": "remotion-dev.skills"}[source]
    rows = []
    for item in resources:
        upstream = item.get("provenance", {}).get("upstream", {})
        if item.get("provenance", {}).get("content_source") != source_id or upstream.get("kind") != "git":
            continue
        ref = upstream.get("ref", {})
        license_data = item.get("license", {})
        rows.append({
            "resource_id": item["id"], "path": upstream.get("path"), "ref": ref.get("value"), "selector": upstream.get("selector"),
            "catalog_metadata": {
                key: item[key] for key in ("title", "summary", "purpose") if key in item
            } | {"license": {key: license_data[key] for key in ("status", "expression", "scope", "redistribution") if key in license_data}},
        })
    return rows


def source_record(source: str, sources_file: Path) -> dict:
    source_id = {"opendesign": "opendesign", "remotion": "remotion-dev.skills", "legacy": "discover.awesome-agent-ecosystem"}[source]
    for record in _load_yaml(sources_file)["sources"]:
        if record["id"] == source_id:
            return record
    raise SnapshotError(f"source is not declared in data/sources.yaml: {source_id}")


def source_scope(source: str, sources_file: Path) -> list[str]:
    scope = source_record(source, sources_file).get("tracking", {}).get("scope", [])
    if isinstance(scope, list):
        return scope
    patterns = re.findall(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._*-]+)+/\*\*", str(scope))
    if not patterns:
        raise SnapshotError(f"unable to resolve selected scope from data/sources.yaml for {source}")
    return patterns


def _download_archive(url: str, ref: str, repo: str, directory: Path) -> Path:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "codeload.github.com"}:
        raise SnapshotError("URL input must be an official GitHub HTTPS archive URL")
    path = parsed.path.strip("/")
    if parsed.hostname == "github.com":
        expected = f"{repo}/archive/{ref}.tar.gz"
    else:
        expected = f"{repo}/tar.gz/{ref}"
    if path != expected:
        raise SnapshotError(f"archive URL must identify {repo} at the locked commit SHA")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    archive = directory / "upstream.tar.gz"
    archive.write_bytes(response.content)
    return archive


def run(args) -> dict:
    if args.source not in LOCKED_SOURCES:
        raise SnapshotError("only selected public content sources are supported")
    ref = validate_locked_ref(args.ref)
    declared_source = source_record(args.source, args.sources)
    repo = LOCKED_SOURCES[args.source]["repo"]
    if args.source == "legacy":
        repo = urlparse(declared_source.get("url", "")).path.strip("/").split("/", 1)[0] + "/" + urlparse(declared_source.get("url", "")).path.strip("/").split("/", 1)[1]
    if args.source == "legacy":
        if args.directory or args.archive or args.url:
            raise SnapshotError("legacy discovery reads only --discovery YAML and selected --discovery-id entries")
        snapshot = snapshot_discovery(args.discovery, ref, args.discovery_id)
        try:
            snapshot["input_path"] = args.discovery.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            snapshot["input_path"] = "<local-discovery-input>"
        snapshot["ref_binding"] = "local queue SHA-256 recorded; supplied ref is the legacy discovery baseline pointer"
        snapshot["complete"] = not snapshot["failures"]
        report = {"snapshot": snapshot, "diff": None}
        if args.baseline:
            report["diff"] = _compare_with_baseline(args.baseline, snapshot)
        return report
    if args.directory and args.archive or args.directory and args.url or args.archive and args.url:
        raise SnapshotError("choose exactly one input: --directory, --archive, or --url")
    if not (args.directory or args.archive or args.url):
        raise SnapshotError("an input is required")
    if args.discovery_id:
        raise SnapshotError("--discovery-id is only valid with --source legacy")
    catalog = catalog_paths(args.source, args.resources)
    patterns = source_scope(args.source, args.sources)
    if args.directory:
        snapshot = snapshot_directory(args.directory, args.source, ref, patterns)
        snapshot["ref_binding"] = "caller-supplied SHA; local directory content is fingerprinted, commit identity is unverified"
    elif args.archive:
        snapshot = snapshot_archive(args.archive, args.source, ref, patterns)
        snapshot["ref_binding"] = "archive root matched repository name and full commit SHA"
    else:
        with tempfile.TemporaryDirectory(prefix="source-sync-") as temp:
            archive = _download_archive(args.url, ref, repo, Path(temp))
            snapshot = snapshot_archive(archive, args.source, ref, patterns)
            snapshot["ref_binding"] = "official GitHub URL and archive root matched repository name and full commit SHA"
    paths = snapshot["files"]
    linked = []
    missing = []
    for row in catalog:
        if not row["path"]:
            continue
        (linked if row["path"] in paths else missing).append({**row, "exists": row["path"] in paths})
    snapshot["catalog_records"] = [{**row, "candidate_ref_matches_catalog_ref": row["ref"] == ref} for row in linked]
    snapshot["catalog_baseline_refs"] = sorted({row["ref"] for row in catalog if row["ref"]})
    snapshot["catalog_metadata_comparisons"] = [
        {
            "resource_id": row["resource_id"], "path": row["path"],
            "catalog_metadata": row["catalog_metadata"],
            "source_metadata": paths.get(row["path"], {}).get("metadata", {}),
            "source_sha256": paths.get(row["path"], {}).get("sha256"),
        }
        for row in linked
    ]
    snapshot["catalog_missing_paths"] = missing
    snapshot["complete"] = not snapshot["failures"]
    report = {"snapshot": snapshot, "diff": None}
    if args.baseline:
        report["diff"] = _compare_with_baseline(args.baseline, snapshot)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=sorted(LOCKED_SOURCES))
    parser.add_argument("--ref", required=True, help="full immutable commit SHA")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--directory", type=Path)
    inputs.add_argument("--archive", type=Path)
    inputs.add_argument("--url", help="official GitHub archive URL at --ref")
    parser.add_argument("--baseline", type=Path, help="prior metadata snapshot; never overwritten")
    parser.add_argument("--resources", type=Path, default=ROOT / "data/resources.yaml")
    parser.add_argument("--discovery", type=Path, default=ROOT / "data/discovery/legacy-v2.yaml")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/sources.yaml")
    parser.add_argument("--discovery-id", action="append", default=[], help="legacy queue selector CATEGORY/NAME; repeat to select multiple entries")
    parser.add_argument("--output", type=Path, required=True, help="review evidence JSON outside canonical data")
    args = parser.parse_args(argv)
    try:
        _validate_output(args.output, args.baseline)
        if args.source == "legacy":
            if args.directory or args.archive or args.url or not args.discovery_id:
                raise SnapshotError("legacy source requires --discovery-id and does not take archive/directory/URL input")
        elif not (args.directory or args.archive or args.url):
            raise SnapshotError("a directory, archive, or URL input is required")
        report = run(args)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix(args.output.suffix + ".tmp")
        temp.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp.replace(args.output)
        print(json.dumps({"output": str(args.output), "files": len(report["snapshot"]["files"]), "complete": report["snapshot"]["complete"], "change_count": len((report.get("diff") or {}).get("changes", []))}, ensure_ascii=False))
        return 0 if report["snapshot"]["complete"] else 2
    except (SnapshotError, OSError, ValueError, requests.RequestException) as exc:
        print(f"source-sync: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
