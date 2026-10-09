#!/usr/bin/env python3
"""Resolve selected upstream refs and write review-only candidate reports.

This is the automation bridge around ``source-sync.py``. It never edits the
catalog, the source registry, or generated site files. A successful run writes
deterministic candidate evidence files; the existing weekly-sync workflow then
opens a PR for one-person review.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
SOURCE_SYNC_SPEC = importlib.util.spec_from_file_location(
    "source_sync", ROOT / "scripts/source-sync.py"
)
SOURCE_SYNC = importlib.util.module_from_spec(SOURCE_SYNC_SPEC)
SOURCE_SYNC_SPEC.loader.exec_module(SOURCE_SYNC)

AUTOMATED_SOURCE_MAP = {
    "opendesign": {
        "record_id": "opendesign",
        "repo": "nexu-io/open-design",
        "watch_ref": "main",
        "baseline": "docs/evidence/phase2/source-opendesign.json",
    },
    "remotion": {
        "record_id": "remotion-dev.skills",
        "repo": "remotion-dev/skills",
        "watch_ref": "main",
        "baseline": "docs/evidence/phase2/source-remotion.json",
    },
}


def resolve_commit(repo: str, ref: str, token: str | None = None, *, get=requests.get) -> str:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "awesome-agent-ecosystem-source-sync"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = get(f"https://api.github.com/repos/{repo}/commits/{ref}", headers=headers, timeout=60)
    response.raise_for_status()
    sha = str(response.json().get("sha", ""))
    if not SOURCE_SYNC.validate_locked_ref(sha):
        raise RuntimeError(f"GitHub did not return a full commit SHA for {repo}@{ref}")
    return sha.lower()


def archive_url(repo: str, sha: str) -> str:
    return f"https://codeload.github.com/{repo}/tar.gz/{sha}"


def automated_source_ids(sources_document: dict) -> list[str]:
    records = sources_document.get("sources", [])
    return [
        source_key
        for source_key, config in AUTOMATED_SOURCE_MAP.items()
        if any(
            record.get("id") == config["record_id"]
            and (record.get("tracking") or {}).get("cadence") == "weekly"
            for record in records
        )
    ]


def _download_archive(repo: str, sha: str, directory: Path, token: str | None) -> Path:
    headers = {"User-Agent": "awesome-agent-ecosystem-source-sync"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(archive_url(repo, sha), headers=headers, timeout=180)
    response.raise_for_status()
    archive = directory / "upstream.tar.gz"
    archive.write_bytes(response.content)
    return archive


def run_one(
    source_key: str,
    *,
    root: Path = ROOT,
    token: str | None = None,
    resolver=resolve_commit,
    downloader=_download_archive,
) -> dict:
    config = AUTOMATED_SOURCE_MAP[source_key]
    sha = resolver(config["repo"], config["watch_ref"], token)
    baseline = root / config["baseline"]
    if not baseline.is_file():
        raise RuntimeError(f"missing locked baseline for {source_key}: {baseline}")
    with tempfile.TemporaryDirectory(prefix=f"source-sync-{source_key}-") as temp:
        archive = downloader(config["repo"], sha, Path(temp), token)
        args = SimpleNamespace(
            source=source_key,
            ref=sha,
            directory=None,
            archive=archive,
            url=None,
            baseline=baseline,
            resources=root / "data/resources.yaml",
            discovery=root / "data/discovery/legacy-v2.yaml",
            sources=root / "data/sources.yaml",
            discovery_id=[],
            output=root / "docs/evidence/source-sync" / f"{source_key}.json",
        )
        return SOURCE_SYNC.run(args)


def collect_reports(source_keys: list[str], *, runner=run_one) -> dict[str, dict]:
    reports: dict[str, dict] = {}
    for source_key in source_keys:
        reports[source_key] = runner(source_key)
    return reports


def write_candidate_reports(reports: dict[str, dict], output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    changed: list[str] = []
    for source_key in sorted(reports):
        target = output_dir / f"{source_key}.json"
        serialized = json.dumps(reports[source_key], ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") == serialized:
            continue
        target.write_text(serialized, encoding="utf-8")
        changed.append(source_key)
    return changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", choices=sorted(AUTOMATED_SOURCE_MAP))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/evidence/source-sync")
    args = parser.parse_args(argv)
    try:
        sources_document = yaml.safe_load((ROOT / "data/sources.yaml").read_text(encoding="utf-8"))
        source_keys = args.source or automated_source_ids(sources_document)
        if not source_keys:
            raise RuntimeError("no weekly locked sources are configured")
        reports = collect_reports(source_keys, runner=lambda source: run_one(source, token=os.environ.get("GITHUB_TOKEN")))
        changed = write_candidate_reports(reports, args.output_dir)
        print(json.dumps({"sources": source_keys, "changed": changed, "output_dir": str(args.output_dir)}, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError, requests.RequestException) as exc:
        print(f"auto-source-sync: {exc}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
