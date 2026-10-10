# Web Prototype P0 content review

This is the single owner-selected asset fixture. It does not approve the full
candidate catalog or mark the upstream resource usage-tested.

- Resource: `opendesign.web-prototype`; source: `opendesign`.
- Repository: `nexu-io/open-design`.
- Fixed source commit: `17e255959703a3fad7c8eb7f7b70dcafccc5629a`.
- Root: `plugins/_official/examples/web-prototype`; package version: `0.1.1`.
- Complete package: `SKILL.md`, `assets/template.html`, `example.html`,
  `open-design.json`, `references/checklist.md`, `references/layouts.md`.
- Repository `LICENSE` is also retained as `UPSTREAM-LICENSE`.
- Seven files, 63,292 bytes. All bytes were fetched at the fixed commit and
  matched the source report's SHA-256 values.

## License evidence and review decision

Package metadata declares MIT. The repository LICENSE contains Apache-2.0;
there is no separate LICENSE inside this six-file package. Both declarations
and the original repository license text are preserved, rather than silently
relabeling the asset. Content publication requires the owner's explicit review
of this discrepancy. Source report PR approval alone does not authorize it.

## Consumption and rollback

The two HTML files inspected here contain no scripts or external fonts, images,
or scripts. Content is treated as data, never executed by the supply process.
The product consumer freezes each verified text file as a download attachment,
preserves relative directories, then projects stable IDs into the existing
platform asset library inside one database transaction.

Release identity is the public merge commit plus SHA-256 of the exact manifest
bytes. The manifest does not embed its own merge commit or digest. COS keys use
the manifest digest; retries and a revert to previous manifest bytes reuse
verified frozen content. Reverting to the pre-import version withdraws this
asset's directory projection while retaining its frozen files.

## Validation boundary

The manifest is a file inventory, not a second approval system. GitHub PR and
protected main remain the approval and audit surface. The source workflow only
updates review reports and this selected manifest. The private product consumes
an explicitly selected merged public commit; credentials remain private.

No COS write, product import, live retry, or live product rollback is claimed by
this review. These require the content publication decision and real receipts.
