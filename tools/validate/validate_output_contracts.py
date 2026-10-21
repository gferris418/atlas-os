#!/usr/bin/env python3
"""Validate that every active ATLAS output has a canonical machine-readable form."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    registry_path = root / "registries/output-profiles.yaml"
    spec_path = root / "spec/output.yaml"
    schema_path = root / "schemas/registry.schema.json"
    output_schema_path = root / "schemas/output.schema.json"

    for path in (registry_path, spec_path, schema_path, output_schema_path):
        if not path.is_file():
            errors.append(f"missing output contract: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    registry = load_yaml(registry_path)
    registry_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(registry, registry_schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        errors.append(f"output profile registry schema violation: {exc.message}")
        return errors

    for profile in registry.get("items", []):
        if profile.get("status") != "active":
            continue
        profile_id = profile.get("id", "unknown")
        canonical = profile.get("format")
        supported = profile.get("supported_formats", [])
        extensions = profile.get("file_extensions", {})
        checks = profile.get("validation_checks", [])
        standards = profile.get("standards", [])
        if profile.get("machine_readable") is not True:
            errors.append(f"{profile_id}: active profile must be machine_readable=true")
        if canonical not in {"json", "yaml"}:
            errors.append(f"{profile_id}: canonical format must be json or yaml")
        if canonical not in supported:
            errors.append(f"{profile_id}: canonical format missing from supported_formats")
        if canonical not in extensions:
            errors.append(f"{profile_id}: canonical format missing from file_extensions")
        if "schema-validity" not in checks:
            errors.append(f"{profile_id}: canonical output must require schema-validity")
        if not any("JSON Schema 2020-12" in item for item in standards):
            errors.append(f"{profile_id}: canonical output must declare JSON Schema 2020-12")

    spec = load_yaml(spec_path)
    contract = spec.get("contract", {})
    envelope_rule = str(contract.get("envelope_rule", ""))
    validation_rule = str(contract.get("validation_rule", ""))
    if "Every completed ATLAS output" not in envelope_rule or "schema-valid" not in envelope_rule:
        errors.append("spec/output.yaml must require a schema-valid envelope for every completed output")
    if "canonical structured envelope" not in validation_rule:
        errors.append("spec/output.yaml must validate the canonical structured envelope")
    if contract.get("standards", {}).get("canonical_output") != "JSON Schema 2020-12":
        errors.append("spec/output.yaml canonical output standard must be JSON Schema 2020-12")

    output_schema = json.loads(output_schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator.check_schema(output_schema)
    except jsonschema.SchemaError as exc:
        errors.append(f"schemas/output.schema.json is invalid: {exc.message}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)
    errors = validate(args.root)
    if errors:
        print(f"ATLAS output-contract validation FAILED ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ATLAS output-contract validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
