#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

EXPECTED_SPECS = {
    "approvals.yaml", "canonical-execution-graph.yaml", "context.yaml", "control-plane.yaml",
    "core.yaml", "evidence.yaml", "execution.yaml", "mission-control.yaml", "observability.yaml",
    "persistence.yaml", "routing.yaml", "verification.yaml",
}
EXPECTED_SCHEMAS = {
    "approval.schema.json", "canonical-execution-graph.schema.json", "evidence.schema.json",
    "execution-envelope.schema.json", "handoff.schema.json", "output.schema.json",
    "routing-decision.schema.json", "classification-standard.schema.json",
    "classification-entry.schema.json", "classification-crosswalk.schema.json",
    "classification-catalogue.schema.json", "classification-indicator.schema.json",
}
EXPECTED_REGISTRIES = {"capabilities.yaml", "providers.yaml", "surfaces.yaml"}
EXPECTED_CLASSIFICATION_REGISTRIES = {
    "families.yaml", "authorities.yaml", "standards.yaml", "update-sources.yaml", "crosswalks.yaml",
}
EXPECTED_CLASSIFICATION_CATALOGUES = {
    "economic-activity.yaml", "industry.yaml", "product.yaml", "sector.yaml", "domain.yaml",
    "capability.yaml", "technology.yaml",
}
EXPECTED_INTEGRATIONS = {
    "access-asia.yaml", "argus.yaml", "chatgpt-bootstrap.yaml", "chatgpt.yaml",
    "generic-host.yaml", "hermes-agent.yaml",
}
EXPECTED_DOCS = {
    "README.md", "SUMMARY.md", "architecture.md", "framework.md", "playbook.md", "sop.md",
    "capabilities-routing.md", "evidence-verification.md", "classification-standards.md",
    "canonical-execution-graph.md", "argus-interface.md", "host-integration.md",
    "implementation-guide.md", "examples.md",
}
BANNED = {"legacy", "migration", "library", "docs/releases", "docs/plans"}
APPROVED_FAMILIES = {
    "DOMAIN", "SECTOR", "INDUSTRY", "ECONOMIC_ACTIVITY", "PRODUCT", "CAPABILITY", "TECHNOLOGY",
    "PROCUREMENT_CATEGORY", "TRADE_CLASSIFICATION", "OCCUPATION", "GEOGRAPHY",
    "COMPLIANCE_REGULATORY",
}
LIFECYCLES = {"DISCOVERED", "CANDIDATE", "VERIFIED", "ACTIVE", "SUPERSEDED", "ARCHIVED"}
EVIDENCE_STATUSES = {"CONFIRMED", "PROBABLE", "POSSIBLE", "DISPUTED", "UNVERIFIED", "STALE"}
RELATIONSHIPS = {"EXACT", "CLOSE", "BROADER", "NARROWER", "RELATED", "CANDIDATE"}
REDISTRIBUTION_STATUSES = {"PERMITTED", "RESTRICTED", "UNKNOWN", "NOT_APPLICABLE"}
DATASET_STORAGE_MODES = {"NONE", "METADATA_ONLY", "PERMITTED_EXTRACT", "FULL_DATASET"}
CLASSIFICATION_STATUSES = {"DRAFT", "ADOPTED", "OPERATIONAL", "RETIRED"}
PUBLICATION_STATUSES = {"PUBLISHED", "FORTHCOMING", "NOT_APPLICABLE", "UNKNOWN"}
SOURCE_MODES = {"ATLAS_OWNED", "REMOTE_AUTHORITATIVE", "METADATA_ONLY"}


