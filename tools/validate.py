#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

EXPECTED_SPECS = {
    "approvals.yaml", "context.yaml", "control-plane.yaml", "core.yaml", "evidence.yaml",
    "execution.yaml", "mission-control.yaml", "observability.yaml", "persistence.yaml",
    "routing.yaml", "verification.yaml",
}
EXPECTED_SCHEMAS = {
    "approval.schema.json", "evidence.schema.json", "execution-envelope.schema.json",
    "handoff.schema.json", "output.schema.json", "routing-decision.schema.json",
}
EXPECTED_REGISTRIES = {"capabilities.yaml", "providers.yaml", "surfaces.yaml"}
EXPECTED_INTEGRATIONS = {"access-asia.yaml", "argus.yaml", "chatgpt.yaml", "generic-host.yaml", "hermes-agent.yaml"}
EXPECTED_DOCS = {
    "README.md", "SUMMARY.md", "architecture.md", "framework.md", "playbook.md", "sop.md",
    "capabilities-routing.md", "evidence-verification.md", "argus-interface.md", "host-integration.md",
    "implementation-guide.md", "examples.md",
}
BANNED = {"legacy", "migration", "library", "docs/releases", "docs/plans"}


def _load(path: Path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _names(root: Path, directory: str, suffixes: tuple[str, ...]) -> set[str]:
    base = root / directory
    return {path.name for path in base.iterdir() if path.is_file() and path.suffix in suffixes}


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

    required_root = ["atlas-ai.yaml", "atlas-os.yaml", "governance.yaml", "README.md", "LICENSE"]
    for relative in required_root:
        if not (root / relative).is_file():
            errors.append(f"missing required root file: {relative}")

    if errors:
        return errors

    for directory, expected, _suffixes in expected_sets[:-1]:
        for name in sorted(expected):
            try:
                _load(root / directory / name)
            except Exception as exc:  # validation boundary intentionally reports parse failures
                errors.append(f"cannot parse {directory}/{name}: {exc}")

    try:
        manifest = _load(root / "atlas-os.yaml")
        ai = _load(root / "atlas-ai.yaml")
        governance = _load(root / "governance.yaml")
    except Exception as exc:
        return [f"cannot parse root machine contract: {exc}"]

    version = manifest.get("product", {}).get("version")
    if version != "3.0.0":
        errors.append(f"unexpected product version: {version}")
    if ai.get("product_version") != version:
        errors.append("atlas-ai product_version does not match atlas-os")
    if governance.get("version") != version:
        errors.append("governance version does not match atlas-os")

    machine_contracts = ai.get("machine_contracts", [])
    expected_contracts = {
        "atlas-os.yaml", "governance.yaml",
        *(f"spec/{name}" for name in EXPECTED_SPECS),
        *(f"schemas/{name}" for name in EXPECTED_SCHEMAS),
        *(f"registries/{name}" for name in EXPECTED_REGISTRIES),
        *(f"integrations/{name}" for name in EXPECTED_INTEGRATIONS),
    }
    if set(machine_contracts) != expected_contracts:
        errors.append("atlas-ai machine_contracts does not exactly match the clean authority surface")
    for relative in machine_contracts:
        if not (root / relative).is_file():
            errors.append(f"machine contract missing: {relative}")
        if relative.startswith(("migration/", "legacy/")) or "release-verification" in relative:
            errors.append(f"historical contract leaked into machine authority: {relative}")

    core = _load(root / "spec/core.yaml")["contract"]
    if core.get("pre_execution_flow") != ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"]:
        errors.append("core pre_execution_flow must contain exactly the canonical three steps")

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
