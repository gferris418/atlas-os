#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

EXPECTED_SPECS = {
    "approvals.yaml", "chat-event-persistence.yaml", "context.yaml", "control-plane.yaml", "core.yaml", "evidence.yaml",
    "execution.yaml", "mission-control.yaml", "observability.yaml", "performance-telemetry.yaml", "persistence.yaml",
    "quality-governance.yaml", "routing.yaml", "verification.yaml",
}
EXPECTED_SCHEMAS = {
    "approval.schema.json", "evidence.schema.json", "execution-envelope.schema.json",
    "handoff.schema.json", "output.schema.json", "routing-decision.schema.json",
    "classification-standard.schema.json", "classification-entry.schema.json",
    "classification-crosswalk.schema.json",
}
EXPECTED_REGISTRIES = {"capabilities.yaml", "providers.yaml", "surfaces.yaml"}
EXPECTED_CLASSIFICATION_REGISTRIES = {
    "families.yaml", "authorities.yaml", "standards.yaml", "update-sources.yaml", "crosswalks.yaml",
}
EXPECTED_INTEGRATIONS = {
    "access-asia.yaml", "argus.yaml", "chatgpt-bootstrap.yaml", "chatgpt.yaml",
    "generic-host.yaml", "hermes-agent.yaml",
}
EXPECTED_DOCS = {
    "README.md", "SUMMARY.md", "architecture.md", "framework.md", "playbook.md", "sop.md",
    "capabilities-routing.md", "evidence-verification.md", "classification-standards.md",
    "argus-interface.md", "host-integration.md", "implementation-guide.md", "examples.md",
}
BANNED = {"legacy", "migration", "library", "docs/releases", "docs/plans"}
APPROVED_FAMILIES = {
    "DOMAIN", "SECTOR", "INDUSTRY", "ECONOMIC_ACTIVITY", "PRODUCT", "CAPABILITY",
    "PROCUREMENT_CATEGORY", "TRADE_CLASSIFICATION", "OCCUPATION", "GEOGRAPHY",
    "COMPLIANCE_REGULATORY",
}
LIFECYCLES = {"DISCOVERED", "CANDIDATE", "VERIFIED", "ACTIVE", "SUPERSEDED", "ARCHIVED"}
EVIDENCE_STATUSES = {"CONFIRMED", "PROBABLE", "POSSIBLE", "DISPUTED", "UNVERIFIED", "STALE"}
RELATIONSHIPS = {"EXACT", "CLOSE", "BROADER", "NARROWER", "RELATED", "CANDIDATE"}
REDISTRIBUTION_STATUSES = {"PERMITTED", "RESTRICTED", "UNKNOWN", "NOT_APPLICABLE"}
DATASET_STORAGE_MODES = {"NONE", "METADATA_ONLY", "PERMITTED_EXTRACT", "FULL_DATASET"}


