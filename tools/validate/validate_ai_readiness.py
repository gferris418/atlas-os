#!/usr/bin/env python3
"""Validate that every active ATLAS authority is machine-readable and AI-addressable."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class ValidationErrors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        self.items.append(message)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.add(message)


def load_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def validate_schema(root: Path, relative: str, schema_relative: str, errors: ValidationErrors) -> Any | None:
    path = root / relative
    schema_path = root / schema_relative
    if not path.is_file():
        errors.add(f"missing structured authority: {relative}")
        return None
    if not schema_path.is_file():
        errors.add(f"missing schema: {schema_relative}")
        return None
    try:
        document = load_structured(path)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(document, schema, format_checker=jsonschema.FormatChecker())
        return document
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        errors.add(f"{relative}: {exc}")
        return None


def active_normative_specs(root: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted((root / "spec").glob("*.yaml")):
        document = load_structured(path)
        if isinstance(document, dict) and document.get("status") == "active" and document.get("normative") is True:
            result.add(path.relative_to(root).as_posix())
    return result


def machine_registries(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in (root / "registries").iterdir()
        if path.is_file() and path.suffix in {".yaml", ".json"}
    }


def machine_schemas(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in (root / "schemas").glob("*.json")}


def validate(root: Path) -> list[str]:
    errors = ValidationErrors()

    product = validate_schema(root, "atlas-os.yaml", "schemas/atlas-os.schema.json", errors)
    if not isinstance(product, dict):
        return errors.items

    ai_manifest_rel = product.get("authority", {}).get("ai_manifest")
    errors.require(ai_manifest_rel == "ai/manifest.yaml", "atlas-os.yaml must bind authority.ai_manifest to ai/manifest.yaml")
    manifest = validate_schema(root, "ai/manifest.yaml", "schemas/ai-manifest.schema.json", errors)
    if not isinstance(manifest, dict):
        return errors.items

    product_version = product.get("product", {}).get("version")
    control_revision = manifest.get("product", {}).get("control_revision")
    errors.require(manifest.get("product", {}).get("version") == product_version, "AI manifest version must match atlas-os.yaml")
    errors.require(manifest.get("product", {}).get("authority") == "atlas-os.yaml", "AI manifest must resolve atlas-os.yaml as product authority")
    errors.require(manifest.get("policy", {}).get("authoritative_formats") == ["yaml", "json"], "AI authoritative formats must be YAML and JSON")
    errors.require(manifest.get("policy", {}).get("markdown_role") == "documentation-only", "Markdown must be documentation-only")
    errors.require(manifest.get("policy", {}).get("structured_output_required") is True, "structured output must be required")

    authority = manifest.get("authority", {})
    listed_specs = set(authority.get("specifications", []))
    listed_registries = set(authority.get("registries", []))
    listed_schemas = set(authority.get("schemas", []))
    errors.require(listed_specs == active_normative_specs(root), "AI manifest specification index must exactly cover all active normative specs")
    errors.require(listed_registries == machine_registries(root), "AI manifest registry index must exactly cover every YAML/JSON registry")
    errors.require(listed_schemas == machine_schemas(root), "AI manifest schema index must exactly cover every JSON Schema")

    for relative in sorted(listed_specs | listed_registries | listed_schemas):
        errors.require((root / relative).is_file(), f"AI manifest references missing authority: {relative}")

    surfaces = load_structured(root / "registries/surfaces.yaml")
    active_surfaces = {item["id"]: item for item in surfaces.get("items", []) if item.get("status") == "active"}
    adapter_index = {item["surface_id"]: item["path"] for item in manifest.get("adapters", [])}
    errors.require(set(adapter_index) == set(active_surfaces), "AI manifest adapter index must exactly match active surfaces")

    adapter_schema = "schemas/ai-host-adapter.schema.json"
    adapter_documents: dict[str, dict[str, Any]] = {}
    for surface_id, surface in active_surfaces.items():
        source = surface.get("source")
        path = surface.get("path")
        errors.require(source == path, f"{surface_id}: source and path must identify the same structured adapter")
        errors.require(isinstance(source, str) and source.endswith((".yaml", ".json")), f"{surface_id}: active authority cannot be Markdown-only")
        errors.require(adapter_index.get(surface_id) == source, f"{surface_id}: AI manifest adapter path drift")
        if isinstance(source, str):
            adapter = validate_schema(root, source, adapter_schema, errors)
            if isinstance(adapter, dict):
                adapter_documents[surface_id] = adapter
                errors.require(adapter.get("surface_id") == surface_id, f"{surface_id}: adapter surface_id mismatch")
                errors.require(adapter.get("authority", {}).get("product_manifest") == "atlas-os.yaml", f"{surface_id}: adapter product authority mismatch")
                errors.require(adapter.get("authority", {}).get("ai_manifest") == "ai/manifest.yaml", f"{surface_id}: adapter AI manifest mismatch")
                errors.require(adapter.get("control_revision") == control_revision, f"{surface_id}: adapter control revision drift")

    output_registry = load_structured(root / "registries/output-profiles.yaml")
    for profile in output_registry.get("items", []):
        if profile.get("status") != "active":
            continue
        profile_id = profile.get("id", "unknown")
        errors.require(profile.get("machine_readable") is True, f"{profile_id}: active output profile must be machine-readable")
        canonical_format = profile.get("format")
        errors.require(canonical_format in {"json", "yaml"}, f"{profile_id}: canonical format must be json or yaml")
        errors.require(canonical_format in profile.get("supported_formats", []), f"{profile_id}: canonical format missing from supported_formats")
        errors.require(canonical_format in profile.get("file_extensions", {}), f"{profile_id}: canonical format missing file extension")

    migration_registry = load_structured(root / "registries/migrations.yaml")
    migration_items = {item["id"]: item for item in migration_registry.get("items", [])}
    canonical_migrations: dict[str, dict[str, Any]] = {}
    for migration_id, item in migration_items.items():
        path = item.get("path")
        if not isinstance(path, str) or not (root / path).is_file():
            errors.add(f"{migration_id}: missing canonical migration record")
            continue
        record = validate_schema(root, path, "schemas/migration.schema.json", errors)
        if not isinstance(record, dict):
            continue
        canonical_migrations[migration_id] = record
        errors.require(record.get("id") == migration_id, f"{migration_id}: canonical migration id mismatch")
        errors.require(str(record.get("status", "")).lower() == item.get("status"), f"{migration_id}: registry/canonical status drift")
        errors.require(record.get("release_blocking") == item.get("release_blocking"), f"{migration_id}: release_blocking drift")
        errors.require(record.get("dependencies", []) == item.get("dependencies", []), f"{migration_id}: dependency drift")

    open_blockers = {
        migration_id
        for migration_id, record in canonical_migrations.items()
        if record.get("release_blocking") is True and record.get("status") != "CLOSED"
    }
    errors.require(set(product.get("release", {}).get("blocking_controls", [])) == open_blockers, "atlas-os.yaml release blockers must exactly match open release-blocking migrations")

    expected_verification_paths = {
        adapter.get("release_verification")
        for adapter in adapter_documents.values()
        if adapter.get("release_verification")
    }
    listed_verification_paths = set(manifest.get("controls", {}).get("release_verification", []))
    errors.require(listed_verification_paths == expected_verification_paths, "AI manifest release-verification index must exactly match adapters requiring external proof")

    covered_controls: set[str] = set()
    for relative in sorted(listed_verification_paths):
        record = validate_schema(root, relative, "schemas/release-verification.schema.json", errors)
        if not isinstance(record, dict):
            continue
        errors.require(record.get("version") == product_version, f"{relative}: version drift")
        errors.require(record.get("control_revision") == control_revision, f"{relative}: control revision drift")
        for migration_id in record.get("migration_controls", []):
            covered_controls.add(migration_id)
            errors.require(migration_id in canonical_migrations, f"{relative}: unknown migration control {migration_id}")
        if record.get("status") == "PASS":
            errors.require(bool(record.get("evidence")), f"{relative}: PASS requires evidence")

    errors.require(open_blockers <= covered_controls, "every open release blocker must have machine-readable external verification coverage")

    output = manifest.get("output", {})
    errors.require(output.get("schema") == "schemas/output.schema.json", "AI output schema must be schemas/output.schema.json")
    errors.require(output.get("registry") == "registries/output-profiles.yaml", "AI output registry mismatch")
    errors.require(output.get("envelope_required") is True, "AI output envelope must be mandatory")

    return errors.items


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    problems = validate(root)
    if problems:
        print("AI readiness validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("AI readiness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
