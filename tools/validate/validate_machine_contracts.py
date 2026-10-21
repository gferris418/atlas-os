#!/usr/bin/env python3
"""Validate ATLAS machine-discovery, governance, surface, verification, and migration contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml

EXTERNAL_SURFACES = ("chatgpt", "codex", "work", "hermes-agent")
ADAPTER_SURFACES = (*EXTERNAL_SURFACES, "generic-ai-host")
STATUS_MAP = {
    "OPEN": "open",
    "IN_PROGRESS": "in-progress",
    "BLOCKED": "blocked",
    "CLOSED": "closed",
}


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def _active_normative_specs(root: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted((root / "spec").glob("*.yaml")):
        record = load(path)
        if isinstance(record, dict) and record.get("status") == "active" and record.get("normative") is True:
            result.add(path.relative_to(root).as_posix())
    return result


def _machine_catalog(root: Path, directory: str) -> set[str]:
    base = root / directory
    return {
        path.relative_to(root).as_posix()
        for path in base.iterdir()
        if path.is_file() and path.suffix in {".yaml", ".yml", ".json"}
    }


def _expected_machine_contracts(root: Path) -> set[str]:
    integrations = {
        path.relative_to(root).as_posix()
        for path in (root / "integrations").rglob("*")
        if path.is_file() and path.suffix in {".yaml", ".yml", ".json"}
    }
    migrations = {
        path.relative_to(root).as_posix()
        for path in (root / "migration").glob("*.yaml")
    }
    return (
        {"atlas-os.yaml", "governance.yaml"}
        | _active_normative_specs(root)
        | _machine_catalog(root, "registries")
        | _machine_catalog(root, "schemas")
        | migrations
        | integrations
    )


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    required = (
        "atlas-ai.yaml",
        "governance.yaml",
        "schemas/ai-manifest.schema.json",
        "schemas/governance.schema.json",
        "schemas/surface-adapter.schema.json",
        "schemas/release-verification.schema.json",
        "schemas/migration.schema.json",
        "registries/surfaces.yaml",
        "registries/migrations.yaml",
        *(f"integrations/{surface}/adapter.yaml" for surface in ADAPTER_SURFACES),
        *(f"integrations/{surface}/release-verification.yaml" for surface in EXTERNAL_SURFACES),
    )
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing machine contract: {relative}")
    if errors:
        return errors

    manifest = load(root / "atlas-os.yaml")
    ai_manifest = load(root / "atlas-ai.yaml")
    governance = load(root / "governance.yaml")
    ai_schema = load(root / "schemas/ai-manifest.schema.json")
    governance_schema = load(root / "schemas/governance.schema.json")
    surface_schema = load(root / "schemas/surface-adapter.schema.json")
    verification_schema = load(root / "schemas/release-verification.schema.json")
    migration_schema = load(root / "schemas/migration.schema.json")

    try:
        jsonschema.validate(ai_manifest, ai_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        errors.append(f"atlas-ai.yaml schema violation: {exc.message}")
    try:
        jsonschema.validate(governance, governance_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        errors.append(f"governance.yaml schema violation: {exc.message}")

    product_version = manifest.get("product", {}).get("version")
    control_revision = manifest.get("execution", {}).get("control_revision")
    if ai_manifest.get("product_version") != product_version:
        errors.append(
            f"AI manifest product version drift: {ai_manifest.get('product_version')} != {product_version}"
        )
    if ai_manifest.get("control_revision") != control_revision:
        errors.append(
            f"AI manifest control revision drift: {ai_manifest.get('control_revision')} != {control_revision}"
        )
    if manifest.get("authority", {}).get("ai_manifest") != "atlas-ai.yaml":
        errors.append("atlas-os.yaml does not bind atlas-ai.yaml as the AI discovery authority")
    if manifest.get("authority", {}).get("governance") != "governance.yaml":
        errors.append("atlas-os.yaml does not bind governance.yaml as the governance authority")
    if governance.get("authority", {}).get("product_manifest") != "atlas-os.yaml":
        errors.append("governance.yaml does not bind atlas-os.yaml as product authority")
    if governance.get("authority", {}).get("ai_manifest") != "atlas-ai.yaml":
        errors.append("governance.yaml does not bind atlas-ai.yaml as discovery authority")

    machine_contracts = set(ai_manifest.get("machine_contracts", []))
    expected_machine_contracts = _expected_machine_contracts(root)
    missing_machine_contracts = expected_machine_contracts - machine_contracts
    extra_machine_contracts = machine_contracts - expected_machine_contracts
    if missing_machine_contracts:
        errors.append(
            "AI discovery omits machine authority: " + ", ".join(sorted(missing_machine_contracts))
        )
    if extra_machine_contracts:
        errors.append(
            "AI discovery declares non-authority machine contracts: "
            + ", ".join(sorted(extra_machine_contracts))
        )

    if "GOVERNANCE.md" not in set(ai_manifest.get("human_guidance", [])):
        errors.append("GOVERNANCE.md must be registered as human guidance, not machine authority")

    for relative in machine_contracts:
        path = root / relative
        if path.suffix not in {".yaml", ".yml", ".json"}:
            errors.append(f"non-structured file declared as machine contract: {relative}")
        if not path.is_file():
            errors.append(f"machine contract does not exist: {relative}")

    for relative in ai_manifest.get("human_guidance", []):
        if not relative.endswith(".md"):
            errors.append(f"human guidance must be Markdown and non-authoritative: {relative}")
        if not (root / relative).is_file():
            errors.append(f"human guidance does not exist: {relative}")

    surface_registry = load(root / "registries/surfaces.yaml")
    registered_surfaces = {item["id"]: item for item in surface_registry.get("items", [])}
    expected_ids = {f"surface.{surface}" for surface in ADAPTER_SURFACES}
    if set(registered_surfaces) != expected_ids:
        errors.append(
            f"surface registry set drift: {sorted(registered_surfaces)} != {sorted(expected_ids)}"
        )
    for surface in ADAPTER_SURFACES:
        surface_id = f"surface.{surface}"
        item = registered_surfaces.get(surface_id)
        if not item:
            continue
        expected_path = f"integrations/{surface}/adapter.yaml"
        if item.get("source") != expected_path or item.get("path") != expected_path:
            errors.append(f"surface registry must route {surface_id} to {expected_path}")
            continue
        if expected_path not in machine_contracts:
            errors.append(f"surface adapter missing from AI machine contracts: {expected_path}")
        adapter = load(root / expected_path)
        try:
            jsonschema.validate(adapter, surface_schema, format_checker=jsonschema.FormatChecker())
        except jsonschema.ValidationError as exc:
            errors.append(f"{expected_path} schema violation: {exc.message}")
            continue
        if adapter.get("surface_id") != surface_id:
            errors.append(f"surface adapter identity drift: {expected_path}")
        if set(adapter.get("capabilities", [])) != set(item.get("capabilities", [])):
            errors.append(f"surface capability drift: {surface_id}")
        expected_verification = (
            f"integrations/{surface}/release-verification.yaml"
            if surface in EXTERNAL_SURFACES
            else None
        )
        if adapter.get("release_verification") != expected_verification:
            errors.append(f"surface release-verification route drift: {surface_id}")

    declared_surfaces = set(ai_manifest.get("external_verification", {}).get("surfaces", []))
    if declared_surfaces != set(EXTERNAL_SURFACES):
        errors.append(
            f"AI manifest surface set drift: {sorted(declared_surfaces)} != {sorted(EXTERNAL_SURFACES)}"
        )

    for surface in EXTERNAL_SURFACES:
        path = root / "integrations" / surface / "release-verification.yaml"
        record = load(path)
        try:
            jsonschema.validate(
                record, verification_schema, format_checker=jsonschema.FormatChecker()
            )
        except jsonschema.ValidationError as exc:
            errors.append(f"{path.relative_to(root)} schema violation: {exc.message}")
            continue
        if record.get("surface") != surface:
            errors.append(f"surface identity drift in {path.relative_to(root)}")
        if record.get("product_version") != product_version:
            errors.append(f"product version drift in {path.relative_to(root)}")
        if record.get("control_revision") != control_revision:
            errors.append(f"control revision drift in {path.relative_to(root)}")
        if not record.get("fresh_session_required"):
            errors.append(f"external verification must require a fresh session: {surface}")
        if not record.get("independent_evidence_required"):
            errors.append(f"external verification must require independent evidence: {surface}")

    migrations: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "migration").glob("*.yaml")):
        record = load(path)
        try:
            jsonschema.validate(record, migration_schema, format_checker=jsonschema.FormatChecker())
        except jsonschema.ValidationError as exc:
            errors.append(f"{path.relative_to(root)} schema violation: {exc.message}")
            continue
        control_id = record["id"]
        migrations[control_id] = record
        evidence_ids = {item["id"] for item in record["evidence"]}
        for criterion in record["acceptance_criteria"]:
            missing = set(criterion["evidence_ids"]) - evidence_ids
            if missing:
                errors.append(
                    f"{control_id}.{criterion['id']} references missing evidence: {sorted(missing)}"
                )
            if criterion["status"] == "PASS" and not criterion["evidence_ids"]:
                errors.append(f"{control_id}.{criterion['id']} passes without linked evidence")
        if record["status"] == "CLOSED" and any(
            criterion["status"] != "PASS" for criterion in record["acceptance_criteria"]
        ):
            errors.append(f"closed migration has non-PASS criteria: {control_id}")

    registry = load(root / "registries/migrations.yaml")
    registry_items = {item["id"]: item for item in registry.get("items", [])}
    if set(registry_items) != set(migrations):
        errors.append(
            f"migration registry/control set drift: {sorted(registry_items)} != {sorted(migrations)}"
        )
    for control_id, record in migrations.items():
        item = registry_items.get(control_id)
        if not item:
            continue
        expected_status = STATUS_MAP[record["status"]]
        if item.get("status") != expected_status:
            errors.append(
                f"migration registry status drift {control_id}: {item.get('status')} != {expected_status}"
            )
        if item.get("release_blocking") != record["release_blocking"]:
            errors.append(f"migration registry release_blocking drift: {control_id}")
        if item.get("dependencies") != record["dependencies"]:
            errors.append(f"migration registry dependency drift: {control_id}")

    blockers = set(manifest.get("release", {}).get("blocking_controls", []))
    machine_controls = set(ai_manifest.get("external_verification", {}).get("controls", []))
    if blockers != machine_controls:
        errors.append(
            f"release blocker/AI verification control drift: {sorted(blockers)} != {sorted(machine_controls)}"
        )
    if governance.get("release", {}).get("released_requires_no_open_blockers") is not True:
        errors.append("governance must fail closed on release blockers")
    if governance.get("release", {}).get("missing_evidence_is_pass") is not False:
        errors.append("governance must not convert missing evidence into PASS")
    for blocker in blockers:
        record = migrations.get(blocker)
        if record is None:
            errors.append(f"release blocker lacks machine migration record: {blocker}")
        elif record["status"] == "CLOSED" and any(
            not evidence["independent"]
            for evidence in record["evidence"]
            if evidence["result"] == "PASS"
        ):
            errors.append(
                f"external release blocker {blocker} contains non-independent PASS evidence after closure"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        print(f"ATLAS machine-contract validation FAILED ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ATLAS machine-contract validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
