#!/usr/bin/env python3
"""Build public catalog views from the three validated v3 source files."""
import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def build_outputs(root=ROOT):
    root = Path(root)
    # Validate before constructing or writing any generated output.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from validate import is_usable_for_host, validate_catalog

    errors = validate_catalog(root)
    if errors:
        raise ValueError("\n".join(errors))

    categories_doc = yaml.safe_load((root / "data" / "categories.yaml").read_text(encoding="utf-8"))
    sources_doc = yaml.safe_load((root / "data" / "sources.yaml").read_text(encoding="utf-8"))
    resources_doc = yaml.safe_load((root / "data" / "resources.yaml").read_text(encoding="utf-8"))
    categories = categories_doc["categories"]
    resources = resources_doc["resources"]
    meta = resources_doc["meta"]

    # Discovery remains a separate, unverified contract. It is browsable without
    # asserting that a directory link is the actual content upstream.
    discovery = None
    discovery_path = root / "data" / "discovery" / "legacy-v2.yaml"
    if discovery_path.exists():
        from discovery_index.core import build_index
        discovery = build_index(discovery_path, root / "data" / "resources.yaml",
                                root / "data" / "discovery" / "classification-overrides.yaml")
        supplemental_path = root / "data" / "discovery" / "opendesign-references.yaml"
        if supplemental_path.exists():
            supplemental = yaml.safe_load(supplemental_path.read_text(encoding="utf-8"))
            discovery["entries"].extend(supplemental["entries"])
            discovery["additional_sources"] = [{"source_id": supplemental["source_id"],
                                                "ref": supplemental["ref"],
                                                "entries": len(supplemental["entries"])}]

    catalog = {
        "schema_version": 3,
        "categories": categories_doc,
        "sources": sources_doc,
        "resources": resources_doc,
        # Public display projection shares the canonical admission rule; it is
        # not an installation kernel or a mutation of the source records.
        "availability": {
            resource["id"]: [host for host in resource["verification"]["tested_hosts"]
                             if is_usable_for_host(resource, host)]
            for resource in resources
        },
    }
    if discovery is not None:
        catalog["discovery"] = discovery
    site_data = {
        "meta": {
            "updated": str(meta["updated"]),
            "catalogVersion": meta["catalog_version"],
            "review": meta["review"],
        },
        "categories": [],
    }
    for category in categories:
        entries = []
        for resource in resources:
            classification = resource["classification"]
            if classification["category"] != category["id"]:
                continue
            provenance = resource["provenance"]
            upstream = provenance["upstream"]
            entries.append({
                "id": resource["id"],
                "name": resource["title"],
                "url": upstream["url"],
                "source": provenance["relation"],
                "relation": provenance["relation"],
                "platform": ", ".join(channel.get("kind", "") for channel in resource["distribution"]),
                "subcat": classification["subtype"] or "",
                "note": resource["summary"],
                "stars": None,
                "installs": None,
                "verified": resource["verification"].get("checked_at") or "",
                "vmethod": "",
                "purpose": resource["purpose"],
                "classification": classification,
                "provenance": provenance,
                "license": resource["license"],
                "distribution": resource["distribution"],
                "previews": resource["previews"],
                "compatibility": resource["compatibility"],
                "components": resource["components"],
                "lifecycle": resource["lifecycle"],
                "review": resource["review"],
                "verification": resource["verification"],
                "tested_hosts": resource["verification"]["tested_hosts"],
                "usable_for_hosts": [
                    host for host in resource["verification"]["tested_hosts"]
                    if is_usable_for_host(resource, host)
                ],
                "authors": resource["authors"],
                "publisher": resource["publisher"],
                **({"template": resource["template"]} if "template" in resource else {}),
                **({"design_system": resource["design_system"]} if "design_system" in resource else {}),
            })
        site_data["categories"].append({
            "id": category["id"],
            "name": category["label"],
            "desc": category["definition"],
            "entries": entries,
        })

    if discovery is not None:
        site_data["discovery"] = discovery

    js = "// GENERATED by scripts/build.py from schema v3 sources — do not edit by hand\n"
    js += "const DATA = " + json.dumps(site_data, ensure_ascii=False, indent=2) + ";\n"
    catalog_json = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"

    lines = [
        "# Awesome Agent Ecosystem [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "<!-- GENERATED by scripts/build.py from data/categories.yaml, data/sources.yaml and data/resources.yaml -->",
        "",
        f"> Public asset catalog `{meta['catalog_version']}` · contract review: **{meta['review']['status']}** · updated {meta['updated']}.",
        "> Contract approval does not approve individual resources or runtime compatibility. Publication and installation are separate steps.",
        "",
        "## Run the public store",
        "",
        "Requires Node.js 22.12+ and Python 3.9+. No private ThusDesign code or production credentials are needed.",
        "",
        "```bash",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install -r requirements.txt",
        "npm ci",
        "npm run generate",
        "python -m unittest discover -s tests -v",
        "npm test",
        "npm run typecheck",
        "npm run build",
        "npm run check:host",
        "npm run start -- --port 3001",
        "```",
        "",
        "Open http://localhost:3001. Development uses `npm run dev -- --port 3001`.",
        "Use an available port among 3000/3001; the server fails rather than silently switching ports.",
        "",
        "The store shares its public UI and catalog logic with a minimal host example. Account integration and migration of the existing ThusDesign stores are Phase 2+ work.",
        "See [host integration](docs/host-integration.md), [source tools](docs/source-tools.md), [maintenance](MAINTENANCE.md), and [contribution guidelines](CONTRIBUTING.md).",
        "Generated outputs read the resource source files and the public discovery queue. Discovery visibility does not grant resource approval, usage verification or publication.",
        "",
        "## Categories",
        "",
    ]
    for category in categories:
        lines.append(f"- [{category['label']}](#{category['id']})")
    lines += ["", "## Resources", ""]
    for category in categories:
        items = [r for r in resources if r["classification"]["category"] == category["id"]]
        lines += [f'<a id="{category["id"]}"></a>', f"### {category['label']}", "", f"> {category['definition']}", ""]
        if category["id"] == "templates":
            lines += ["Templates are reusable content and code frameworks. Their examples are references; visual style is supplied by an independent design system.", ""]
        elif category["id"] == "design-systems":
            lines += ["Design-system profiles link the actual manifest, design rules and token CSS files when available; optional references may be incomplete.", ""]
        if not items:
            lines += ["No resources yet.", ""]
            continue
        lines += ["| Resource | Subtype | Relation | Lifecycle | Verification | 可使用宿主 | License |", "|---|---|---|---|---|---|---|"]
        for resource in items:
            classification = resource["classification"]
            subtype = classification.get("subtype") or "—"
            life = resource["lifecycle"]["state"]
            verification = resource["verification"]["level"]
            license_status = resource["license"]["status"]
            usable_hosts = [
                host for host in resource["verification"]["tested_hosts"]
                if is_usable_for_host(resource, host)
            ]
            url = resource["provenance"]["upstream"]["url"]
            lines.append(f"| [{resource['title']}]({url}) (`{resource['id']}`) | {subtype} | {resource['provenance']['relation']} | {life} | {verification} | {', '.join(usable_hosts) or '—'} | {license_status} |")
        lines.append("")
        if category["id"] == "plugins":
            for resource in items:
                if not resource["components"]:
                    continue
                lines += ["", f"**Components in {resource['title']}**", "",
                          "| Component ID | Type | Delivery | Resource reference |", "|---|---|---|---|"]
                for component in resource["components"]:
                    resource_ref = component.get("resource_id") or "—"
                    lines.append(f"| `{component['id']}` | `{component['type']}` | `{component['delivery']}` | `{resource_ref}` |")
                lines.append("")
    if discovery is not None:
        entries = discovery["entries"]
        visible = [entry for entry in entries if not entry.get("mapped_resource_id")]
        lines += ["## Discovery entries", "",
                  "The store also browses the complete historical discovery queue. These are unverified leads, collections or reference entries; they are not approved installation records.", "",
                  f"{len(entries)} indexed discovery entries ({discovery['coverage']['total_assets']} historical asset leads), {len(visible)} additional browser entries after existing-resource matches; {len(discovery['platforms'])} platforms are listed as discovery channels.", ""]
        for category in categories:
            group = [entry for entry in visible if entry["classification"]["category"] == category["id"]]
            if not group:
                continue
            lines += [f"### Discovery · {category['label']}", "",
                      "| Entry | Content kind | Discovery URL | Review |", "|---|---|---|---|"]
            for entry in group:
                title = entry["title"].replace("|", "\|")
                lines.append(f"| {title} (`{entry['id']}`) | {entry['content_kind']} | [Original listing]({entry['source_url']}) | Unverified |")
            lines.append("")
        lines += ["### Discovery platforms", "", "| Platform | Source |", "|---|---|"]
        for platform in discovery["platforms"]:
            name = platform["name"].replace("|", "\|")
            lines.append(f"| {name} | [Discovery channel]({platform['url']}) |")
        lines.append("")
    lines += ["## Sources", "", "Source roles and update scopes are recorded in `data/sources.yaml`.", ""]

    outputs = {
        root / "README.md": "\n".join(lines),
        root / "site" / "data.js": js,
        root / "site" / "catalog.json": catalog_json,
    }
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return len(resources)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="catalog root (defaults to this repository)")
    args = parser.parse_args()
    try:
        count = build_outputs(args.root)
    except ValueError as exc:
        print(f"FAIL: catalog validation failed\n{exc}", file=sys.stderr)
        return 1
    print(f"OK  README.md, site/data.js and site/catalog.json ({count} resources)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
