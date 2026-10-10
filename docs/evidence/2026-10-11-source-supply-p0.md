# Source supply P0 live acceptance — 2026-10-11

Target repository: `HowieZhao95/awesome-agent-ecosystem`.
The private product repository `HowieZhao95/my-apps` is a separate consumer;
its commits are not part of this repository's publication history.

## Proven

- [weekly-sync run 38072615504](https://github.com/HowieZhao95/awesome-agent-ecosystem/actions/runs/38072615504)
  completed successfully at source revision `f12ecd10c67a721d1d9055974f8d659b18505b72`.
- [Source report PR #1](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/1)
  was approved by the owner and merged at `c60925acdd909f439d3e867db8e101159a6cdbe8`.
  Its final head `d1f74ede63958e20d6b43552893205a3f7198317` changed only two
  source report JSON files; it did not approve or publish asset content.
- OpenDesign snapshot: commit `17e255959703a3fad7c8eb7f7b70dcafccc5629a`,
  5,172 files, `complete: true`, no read failures or missing catalog paths.
  Its 5,078 additions also reflect the expanded selected scope relative to the
  historical 94-file baseline; they are not proof of 5,078 newly authored files.
- Remotion snapshot: commit `32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5`,
  145 files, `complete: true`, 22 changed files, no read failures or missing catalog paths.
- Local checks after the corrective changes: 95 Python tests, 50 Node tests,
  TypeScript check, package/site production build, and an external packaged host
  typecheck/build from an empty npm cache passed.
- The empty-cache host failure was reproduced before replacing forced offline
  installation with cache-preferred installation. Partial snapshot replacement
  was reproduced before making collection fail on incomplete snapshots.
- [quality-gate run 38073167632](https://github.com/HowieZhao95/awesome-agent-ecosystem/actions/runs/38073167632)
  passed all gates at revision `509510d0f7c2e89c6034ac7c2e238335f759aade`.
- Two real Remotion fetches returned the same 145-file report at the same commit.
  Report SHA-256: `eb6a7854c5c0c8b915af5f8bd9f3289b802bfd2c9b566d10a3aec7f0641a7ad8`;
  the second write returned `changed: []`.
- `main` now requires a PR and the `validate` check, with zero required approving
  reviewers (one-person operation). Force pushes and branch deletion are disabled.
- The misplaced `my-apps/catalog-supply` workflow is `disabled_manually`; only
  this public repository runs source acquisition.
- [Scope correction PR #3](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/3)
  merged at `d06e5bdcda0d439e44a3fb8c543e3de72e505360` after owner approval.
  [weekly-sync 38073773581](https://github.com/HowieZhao95/awesome-agent-ecosystem/actions/runs/38073773581)
  passed with only controlled source acquisition.
- [Post-merge quality-gate 38074381601](https://github.com/HowieZhao95/awesome-agent-ecosystem/actions/runs/38074381601)
  passed at the source-report merge commit `c60925acdd909f439d3e867db8e101159a6cdbe8`.
- The owner selected Web Prototype as the sole content fixture. Its seven-file
  inventory and license discrepancy are documented in
  [the content review](2026-10-11-web-prototype-review.md).

## Not yet proven

- The content manifest PR must pass generated-output and external-host gates.
- No candidate content approval has been inferred from successful CI.
- Fixed catalog release, approved-content freezing to COS, product directory
  synchronization, failed-sync retry, and product rollback have no live receipt.
  Reverting a review report alone does not prove product rollback.
- The owner clarified that COS/database credentials are in the local private
  myApps configuration. They are not copied into this public repository.

The P0 objective remains incomplete until the publication and consumer receipts
exist. Candidate collection success must not be reported as end-to-end closure.