def _load(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _names(root: Path, directory: str, suffixes: tuple[str, ...]) -> set[str]:
    base = root / directory
    if not base.is_dir():
        return set()
    return {path.name for path in base.iterdir() if path.is_file() and path.suffix in suffixes}


def _validate_classification(root: Path, errors: list[str]) -> None:
    base = root / "registries" / "classification"
    families = _load(base / "families.yaml").get("families", [])
    family_ids = [entry.get("id") for entry in families]
    if set(family_ids) != APPROVED_FAMILIES or len(family_ids) != len(set(family_ids)):
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


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    for relative in BANNED:
        if (root / relative).exists():
            errors.append(f"historical/generated content remains active: {relative}")

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
            "classification registry surface drift: "
            f"{sorted(classification_actual)} != {sorted(EXPECTED_CLASSIFICATION_REGISTRIES)}"
        )

    required_root = ["atlas-ai.yaml", "atlas-os.yaml", "governance.yaml", "plugin.json", "README.md", "LICENSE"]
    for relative in required_root:
        if not (root / relative).is_file():
            errors.append(f"missing required root file: {relative}")

    required_skills = [".agents/skills/atlas-os/SKILL.md", "skills/atlas-os/SKILL.md"]
    for relative in required_skills:
        if not (root / relative).is_file():
            errors.append(f"missing required skill file: {relative}")

    if errors:
        return errors

    for directory, expected, _suffixes in expected_sets[:-1]:
        for name in sorted(expected):
            try:
                _load(root / directory / name)
            except Exception as exc:
                errors.append(f"cannot parse {directory}/{name}: {exc}")
    for name in sorted(EXPECTED_CLASSIFICATION_REGISTRIES):
        try:
            _load(root / "registries" / "classification" / name)
        except Exception as exc:
            errors.append(f"cannot parse registries/classification/{name}: {exc}")

    try:
        manifest = _load(root / "atlas-os.yaml")
        ai = _load(root / "atlas-ai.yaml")
        governance = _load(root / "governance.yaml")
        plugin = _load(root / "plugin.json")
    except Exception as exc:
        return [f"cannot parse root machine contract: {exc}"]

    version = manifest.get("product", {}).get("version")
    if version != "3.0.3":
        errors.append(f"unexpected product version: {version}")
    if ai.get("product_version") != version:
        errors.append("atlas-ai product_version does not match atlas-os")
    if governance.get("version") != version:
        errors.append("governance version does not match atlas-os")
    if plugin.get("version") != version:
        errors.append("plugin version does not match atlas-os")

    machine_contracts = ai.get("machine_contracts", [])
    expected_contracts = {
        "atlas-os.yaml", "governance.yaml", "plugin.json",
        *(f"spec/{name}" for name in EXPECTED_SPECS),
        *(f"schemas/{name}" for name in EXPECTED_SCHEMAS),
        *(f"registries/{name}" for name in EXPECTED_REGISTRIES),
        *(f"registries/classification/{name}" for name in EXPECTED_CLASSIFICATION_REGISTRIES),
        *(f"integrations/{name}" for name in EXPECTED_INTEGRATIONS),
    }
    if set(machine_contracts) != expected_contracts:
        errors.append("atlas-ai machine_contracts does not exactly match the clean authority surface")
    for relative in machine_contracts:
        if not (root / relative).is_file():
            errors.append(f"machine contract missing: {relative}")
        if relative.startswith(("migration/", "legacy/")) or "release-verification" in relative:
            errors.append(f"historical contract leaked into machine authority: {relative}")

    canonical_skill = (root / ".agents/skills/atlas-os/SKILL.md").read_text(encoding="utf-8")
    packaged_skill = (root / "skills/atlas-os/SKILL.md").read_text(encoding="utf-8")
    if canonical_skill != packaged_skill:
        errors.append("packaged ATLAS plugin skill must exactly match the canonical agent skill")

    if "registries/classification" not in manifest.get("registries", []):
        errors.append("atlas-os registries must include registries/classification")

    _validate_classification(root, errors)

    mission_control = _load(root / "spec/mission-control.yaml")["contract"]
    prompt_entry = mission_control.get("prompt_entry", {})
    if (
        prompt_entry.get("scope") != "EVERY_ATLAS_GOVERNED_PROMPT"
        or prompt_entry.get("order") != "FIRST"
        or prompt_entry.get("before_pre_execution_flow") is not True
        or prompt_entry.get("no_tool_or_provider_before_entry") is not True
    ):
        errors.append("Mission Control must be the first gate for every ATLAS-governed prompt")
    if prompt_entry.get("role") != "governance_entry_gate_not_preprocessing_step":
        errors.append("Mission Control prompt entry must remain outside the three-step preprocessing flow")

    core = _load(root / "spec/core.yaml")["contract"]
    if core.get("pre_execution_flow") != ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"]:
        errors.append("core pre_execution_flow must contain exactly the canonical three steps")

    chatgpt_bootstrap = _load(root / "integrations/chatgpt-bootstrap.yaml")
    if chatgpt_bootstrap.get("bootstrap", {}).get("prompt_entry") != "MISSION_CONTROL_FIRST":
        errors.append("ChatGPT bootstrap must enter Mission Control first when ATLAS is active")
    if chatgpt_bootstrap.get("bootstrap", {}).get("prompt_entry_scope") != "every_user_prompt_while_atlas_active":
        errors.append("ChatGPT bootstrap must apply Mission Control entry to every prompt while ATLAS is active")
    if chatgpt_bootstrap.get("guarantees", {}).get("mission_control_first_when_atlas_active") is not True:
        errors.append("ChatGPT bootstrap must guarantee Mission Control-first behavior while ATLAS is active")
    if chatgpt_bootstrap.get("guarantees", {}).get("universal_prompt_injection") is not False:
        errors.append("ChatGPT bootstrap must not claim universal host prompt injection")

    routing = _load(root / "spec/routing.yaml")["contract"]
    if routing.get("atlas_owns_next_step") is not True or routing.get("provider_return_target") != "ATLAS":
        errors.append("routing contract must keep every next step under ATLAS")

    argus = _load(root / "integrations/argus.yaml")
    if argus.get("activation_authority") != "ATLAS" or argus.get("next_step_authority") != "ATLAS":
        errors.append("ARGUS integration must remain bounded by ATLAS authority")
    if argus.get("explicit_user_approval_required") is not True:
        errors.append("ARGUS activation must require explicit user approval")

    summary = (root / "docs/SUMMARY.md").read_text(encoding="utf-8")
    for name in EXPECTED_DOCS - {"SUMMARY.md"}:
        if name not in summary:
            errors.append(f"docs/SUMMARY.md omits {name}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the clean ATLAS-OS repository contract")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        print(f"ATLAS validation FAILED ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ATLAS validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())