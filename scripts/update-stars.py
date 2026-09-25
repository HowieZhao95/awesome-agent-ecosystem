#!/usr/bin/env python3
"""Incrementally refresh GitHub repository metadata in resources.yaml."""
import argparse
import datetime
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "resources.yaml"
STATE = ROOT / "data" / "github-repo-state.json"
REPO_RE = re.compile(r"github\.com/([^/]+)/([^/?#]+)", re.IGNORECASE)


class ScanFailed(RuntimeError):
    """Raised when a complete repository scan cannot be obtained."""


@dataclass(frozen=True)
class ScanResult:
    updated_entries: int
    checked_repos: int
    not_modified_repos: int
    skipped_entries: int
    missing_repos: tuple[str, ...]


def repo_of(url):
    match = REPO_RE.search(url or "")
    if not match:
        return None
    repo = match.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{match.group(1)}/{repo}".lower()


def _load_state(path):
    if not path.exists():
        return {"version": 1, "repos": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScanFailed(f"cannot read state file {path}: {exc}") from exc
    if state.get("version") != 1 or not isinstance(state.get("repos"), dict):
        raise ScanFailed(f"unsupported state file format: {path}")
    return state


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def run(data_file=DATA, state_file=STATE, session=None, token=None, today=None):
    data_file = Path(data_file)
    state_file = Path(state_file)
    session = session or requests.Session()
    today = today or str(datetime.date.today())

    raw = data_file.read_text(encoding="utf-8")
    doc = yaml.safe_load(raw)
    state = _load_state(state_file)
    entries_by_repo = {}
    skipped = 0
    for category in doc["categories"]:
        for entry in category["entries"]:
            repo = repo_of(entry.get("url"))
            if repo:
                entries_by_repo.setdefault(repo, []).append(entry)
            else:
                skipped += 1

    base_headers = {"Accept": "application/vnd.github+json"}
    if token:
        base_headers["Authorization"] = f"Bearer {token}"

    fetched = {}
    not_modified = 0
    missing_repos = []
    next_state = json.loads(json.dumps(state))
    for repo in sorted(entries_by_repo):
        headers = dict(base_headers)
        old_repo_state = state["repos"].get(repo, {})
        if old_repo_state.get("etag"):
            headers["If-None-Match"] = old_repo_state["etag"]
        try:
            response = session.get(
                f"https://api.github.com/repos/{repo}", headers=headers, timeout=15
            )
        except requests.RequestException as exc:
            raise ScanFailed(f"{repo}: {exc}") from exc
        if response.status_code == 304:
            not_modified += 1
            continue
        if response.status_code in (404, 410):
            missing_repos.append(repo)
            continue
        if response.status_code != 200:
            raise ScanFailed(f"{repo}: HTTP {response.status_code}")
        try:
            payload = response.json()
        except (ValueError, TypeError) as exc:
            raise ScanFailed(f"{repo}: invalid JSON response") from exc
        if not isinstance(payload.get("stargazers_count"), int):
            raise ScanFailed(f"{repo}: response has no integer stargazers_count")
        fetched[repo] = payload["stargazers_count"]
        metadata = {"etag": response.headers.get("ETag", ""), "stars": payload["stargazers_count"]}
        for key in ("html_url", "description", "pushed_at", "default_branch", "archived", "topics"):
            if key in payload:
                metadata[key] = payload[key]
        next_state["repos"][repo] = metadata

    updated_entries = 0
    for repo, stars in fetched.items():
        for entry in entries_by_repo[repo]:
            if entry.get("stars") is not None and entry["stars"] != stars:
                entry["stars"] = stars
                updated_entries += 1

    if updated_entries:
        doc["meta"]["updated"] = today
        meta_offset = raw.find("meta:")
        prefix = raw[:meta_offset] if meta_offset >= 0 else ""
        rendered = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
        _atomic_write(
            data_file,
            prefix + rendered,
        )

    if next_state != state:
        _atomic_write(
            state_file,
            json.dumps(next_state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )

    return ScanResult(updated_entries, len(entries_by_repo), not_modified, skipped, tuple(missing_repos))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--state", type=Path, default=STATE)
    args = parser.parse_args()
    try:
        result = run(args.data, args.state, token=os.environ.get("GITHUB_TOKEN"))
    except ScanFailed as exc:
        parser.exit(1, f"ERROR: scan aborted; no changes written: {exc}\n")
    print(
        f"Done. {result.updated_entries} entries updated across "
        f"{result.checked_repos} unique repos; {result.not_modified_repos} not modified; "
        f"{result.skipped_entries} non-GitHub entries skipped."
    )
    for repo in result.missing_repos:
        print(f"::warning::GitHub reference unavailable (404/410): {repo}")


if __name__ == "__main__":
    main()
