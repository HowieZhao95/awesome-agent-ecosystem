# Selected upstream reuse assessment

This review compares the locked upstream snapshots with the current catalog records and the local ThusDesign design-system entry points. It identifies source material suitable for review and adaptation; it does not grant rights, claim execution compatibility, or move any candidate to a usable state.

## OpenDesign

The selected archive contains 94 files in the source scope from `data/sources.yaml`. All nine current OpenDesign preview paths resolve in the locked archive:

| Resource | Preview path | Snapshot check |
| --- | --- | --- |
| `opendesign.web-prototype` | `design-templates/web-prototype/example.html` | present |
| `opendesign.html-ppt-pitch-deck` | `design-templates/html-ppt-pitch-deck/example.html` | present |
| `opendesign.live-dashboard` | `design-templates/live-dashboard/example.html` | present |
| `opendesign.motion-frames` | `design-templates/motion-frames/example.html` | present |
| `opendesign.docs-page` | `design-templates/docs-page/example.html` | present |
| `opendesign.social-carousel` | `apps/web/public/community-templates/social-carousel.jpg` | present |
| `opendesign.agentic-design-system` | `design-systems/agentic/system/kit.html` | present |
| `opendesign.image-poster` | `design-templates/image-poster/example.html` | present |
| `opendesign.mockup-device-3d` | `plugins/_official/examples/mockup-device-3d/example.html` | present |

The full path-by-path result is in [`source-preview-path-check.txt`](evidence/phase2/source-preview-path-check.txt).

The agentic design-system folder includes `DESIGN.md`, manifests, `design-tokens.json`, `tokens.css`, Tailwind v4 CSS, static previews, and sample HTML. This is a substantive design-system reference. The current ThusDesign CSS entry at `packages/design-system/styles/globals.css` defines its own OKLCH semantic variables, including `--primary`, `--ring`, and `--sidebar-primary`. A source search across `packages/`, `apps/`, and `scripts/` found no code references to the OpenDesign asset paths or `opendesign` integration identifiers; its query and token sample are captured in [`source-runtime-boundary.txt`](evidence/phase2/source-runtime-boundary.txt). The practical boundary is therefore reference and possible manual adaptation; there is no evidence of a shared runtime module or direct code dependency.

OpenDesign examples and previews are content assets rather than reusable application modules. Their own package metadata may declare a license, while embedded images, fonts, names, and other external assets can have separate rights. The repository root license does not settle those per-asset questions.

## Remotion Skills

The fixed archive contains 145 files across the selected two Skill folders and their scoped supporting material. The catalog currently selects `skills/remotion-best-practices/SKILL.md` and `skills/remotion-render/SKILL.md`; their frontmatter metadata is present in the snapshot. These are agent instructions, not a JavaScript/React runtime library. A code search across `packages/`, `apps/`, and `scripts/` found no imports or runtime references to these Skills. Reuse is limited to linking or separately reviewing the instruction content and its terms; no runtime code reuse was observed.

## Existing generic viewer modules

The app already has generic image, video, and HTML preview code, but its packages are not public dependencies. The `ImageViewer` resolver imports `@repo/storage/url-utils`, and its shared `MediaItem` type imports desktop-aware `LocalMediaRef` from `@repo/relay-kit/agent-media`; the owning `@repo/design-system` package is private and has many other workspace dependencies. The complete ImageViewer module is therefore coupled to product storage and relay contracts.

`VideoPlayer` wraps the public `media-chrome` React controls, but it also imports the product `cn` helper and maps controls to host theme tokens. It is a useful implementation reference, while a public catalog page can use native `<video controls>` without importing the private design-system package. `@repo/browser-sandbox` is private and its `IframePreview` uses the app's virtual filesystem, Blob URLs, console bridge, and package-local infrastructure; it is not a distributable preview dependency. A public HTML preview can use an iframe owned by the public site with its own sandbox contract. The reviewed paths and dependencies are captured in [`source-viewer-module-boundary.txt`](evidence/phase2/source-viewer-module-boundary.txt).

## Legacy discovery queue

The queue mode exports only explicitly selected `CATEGORY/NAME` entries, retaining discovery metadata such as the URL and note while omitting historical popularity counts. The emitted input digest identifies the actual local YAML bytes. Legacy source labels and URLs remain leads; they do not establish authorship, a license, compatibility, or a successful installation.

## Evidence and review limits

`docs/evidence/phase2/source-opendesign.json` and `source-remotion.json` record selected paths, hashes, sizes, fingerprints, and catalog joins, not source bodies. Their repeat reports compare each fixed snapshot to itself and have zero changes. The reports show that the current catalog source paths exist in the selected snapshots; this is path and metadata evidence, not execution or visual-render validation. No source rights or compatibility fields are changed by this review.
