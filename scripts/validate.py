#!/usr/bin/env python3
"""Validate the draft v3 public catalog without mutating its source files."""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

try:
    import yaml
except ImportError:
    sys.exit("Missing dep: pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_REQUIRED = (
    "id", "title", "summary", "purpose", "classification", "provenance",
    "authors", "publisher", "license", "distribution", "previews",
    "compatibility", "components", "lifecycle", "review", "verification",
)
SOURCE_ROLES = {"content-upstream", "discovery-channel", "distribution-channel", "specification"}
RELATIONS = {"original", "adapted", "curated"}
LIFECYCLE = {"reference", "candidate", "usable", "withdrawn"}
REVIEW = {"pending", "approved", "rejected"}
VERIFICATION = {"unverified", "source-inspected", "usage-tested"}
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")


def _read(path, errors):
    try:
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{path}: cannot read YAML: {exc}")
        return None


def _ids(items, where, errors):
    result = {}
    if not isinstance(items, list):
        errors.append(f"{where}: expected a list")
        return result
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{where}[{i}]: expected a mapping")
            continue
        key = item.get("id")
        if not isinstance(key, str) or not IDENTIFIER.fullmatch(key):
            errors.append(f"{where}[{i}]: invalid id {key!r}")
            continue
        if key in result:
            errors.append(f"{where}[{i}]: duplicate id {key}")
        result[key] = item
    return result


def _usable_blockers(item):
    """Return the existing publication gates for a usable resource."""
    blockers = []
    review = item.get("review") or {}
    verification = item.get("verification") or {}
    license_data = item.get("license") or {}
    classification = item.get("classification") or {}
    provenance = item.get("provenance") or {}
    upstream = provenance.get("upstream") or {}
    ref = upstream.get("ref") or {}
    kind, ref_kind = upstream.get("kind"), ref.get("kind")
    locked = ref_kind in {"commit", "release", "content-hash", "immutable-entry"} and (kind != "git" or ref_kind == "commit")

    if review.get("status") != "approved" or not review.get("by") or not review.get("at") or not review.get("evidence"):
        blockers.append("review must be approved with reviewer, time and evidence")
    if verification.get("level") != "usage-tested" or not verification.get("checked_at") or not verification.get("by") or not verification.get("evidence"):
        blockers.append("verification must be usage-tested with date, tester and evidence")
    tested_hosts = verification.get("tested_hosts")
    if not isinstance(tested_hosts, list) or not tested_hosts:
        blockers.append("verification must list at least one tested_host")
    if license_data.get("status") != "verified" or license_data.get("redistribution") != "allowed":
        blockers.append("license and redistribution must be verified and allowed")
    if license_data.get("status") == "verified" and (
        not license_data.get("expression") or not license_data.get("evidence")
    ):
        blockers.append("verified license needs expression and evidence")
    if not locked:
        blockers.append("upstream ref must be immutable")
    hosts = (item.get("compatibility") or {}).get("hosts")
    if not isinstance(hosts, list) or not hosts:
        blockers.append("at least one host must be declared")
    if classification.get("category") == "design-systems" and not (
        {"design-md", "tokens"} <= set(classification.get("conventions") or [])
        and "css" in (classification.get("formats") or [])
    ):
        blockers.append("design system minimum profile needs design-md, tokens and css")
    if classification.get("category") == "templates":
        template = item.get("template") or {}
        files = template.get("files") or [] if isinstance(template, dict) else []
        roles = {entry.get("role") for entry in files if isinstance(entry, dict)}
        if not {"instructions", "framework", "example", "support"} <= roles:
            blockers.append("usable template needs instructions, framework, example and support files")
        style = template.get("style") or {} if isinstance(template, dict) else {}
        if not isinstance(style, dict) or style.get("upstream_status") != "independent":
            blockers.append("usable template requires an independent upstream style boundary")
    if classification.get("category") == "design-systems":
        design_system = item.get("design_system") or {}
        files = design_system.get("files", []) if isinstance(design_system, dict) else []
        roles = {entry.get("role") for entry in files if isinstance(entry, dict)}
        if not {"manifest", "rules", "tokens-css"} <= roles:
            blockers.append("usable design system needs manifest, rules and tokens-css files")
    return blockers


