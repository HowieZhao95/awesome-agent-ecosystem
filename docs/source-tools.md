# Source snapshot and review tool

## Weekly candidate automation

`.github/workflows/weekly-sync.yml` runs `scripts/auto-source-sync.py` for the
locked sources whose `data/sources.yaml` record declares `tracking.cadence:
weekly` (currently OpenDesign and Remotion). The job resolves the watched
branch to a full commit SHA, downloads the official GitHub archive at that SHA,
reuses `scripts/source-sync.py`, and writes deterministic candidate reports to
`docs/evidence/source-sync/<source>.json`. The same workflow opens the review
PR after all selected sources succeed.

The automation never edits `data/resources.yaml`, `data/sources.yaml`, or
generated site files. It writes no partial candidate set when one source
fails, and an unchanged candidate produces no diff. Merging the PR remains the
one-person review/promotion decision; reverting the PR restores the prior
candidate evidence.

`scripts/source-sync.py` creates metadata-only snapshots for the public sources selected in `data/sources.yaml`. The source scope is read from that file at runtime. The tool compares a candidate snapshot with an optional prior snapshot and writes a review report to the requested output path. It does not edit `data/resources.yaml`, `data/sources.yaml`, discovery data, or generated site files, and it never promotes a candidate.

Install the project Python dependencies first with `python -m pip install -r requirements.txt`. Use a full commit SHA for every public Git snapshot. A branch name or tag is rejected. GitHub archive URLs must be HTTPS URLs for the declared repository and exact SHA. Tar archive roots must match `<repository-name>-<full-sha>`. A local directory is useful for inspection, but its relationship to the supplied SHA cannot be verified; the report marks that ref as caller-supplied. The archive URL path verifies the source locator and archive root, not the source publisher's rights claims.

```sh
python scripts/source-sync.py \
  --source opendesign \
  --ref 53231d40b778d88eba23f35547bf99485d3ae9fc \
  --archive /path/to/open-design-53231d40b778d88eba23f35547bf99485d3ae9fc.tar.gz \
  --output docs/evidence/phase2/source-opendesign.json

python scripts/source-sync.py \
  --source remotion \
  --ref 473352613039e718e46655a26df224851e84c4aa \
  --url https://codeload.github.com/remotion-dev/skills/tar.gz/473352613039e718e46655a26df224851e84c4aa \
  --output docs/evidence/phase2/source-remotion.json

python scripts/source-sync.py \
  --source legacy \
  --ref f8da353b267033f97837d61d3bb95f96882b34aa \
  --discovery-id skills/webapp-testing \
  --discovery-id skills/skill-creator \
  --output docs/evidence/phase2/source-legacy-subset.json
```

To compare against a prior report, pass its path with `--baseline` and write to a different `--output`. Reports wrap the raw snapshot in a `snapshot` field, so they can be supplied directly as baselines. Output paths cannot overwrite files under `data/`, generated catalog files, or the baseline.

Each file record contains its path, size, SHA-256, a fingerprint of extracted metadata, and only selected manifest or Skill frontmatter fields. File bodies and private product sources are never copied. The catalog comparison section joins each matched source path to its current resource id, title, summary, purpose, license metadata, selector, and recorded ref. Candidate ref differences are shown for review; the catalog remains unchanged.

Diffs identify additions, content changes, removals, and renames. A rename is paired first by stable manifest/Skill identity and then by equal content hash; duplicate-content matches are paired deterministically one-to-one by sorted path. An incomplete read still emits a candidate report with failures. In that case possible removals and renames are listed under `suppressed_incomplete_removals`, not proposed as changes. Exit codes are `0` for a complete snapshot, `2` for a partial snapshot, and `1` for an input or validation failure. The supplied baseline is read-only in all cases.

The legacy queue mode requires explicit `CATEGORY/NAME` selectors and emits only those entries' public discovery metadata. It omits stars and install counts. The report hashes the local queue input; its `--ref` is the legacy source's recorded baseline pointer, not proof that the working file came from that historical commit.
