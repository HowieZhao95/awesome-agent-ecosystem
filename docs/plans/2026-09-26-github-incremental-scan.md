# GitHub Incremental Scan Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use test-driven-development to implement each behavior with a failing test first.

**Goal:** Make scheduled GitHub Actions runs discover new entries and refresh referenced GitHub resource metadata without needless data churn or silent failures.

**Architecture:** Keep `data/resources.yaml` as the catalog source. `update-stars.py` groups GitHub URLs by repository, uses conditional requests with saved ETags, updates changed metrics only, and emits a run summary. The workflow validates and builds before opening a review PR only when catalog outputs change.

**Tech Stack:** Python 3, PyYAML, `requests`, GitHub REST API, GitHub Actions.

---

### Task 1: Define scanner behavior

**Files:** Create `tests/test_update_stars.py`; modify `scripts/update-stars.py`.

1. Write tests for GitHub URL parsing, deduplicated repository requests, 200 and 304 responses, changed star counts, unchanged output, and API failure handling.
2. Run `/tmp/awesome-agent-ecosystem-venv/bin/python -m unittest discover -s tests -v`; confirm the new tests fail for missing behavior.
3. Implement the smallest scanner that passes these tests, using `GITHUB_TOKEN` and a deterministic cache file in `data/`.
4. Run the tests and confirm they pass.

### Task 2: Make import and build runs deterministic

**Files:** Modify `scripts/import-marketplace.py`, `scripts/import-skills-mcp.py`, `scripts/build.py` as needed; test in `tests/`.

1. Write a failing test for URL based duplicate detection and no rewrite when nothing changes.
2. Run the test and confirm the expected failure.
3. Apply minimal import changes, then rerun tests and validate the catalog.

### Task 3: Wire GitHub Actions

**Files:** Modify `.github/workflows/weekly-sync.yml` and `.github/workflows/quality-gate.yml`.

1. Use the built-in `github.token`, required write permissions, concurrency, dependency installation from `requirements.txt`, and explicit validation/build steps.
2. Run the scanner and imports with failures visible. Put scan summary into the PR body or workflow summary.
3. Run automated tests in the quality gate. Keep the PR branch stable so repeated runs update one PR.

### Task 4: Document and verify

**Files:** Modify `MAINTENANCE.md`, `CONTRIBUTING.md` if behavior changes.

1. Document setup, token/PR setting, schedule, cache semantics, local commands, and review flow.
2. Run tests, `scripts/validate.py`, and `scripts/build.py`; verify generated files and a second scan with fixture responses are unchanged.

### Verification record

- `python -m unittest discover -s tests -v`: 12 passing tests, including red-to-green checks for URL deduplication, pagination, optional-source failure, conditional GitHub requests, metadata capture, curated empty stars, and all-or-nothing API failure.
- `python scripts/validate.py`: 803 entries pass.
- `python scripts/build.py`: README and site output hashes unchanged.
- Live one-repository scan using temporary files: an initial run returned data and a second request returned `304`. A later unauthenticated rerun hit GitHub's shared IP rate limit; Actions uses its built-in authenticated token.
- Workflow YAML parsed locally. GitHub Actions itself cannot run until this directory is a GitHub repository.