def _load(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _names(root: Path, directory: str, suffixes: tuple[str, ...]) -> set[str]:
    base = root / directory
    if not base.is_dir():
        return set()
    return {path.name for path in base.iterdir() if path.is_file() and path.suffix in suffixes}


def _validate_catalogues(
    base: Path,
    family_ids: set[str],
    authority_set: set[str],
    standard_id_set: set[str],
    versions: dict[str, dict],
    version_owner: dict[str, str],
    errors: list[str],
) -> None:
    catalogue_dir = base / "catalogues"
    actual = _names(base.parent.parent, "registries/classification/catalogues", (".yaml",))
    if actual != EXPECTED_CLASSIFICATION_CATALOGUES:
        errors.append(
            "registries/classification/catalogues surface drift: "
            f"{sorted(actual)} != {sorted(EXPECTED_CLASSIFICATION_CATALOGUES)}"
        )
        return

    catalogue_ids: set[str] = set()
    for filename in sorted(EXPECTED_CLASSIFICATION_CATALOGUES):
        path = catalogue_dir / filename
        payload = _load(path)
        catalogue_id = payload.get("catalogue_id")
        if not catalogue_id or catalogue_id in catalogue_ids:
            errors.append(f"duplicate or missing classification catalogue ID: {catalogue_id}")
            continue
        catalogue_ids.add(catalogue_id)

        family_id = payload.get("family_id")
        if family_id not in family_ids:
            errors.append(f"unknown classification catalogue family: {catalogue_id}")
        authority_id = payload.get("authority_id")
        if authority_id not in authority_set:
            errors.append(f"unknown classification catalogue authority: {catalogue_id}")
        if not str(payload.get("owner", "")).strip():
            errors.append(f"classification catalogue owner is required: {catalogue_id}")
        if payload.get("source_mode") not in SOURCE_MODES:
            errors.append(f"invalid classification catalogue source mode: {catalogue_id}")
        if payload.get("lifecycle") not in LIFECYCLES:
            errors.append(f"invalid classification catalogue lifecycle: {catalogue_id}")
        if payload.get("redistribution_status") not in REDISTRIBUTION_STATUSES:
            errors.append(f"invalid classification catalogue redistribution status: {catalogue_id}")
        if payload.get("dataset_storage") not in DATASET_STORAGE_MODES:
            errors.append(f"invalid classification catalogue storage mode: {catalogue_id}")
        if payload.get("dataset_storage") == "FULL_DATASET" and payload.get("redistribution_status") != "PERMITTED":
            errors.append(f"classification catalogue FULL_DATASET requires PERMITTED redistribution: {catalogue_id}")
        source_standard = payload.get("source_standard_id")
        source_version = payload.get("source_version_id")
        if source_standard not in standard_id_set:
            errors.append(f"classification catalogue references unknown source standard: {catalogue_id}")
        if source_version not in versions:
            errors.append(f"classification catalogue references unknown source version: {catalogue_id}")
        elif version_owner[source_version] != source_standard:
            errors.append(f"classification catalogue source version does not belong to source standard: {catalogue_id}")
        if not str(payload.get("source_url", "")).startswith("https://"):
            errors.append(f"classification catalogue lacks provenance URL: {catalogue_id}")
        if payload.get("source_mode") == "ATLAS_OWNED":
            if payload.get("owner") != "ATLAS" or authority_id != "ATLAS":
                errors.append(f"ATLAS-owned catalogue must use ATLAS authority: {catalogue_id}")
            if payload.get("redistribution_status") != "PERMITTED":
                errors.append(f"ATLAS-owned catalogue must be redistributable: {catalogue_id}")

        items = payload.get("items", [])
        item_ids = [item.get("atlas_classification_id") for item in items]
        seen: set[str] = set()
        for item_id in item_ids:
            if not item_id or item_id in seen:
                errors.append(f"duplicate classification item ID in {catalogue_id}: {item_id}")
            if item_id:
                seen.add(item_id)
        item_by_id = {item.get("atlas_classification_id"): item for item in items if item.get("atlas_classification_id")}
        for item_id, item in item_by_id.items():
            if item.get("family_id") != family_id:
                errors.append(f"classification item family mismatch in {catalogue_id}: {item_id}")
            item_standard = item.get("source_standard_id")
            item_version = item.get("source_version_id")
            if item_standard not in standard_id_set:
                errors.append(f"classification item references unknown source standard in {catalogue_id}: {item_id}")
            if item_version not in versions:
                errors.append(f"classification item references unknown source version in {catalogue_id}: {item_id}")
            elif version_owner[item_version] != item_standard:
                errors.append(f"classification item source version mismatch in {catalogue_id}: {item_id}")
            item_authority = item.get("authority_id")
            if item_authority is not None and item_authority not in authority_set:
                errors.append(f"classification item references unknown authority in {catalogue_id}: {item_id}")
            parent_id = item.get("parent_id")
            if parent_id is not None and parent_id not in item_by_id:
                errors.append(f"unknown classification parent in {catalogue_id}: {parent_id}")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(item_id: str) -> None:
            if item_id in visited:
                return
            if item_id in visiting:
                errors.append(f"classification parent cycle in {catalogue_id}: {item_id}")
                return
            visiting.add(item_id)
            parent_id = item_by_id[item_id].get("parent_id")
            if parent_id in item_by_id:
                visit(parent_id)
            visiting.remove(item_id)
            visited.add(item_id)

        for item_id in item_by_id:
            visit(item_id)


def _validate_classification(root: Path, errors: list[str]) -> None:
    base = root / "registries" / "classification"
    families = _load(base / "families.yaml").get("families", [])
    family_ids = [entry.get("id") for entry in families]
    family_set = set(family_ids)
    if family_set != APPROVED_FAMILIES or len(family_ids) != len(family_set):
        errors.append("classification families must exactly match the approved unique family set")

    authorities = _load(base / "authorities.yaml").get("authorities", [])
    authority_ids = [entry.get("id") for entry in authorities]
    authority_set = set(authority_ids)
    if len(authority_ids) != len(authority_set):
        errors.append("classification authority IDs must be unique")
    for authority in authorities:
        if not authority.get("official_name") or not str(authority.get("source_url", "")).startswith("https://"):
            errors.append(f"invalid classification authority: {authority.get('id')}")

    standards_payload = _load(base / "standards.yaml")
    if standards_payload.get("rules", {}).get("historical_versions_preserved") is not True:
        errors.append("classification standards must preserve historical versions")
    standards = standards_payload.get("standards", [])
    standard_ids = [record.get("standard_id") for record in standards]
    standard_id_set = set(standard_ids)
    if len(standard_ids) != len(standard_id_set):
        errors.append("classification standard IDs must be unique")

    versions: dict[str, dict] = {}
    version_owner: dict[str, str] = {}
    for standard in standards:
        standard_id = standard.get("standard_id")
        if standard.get("family_id") not in APPROVED_FAMILIES:
            errors.append(f"unknown classification family on {standard_id}")
        if standard.get("authority_id") not in authority_set:
            errors.append(f"unknown classification authority on {standard_id}")
        if not standard.get("official_name") or not standard.get("abbreviation") or not standard.get("jurisdiction"):
            errors.append(f"incomplete classification standard metadata: {standard_id}")
        for version in standard.get("versions", []):
            version_id = version.get("version_id")
            if not version_id or version_id in versions:
                errors.append(f"duplicate or missing classification version ID: {version_id}")
                continue
            versions[version_id] = version
            version_owner[version_id] = standard_id
            official_version = version.get("official_version")
            if not isinstance(official_version, str) or not official_version.strip():
                errors.append(f"classification official version must be a non-empty string: {version_id}")
            if version.get("lifecycle") not in LIFECYCLES:
                errors.append(f"invalid classification lifecycle: {version_id}")
            if version.get("evidence_status") not in EVIDENCE_STATUSES:
                errors.append(f"invalid classification evidence status: {version_id}")
            if not str(version.get("source_url", "")).startswith("https://"):
                errors.append(f"classification version lacks authoritative provenance URL: {version_id}")
            if version.get("redistribution_status") not in REDISTRIBUTION_STATUSES:
                errors.append(f"invalid redistribution status: {version_id}")
            if version.get("dataset_storage") not in DATASET_STORAGE_MODES:
                errors.append(f"invalid dataset storage mode: {version_id}")
            classification_status = version.get("classification_status")
            if classification_status is not None and classification_status not in CLASSIFICATION_STATUSES:
                errors.append(f"invalid classification status: {version_id}")
            publication_status = version.get("publication_status")
            if publication_status is not None and publication_status not in PUBLICATION_STATUSES:
                errors.append(f"invalid publication status: {version_id}")
            if version.get("lifecycle") == "ACTIVE" and version.get("evidence_status") != "CONFIRMED":
                errors.append(f"ACTIVE classification version must be CONFIRMED: {version_id}")
            if version.get("dataset_storage") == "FULL_DATASET" and version.get("redistribution_status") != "PERMITTED":
                errors.append(f"FULL_DATASET requires PERMITTED redistribution: {version_id}")

    for version_id, version in versions.items():
        supersedes = version.get("supersedes_version_id")
        if supersedes:
            if supersedes not in versions:
                errors.append(f"classification supersedes unknown version: {version_id} -> {supersedes}")
            elif supersedes == version_id:
                errors.append(f"classification version cannot supersede itself: {version_id}")
            elif version_owner[supersedes] != version_owner[version_id]:
                errors.append(f"classification version supersedes a different standard: {version_id} -> {supersedes}")

    sources = _load(base / "update-sources.yaml").get("update_sources", [])
    source_ids = [source.get("id") for source in sources]
    if len(source_ids) != len(set(source_ids)):
        errors.append("classification update-source IDs must be unique")
    for source in sources:
        if source.get("authority_id") not in authority_set:
            errors.append(f"classification update source has unknown authority: {source.get('id')}")
        if source.get("source_class") != "AUTHORITATIVE" or not str(source.get("url", "")).startswith("https://"):
            errors.append(f"classification update source must be authoritative: {source.get('id')}")

    crosswalk_payload = _load(base / "crosswalks.yaml")
    if crosswalk_payload.get("directional") is not True:
        errors.append("classification crosswalks must be directional")
    if crosswalk_payload.get("candidate_is_not_canonical_equivalence") is not True:
        errors.append("CANDIDATE crosswalks must not be canonical equivalence")
    crosswalk_ids: set[str] = set()
    for crosswalk in crosswalk_payload.get("crosswalks", []):
        crosswalk_id = crosswalk.get("crosswalk_id")
        if not crosswalk_id or crosswalk_id in crosswalk_ids:
            errors.append(f"duplicate or missing crosswalk ID: {crosswalk_id}")
        crosswalk_ids.add(crosswalk_id)
        if crosswalk.get("relationship") not in RELATIONSHIPS:
            errors.append(f"invalid crosswalk relationship: {crosswalk_id}")
        if crosswalk.get("evidence_status") not in EVIDENCE_STATUSES:
            errors.append(f"invalid crosswalk evidence status: {crosswalk_id}")
        if not str(crosswalk.get("source_url", "")).startswith("https://"):
            errors.append(f"crosswalk lacks provenance URL: {crosswalk_id}")
        source_standard = crosswalk.get("source_standard_id")
        target_standard = crosswalk.get("target_standard_id")
        source_version = crosswalk.get("source_version_id")
        target_version = crosswalk.get("target_version_id")
        if source_standard not in standard_id_set:
            errors.append(f"crosswalk references unknown source standard: {crosswalk_id}")
        if target_standard not in standard_id_set:
            errors.append(f"crosswalk references unknown target standard: {crosswalk_id}")
        if source_version not in versions or target_version not in versions:
            errors.append(f"crosswalk references unknown version: {crosswalk_id}")
        else:
            if version_owner[source_version] != source_standard:
                errors.append(f"crosswalk source version does not belong to source standard: {crosswalk_id}")
            if version_owner[target_version] != target_standard:
                errors.append(f"crosswalk target version does not belong to target standard: {crosswalk_id}")
        if crosswalk.get("relationship") == "CANDIDATE" and crosswalk.get("evidence_status") == "CONFIRMED":
            errors.append(f"CANDIDATE crosswalk cannot be treated as confirmed equivalence: {crosswalk_id}")

    _validate_catalogues(base, family_set, authority_set, standard_id_set, versions, version_owner, errors)


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    expected_sets = (
        ("spec", EXPECTED_SPECS, (".yaml",)),
        ("schemas", EXPECTED_SCHEMAS, (".json",)),
        ("registries", EXPECTED_REGISTRIES, (".yaml",)),
        ("integrations", EXPECTED_INTEGRATIONS, (".yaml",)),
        ("docs", EXPECTED_DOCS, (".md",)),
    )
    for directory, expected, suffixes in expected_sets:
        actual = _names(root, directory, suffixes)
        if actual != expected:
            errors.append(f"{directory} surface drift: {sorted(actual)} != {sorted(expected)}")

    classification_actual = _names(root, "registries/classification", (".yaml",))
    if classification_actual != EXPECTED_CLASSIFICATION_REGISTRIES:
        errors.append(
            "registries/classification surface drift: "
            f"{sorted(classification_actual)} != {sorted(EXPECTED_CLASSIFICATION_REGISTRIES)}"
        )

    for relative in BANNED:
        if (root / relative).exists():
            errors.append(f"banned active content exists: {relative}")

    _validate_classification(root, errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ATLAS repository contracts.")
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    args = parser.parse_args()
    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("ATLAS repository contracts valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