def _profile_file_errors(resource_id, profile_name, profile, allowed_roles, upstream):
    """Validate shared path/URL fields for one resource profile."""
    errors = []
    if not isinstance(profile, dict):
        return [f"resources.{resource_id}.{profile_name}: expected a mapping"]
    if profile_name == "design_system" and set(profile) != {"files"}:
        return [f"resources.{resource_id}.{profile_name}: expected only a files list"]
    files = profile.get("files")
    if not isinstance(files, list) or not files:
        return [f"resources.{resource_id}.{profile_name}.files: expected a non-empty list"]
    ref = (upstream.get("ref") or {}).get("value")
    is_git = upstream.get("kind") == "git"
    upstream_url = upstream.get("url") or ""
    upstream_parts = urlsplit(upstream_url)
    upstream_path = upstream_parts.path.rstrip("/")
    path_segments = [segment for segment in upstream_path.split("/") if segment]
    marker_index = next((i for i, segment in enumerate(path_segments) if segment in {"blob", "tree"}), None)
    if marker_index is not None and marker_index >= 2:
        repo_path = "/" + "/".join(path_segments[:marker_index])
    else:
        repo_path = upstream_path
    seen = set()
    for index, entry in enumerate(files):
        where = f"resources.{resource_id}.{profile_name}.files[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"role", "path", "url"}:
            errors.append(f"{where}: expected role, path and url")
            continue
        role, path, url = entry.get("role"), entry.get("path"), entry.get("url")
        if role not in allowed_roles:
            errors.append(f"{where}.role: invalid role {role!r}")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            errors.append(f"{where}.path: expected repository-relative path")
        elif (role, path) in seen:
            errors.append(f"{where}: duplicate role/path")
        else:
            seen.add((role, path))
        parsed = urlsplit(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{where}.url: expected a concrete HTTP(S) file reference")
        elif is_git:
            valid_ref = isinstance(ref, str) and bool(ref)
            expected_paths = {f"{repo_path}/{kind}/{ref}/{path}" for kind in ("blob", "tree")} if valid_ref else set()
            exact_unknown_locator = (
                not valid_ref
                and url == upstream_url
                and path == upstream.get("path")
            )
            if not exact_unknown_locator and (
                parsed.scheme != upstream_parts.scheme
                or parsed.netloc != upstream_parts.netloc
                or parsed.path not in expected_paths
                or parsed.query
                or parsed.fragment
            ):
                errors.append(f"{where}.url: git reference must use the upstream repository, locked ref and matching path")
    return errors


def _resource_profile_errors(resource_id, item, category, upstream):
    errors = []
    if "template" in item:
        if category != "templates":
            errors.append(f"resources.{resource_id}.template: only templates may declare this profile")
        profile = item["template"]
        if not isinstance(profile, dict) or set(profile) != {"files", "style"}:
            errors.append(f"resources.{resource_id}.template: expected only files and style")
        else:
            errors.extend(_profile_file_errors(resource_id, "template", profile, {"instructions", "framework", "example", "support"}, upstream))
            style = profile.get("style")
            if not isinstance(style, dict) or set(style) != {"policy", "upstream_status", "note"}:
                errors.append(f"resources.{resource_id}.template.style: expected policy, upstream_status and note")
            else:
                if style.get("policy") != "external-design-system":
                    errors.append(f"resources.{resource_id}.template.style.policy: must be external-design-system")
                if style.get("upstream_status") not in {"independent", "mixed", "unknown"}:
                    errors.append(f"resources.{resource_id}.template.style.upstream_status: invalid")
                if not isinstance(style.get("note"), str) or not style["note"].strip():
                    errors.append(f"resources.{resource_id}.template.style.note: explanation is required")
    if "design_system" in item:
        if category != "design-systems":
            errors.append(f"resources.{resource_id}.design_system: only design-systems may declare this profile")
        errors.extend(_profile_file_errors(resource_id, "design_system", item["design_system"], {"manifest", "rules", "tokens-css", "example", "support"}, upstream))
    return errors


def is_usable_for_host(resource, target_host):
    """Whether a validated public resource is usable on this specifically tested host."""
    if not isinstance(target_host, str) or not IDENTIFIER.fullmatch(target_host):
        return False
    if (resource.get("lifecycle") or {}).get("state") != "usable":
        return False
    if target_host not in ((resource.get("verification") or {}).get("tested_hosts") or []):
        return False
    return not _usable_blockers(resource)


def validate_data(categories_doc, sources_doc, resources_doc):
    """Return contract violations for the three v3 YAML documents."""
    errors = []
    if not isinstance(categories_doc, dict) or categories_doc.get("schema_version") != 3:
        errors.append("categories: schema_version must be 3")
    if not isinstance(sources_doc, dict) or sources_doc.get("schema_version") != 3:
        errors.append("sources: schema_version must be 3")
    if not isinstance(resources_doc, dict) or resources_doc.get("schema_version") != 3:
        errors.append("resources: schema_version must be 3")
    if errors:
        return errors

    category_list = categories_doc.get("categories")
    categories = _ids(category_list, "categories", errors)
    if len(categories) != 5:
        errors.append("categories: phase-1 taxonomy must define five primary categories")

    subtype_ids = {}
    for cid, cat in categories.items():
        subtype_ids[cid] = set(_ids(cat.get("subtypes", []), f"categories.{cid}.subtypes", errors))
    for cid, expected_count in (("templates", 7), ("prompts", 3)):
        if len(subtype_ids.get(cid, set())) != expected_count:
            errors.append(f"categories.{cid}: expected {expected_count} subtypes")
    for cid in ("design-systems", "skills", "plugins"):
        if subtype_ids.get(cid):
            errors.append(f"categories.{cid}: must not define subtypes")

    dimensions = categories_doc.get("dimensions") or {}
    dimensions_by_name = {}
    for name in ("domains", "formats", "conventions", "plugin_component_types"):
        dimensions_by_name[name] = _ids(dimensions.get(name, []), f"dimensions.{name}", errors)
    domain_ids = set(dimensions_by_name["domains"])
    format_ids = set(dimensions_by_name["formats"])
    convention_ids = set(dimensions_by_name["conventions"])
    component_types = set(dimensions_by_name["plugin_component_types"])

    source_map = _ids(sources_doc.get("sources"), "sources", errors)
    source_roles = {}
    tracking_fields = {"scope", "exclude", "baseline", "cadence", "method", "promotion", "last_checked", "limitations"}
    for sid, source in source_map.items():
        roles = source.get("roles")
        if not isinstance(roles, list) or not roles:
            errors.append(f"sources.{sid}: roles must be a non-empty list")
            roles = []
        invalid = set(roles) - SOURCE_ROLES
        if invalid:
            errors.append(f"sources.{sid}: unknown roles {sorted(invalid)}")
        source_roles[sid] = set(roles)
        access = source.get("access")
        source_url = source.get("url")
        if not source.get("name") or access not in {"public", "restricted", "unknown"}:
            errors.append(f"sources.{sid}: name and access (public/restricted/unknown) are required")
        if source_url is None:
            if access != "unknown":
                errors.append(f"sources.{sid}.url: null is allowed only when access is unknown")
        elif not isinstance(source_url, str) or urlsplit(source_url).scheme not in {"http", "https"} or not urlsplit(source_url).netloc:
            errors.append(f"sources.{sid}.url: expected a valid HTTP(S) URL or an explained unknown")
        tracking = source.get("tracking")
        if not isinstance(tracking, dict):
            errors.append(f"sources.{sid}: tracking must be a mapping")
        else:
            missing = tracking_fields - set(tracking)
            if missing:
                errors.append(f"sources.{sid}.tracking: missing {sorted(missing)}")
            if access == "unknown" and (not isinstance(tracking.get("limitations"), list) or not tracking["limitations"]):
                errors.append(f"sources.{sid}.tracking.limitations: unknown access needs an explanation")

    resources = resources_doc.get("resources")
    if not isinstance(resources, list):
        errors.append("resources: expected a list")
        resources = []
    meta = resources_doc.get("meta") or {}
    if not isinstance(meta, dict) or not meta.get("catalog_version") or not meta.get("updated"):
        errors.append("resources.meta: catalog_version and updated are required")
    elif not isinstance(meta.get("review"), dict) or meta["review"].get("status") not in REVIEW:
        errors.append("resources.meta.review.status: invalid or missing")
    resource_map = _ids(resources, "resources", errors)
    upstream_owners = {}

    for rid, item in resource_map.items():
        for field in RESOURCE_REQUIRED:
            if field not in item:
                errors.append(f"resources.{rid}: missing {field}")
        classification = item.get("classification") or {}
        cid = classification.get("category")
        subtype = classification.get("subtype")
        if cid not in categories:
            errors.append(f"resources.{rid}.classification.category: unknown category {cid!r}")
        elif subtype is not None and subtype not in subtype_ids.get(cid, set()):
            errors.append(f"resources.{rid}.classification.subtype: unknown subtype {subtype!r} for {cid}")
        elif cid in categories and subtype is None and subtype_ids.get(cid):
            errors.append(f"resources.{rid}.classification.subtype: category {cid} requires one subtype")
        for field, allowed in (("domains", domain_ids), ("formats", format_ids), ("conventions", convention_ids)):
            values = classification.get(field)
            if not isinstance(values, list):
                errors.append(f"resources.{rid}.classification.{field}: expected a list")
            else:
                for value in values:
                    if value not in allowed:
                        errors.append(f"resources.{rid}.classification.{field}: unknown value {value!r}")
        domains = classification.get("domains") or []
        if "general" in domains and len(domains) > 1:
            errors.append(f"resources.{rid}.classification.domains: general is exclusive with specific domains")

        provenance = item.get("provenance") or {}
        if provenance.get("relation") not in RELATIONS:
            errors.append(f"resources.{rid}.provenance.relation: invalid")
        content_source = provenance.get("content_source")
        if content_source not in source_map or "content-upstream" not in source_roles.get(content_source, set()):
            errors.append(f"resources.{rid}.provenance.content_source: must reference a content-upstream source")
        discovered = provenance.get("discovered_via")
        if not isinstance(discovered, list):
            errors.append(f"resources.{rid}.provenance.discovered_via: expected a list")
            discovered = []
        for sid in discovered:
            if sid not in source_map or "discovery-channel" not in source_roles.get(sid, set()):
                errors.append(f"resources.{rid}.provenance.discovered_via: {sid!r} must reference a discovery-channel source")
        upstream = provenance.get("upstream") or {}
        kind, url = upstream.get("kind"), upstream.get("url")
        path, selector = upstream.get("path"), upstream.get("selector")
        upstream_identity = (content_source, path or "", selector or "")
        if path or selector:
            if upstream_identity in upstream_owners:
                errors.append(f"resources.{rid}.provenance.upstream: duplicate distribution unit with {upstream_owners[upstream_identity]}")
            else:
                upstream_owners[upstream_identity] = rid
        ref = upstream.get("ref") or {}
        errors.extend(_resource_profile_errors(rid, item, cid, upstream))
        if kind not in {"git", "web", "product", "catalog"} or not url:
            errors.append(f"resources.{rid}.provenance.upstream: kind and concrete URL are required")
        if kind == "git":
            if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
                errors.append(f"resources.{rid}.provenance.upstream.path: git source needs a repository-relative path")
        elif kind in {"web", "product", "catalog"} and not selector:
            errors.append(f"resources.{rid}.provenance.upstream.selector: specific entry selector required")
        ref_kind, ref_value = ref.get("kind"), ref.get("value")
        if ref_kind not in {"commit", "release", "content-hash", "immutable-entry", "branch", "unknown"}:
            errors.append(f"resources.{rid}.provenance.upstream.ref: invalid kind")
        if ref_kind != "unknown" and not ref_value:
            errors.append(f"resources.{rid}.provenance.upstream.ref: known ref kind needs value")
        if ref_kind == "unknown" and ref_value is not None:
            errors.append(f"resources.{rid}.provenance.upstream.ref: unknown ref value must be null")
        if ref_kind == "commit" and (not isinstance(ref_value, str) or not SHA1.fullmatch(ref_value)):
            errors.append(f"resources.{rid}.provenance.upstream.ref: commit must be a full 40-character SHA")
        locked = ref_kind in {"commit", "release", "content-hash", "immutable-entry"} and (kind != "git" or ref_kind == "commit")

        if provenance.get("relation") == "adapted" and (not provenance.get("derives_from") or not provenance.get("changes")):
            errors.append(f"resources.{rid}.provenance: adapted resources need derives_from and changes")
        if provenance.get("relation") == "curated" and provenance.get("derives_from"):
            errors.append(f"resources.{rid}.provenance: curated resource must not declare derives_from")

        for identity_field in ("authors", "publisher"):
            identity = item.get(identity_field) or {}
            identity_status = identity.get("status")
            identities = identity.get("identities")
            evidence = identity.get("evidence")
            if identity_status not in {"known", "unknown"} or not isinstance(identities, list) or not isinstance(evidence, list):
                errors.append(f"resources.{rid}.{identity_field}: status, identities and evidence are required")
            elif identity_status == "known" and (not identities or not evidence):
                errors.append(f"resources.{rid}.{identity_field}: known identity needs identities and evidence")
            elif identity_status == "unknown" and identities:
                errors.append(f"resources.{rid}.{identity_field}: unknown identity cannot include identities")

        license_data = item.get("license") or {}
        license_status = license_data.get("status")
        if license_status not in {"verified", "unknown"}:
            errors.append(f"resources.{rid}.license.status: invalid")
        redistribution = license_data.get("redistribution")
        if redistribution not in {"allowed", "blocked", "unknown"}:
            errors.append(f"resources.{rid}.license.redistribution: invalid")
        if license_status == "verified" and (not license_data.get("expression") or not license_data.get("evidence")):
            errors.append(f"resources.{rid}.license: verified license needs expression and evidence")

        for channel in item.get("distribution") or []:
            sid = channel.get("channel_source")
            if sid is not None and (sid not in source_map or "distribution-channel" not in source_roles.get(sid, set())):
                errors.append(f"resources.{rid}.distribution.channel_source: must reference a distribution-channel source")
        compatibility = item.get("compatibility") or {}
        for dependency in compatibility.get("dependencies") or []:
            sid = dependency.get("source_id")
            if sid is not None and sid not in source_map:
                errors.append(f"resources.{rid}.compatibility.dependencies: unknown source_id {sid!r}")

        components = item.get("components")
        if not isinstance(components, list):
            errors.append(f"resources.{rid}.components: expected a list")
            components = []
        if cid == "plugins" and not components:
            errors.append(f"resources.{rid}.components: plugins need at least one component")
        if cid != "plugins" and components:
            errors.append(f"resources.{rid}.components: only plugins may contain components")
        component_ids = set()
        for component in components:
            component_id = component.get("id")
            if not isinstance(component_id, str) or not IDENTIFIER.fullmatch(component_id):
                errors.append(f"resources.{rid}.components: invalid component id {component_id!r}")
            elif component_id in component_ids:
                errors.append(f"resources.{rid}.components: duplicate component id {component_id}")
            else:
                component_ids.add(component_id)
            if component.get("type") not in component_types:
                errors.append(f"resources.{rid}.components: unknown component type {component.get('type')!r}")
            component_resource = component.get("resource_id")
            if component_resource is not None and component_resource not in resource_map:
                errors.append(f"resources.{rid}.components: unknown resource_id {component_resource!r}")
            component_upstream = component.get("upstream") or {}
            if not component_upstream.get("url") or not component_upstream.get("ref") or not component_upstream.get("path"):
                errors.append(f"resources.{rid}.components: each component needs a concrete upstream path and ref")
            if component.get("delivery") not in {"contained", "referenced", "host-provided"}:
                errors.append(f"resources.{rid}.components: invalid or missing delivery")

        lifecycle = item.get("lifecycle") or {}
        state = lifecycle.get("state")
        if state not in LIFECYCLE:
            errors.append(f"resources.{rid}.lifecycle.state: invalid")
        review = item.get("review") or {}
        if review.get("status") not in REVIEW:
            errors.append(f"resources.{rid}.review.status: invalid")
        verification = item.get("verification") or {}
        level = verification.get("level")
        if level not in VERIFICATION:
            errors.append(f"resources.{rid}.verification.level: invalid")
        tested_hosts = verification.get("tested_hosts")
        if not isinstance(tested_hosts, list):
            errors.append(f"resources.{rid}.verification.tested_hosts: expected a list")
            tested_hosts = []
        seen_tested_hosts = set()
        for tested_host in tested_hosts:
            if not isinstance(tested_host, str) or not IDENTIFIER.fullmatch(tested_host):
                errors.append(f"resources.{rid}.verification.tested_hosts: invalid stable ASCII host id {tested_host!r}")
            elif tested_host in seen_tested_hosts:
                errors.append(f"resources.{rid}.verification.tested_hosts: duplicate host id {tested_host}")
            else:
                seen_tested_hosts.add(tested_host)
        if level == "usage-tested" and not tested_hosts:
            errors.append(f"resources.{rid}.verification.tested_hosts: usage-tested requires at least one tested host")
        if level != "usage-tested" and tested_hosts:
            errors.append(f"resources.{rid}.verification.tested_hosts: only usage-tested resources may list tested hosts")
        if state == "usable":
            blockers = _usable_blockers(item)
            if blockers:
                errors.append(f"resources.{rid}: usable is blocked: {'; '.join(blockers)}")

    return errors


def validate_catalog(root=ROOT):
    root = Path(root)
    errors = []
    docs = [_read(root / "data" / f"{name}.yaml", errors) for name in ("categories", "sources", "resources")]
    if errors:
        return errors
    return validate_data(*docs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT, help="catalog root (defaults to this repository)")
    args = parser.parse_args()
    errors = validate_catalog(args.root)
    if errors:
        print(f"FAIL: {len(errors)} v3 catalog violation(s)")
        for error in errors[:100]:
            print(" -", error)
        return 1
    print("PASS: schema_version=3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
