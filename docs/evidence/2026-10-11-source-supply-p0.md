# Source supply P0 live acceptance — 2026-10-11

Source truth: `HowieZhao95/awesome-agent-ecosystem`.
Private consumer: `HowieZhao95/my-apps`, existing COS and asset library.
No supply database, second producer/runtime, admin UI or approval platform was added.

## Selected release

- Resource `opendesign.web-prototype`, source `opendesign`, package `0.1.1`.
- Upstream `nexu-io/open-design@17e255959703a3fad7c8eb7f7b70dcafccc5629a`.
- Six complete package files plus repository LICENSE: seven files, 63,292 bytes.
- Exact manifest SHA-256: `6425321571c33c9341f458647418337c046a2c8c7771ad5bbf8ce7207d60ebb8`.
- Package MIT declaration and repository Apache-2.0 license are both retained.
  The owner explicitly approved this single content packet in
  [PR #4](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/4),
  merged at `5356dc207bc2a99e7e3a7fb58673a6537a38f656`.
  This does not promote the full discovery catalog or claim host usage testing.

## Real receipts

| Scenario | Evidence |
| --- | --- |
| Source acquisition / repeat | [weekly-sync 38077102820](https://github.com/HowieZhao95/awesome-agent-ecosystem/actions/runs/38077102820) passed; no duplicate candidate PR. |
| First directory import | [consumer 38077476093](https://github.com/HowieZhao95/my-apps/actions/runs/38077476093) passed; readback matched seven platform items, stable IDs and relative paths. |
| Same-release repeat | [consumer 38079629609](https://github.com/HowieZhao95/my-apps/actions/runs/38079629609) returned `unchanged: true`, seven items, zero uploads. IDs, paths and row update timestamps were unchanged. |
| Source change | [Real historical replay](2026-10-11-web-prototype-source-change.json) fetched both complete seven-file versions at `c12c816a44c2f10ce18423f074d2482046cfd869` and `17e255959703a3fad7c8eb7f7b70dcafccc5629a`. Five changed files updated the candidate report/manifest through production functions, preserving resource identity. Repeating the candidate write did nothing. The historical candidate was not published. |
| Failure and retry | A single local process used an unreachable database, leaving the real directory at zero items after seven verified COS freezes. Consumer 38077476093 then retried the same approved release successfully. Production connection settings were not changed. |
| Git revert | [PR #5](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/5) reverted the initial release and merged at `2a85b43f3f7955eeadd99eb4407e605c0b756126`. [Consumer 38080170728](https://github.com/HowieZhao95/my-apps/actions/runs/38080170728) succeeded; readback found zero collections and zero items for this resource. |
| Frozen content after withdrawal | With the upstream content API explicitly blocked in one process, all seven frozen files verified from COS, missing objects = zero, attempted upstream calls = zero. |

This restoration reverts the rollback to the exact original manifest bytes.
The post-merge restoration receipt is recorded in the private P0 plan and the
catalog-projection Actions run; its expected result is the original seven IDs
and frozen paths, with no re-upload. Source Git history remains the rollback authority.

## Permissions and validation

- Public main requires a PR and `validate`, with zero required approving reviewers,
  administrator enforcement, and no force push or deletion.
- The private consumer uses `contents: read`, manual dispatch and default dry-run.
  Three credentials remain encrypted Secrets; non-sensitive storage configuration
  uses Variables so boolean receipt fields remain readable.
- Database role `td_catalog_projection_p0` has only the two existing asset tables;
  no role creation, RLS bypass or writes outside those tables were granted.
- COS API-only user `catalog-projection-p0` has HeadObject/GetObject/PutObject only
  under `design/catalog/opendesign.web-prototype/*`. Live probes confirmed in-prefix
  write/read, out-of-prefix write rejection and delete rejection. Probe files were cleaned.
- The misplaced private producer was replaced by the thin consumer in
  [PR #30](https://github.com/HowieZhao95/my-apps/pull/30) and
  [PR #31](https://github.com/HowieZhao95/my-apps/pull/31).
- Public checks: 109 Python tests, 50 Node tests, typecheck, package/site production
  build and external packaged-host typecheck/build. Private affected checks:
  77 asset-library tests, 169 skill-catalog tests, relevant typechecks and formatting.
- Unrelated full-private-repository CI failures remain recorded: auth scanner
  findings, plus desktop tests lacking Bun and containing stale assertions/mocks.
  The owner explicitly authorized simple verification without a temporary worktree.
  No canvas UI work was included in the private publication tree.

The initial private publication's Vercel Production deployment reached Ready.
These receipts establish the supply/directory path; they are not a Web/Desktop
interactive template-usage acceptance or a claim that every monorepo check passed.
