#!/usr/bin/env python3
"""Validate the complete ATLAS-OS repository contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
import yaml

REQUIRED_PATHS = (
    "README.md",
    "atlas-os.yaml",
    "VERSION",
    "CHANGELOG.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.lock",
    "spec/core.yaml",
    "spec/runtime.yaml",
    "spec/execution-spine.yaml",
    "spec/classification.yaml",
    "spec/domain-practices.yaml",
    "spec/output.yaml",
    "schemas/atlas-os.schema.json",
    "schemas/task.schema.json",
    "schemas/execution.schema.json",
    "schemas/evidence.schema.json",
    "schemas/approval.schema.json",
    "schemas/persistence.schema.json",
    "schemas/migration.schema.json",
    "schemas/registry.schema.json",
    "schemas/dashboard.schema.json",
    "schemas/output.schema.json",
    "registries/capabilities.yaml",
    "registries/tools.yaml",
    "registries/skills.yaml",
    "registries/surfaces.yaml",
    "registries/controls.yaml",
    "registries/migrations.yaml",
    "registries/frameworks.yaml",
    "registries/taxonomies.yaml",
    "registries/classifications.yaml",
    "registries/output-profiles.yaml",
    "registries/domain-methods.yaml",
    "migration/MIG-029.yaml",
    "migration/MIG-037.yaml",
    "migration/dtif-reconciliation.yaml",
    "integrations/chatgpt/README.md",
    "integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md",
    "integrations/chatgpt/RELEASE-VERIFICATION.md",
    "integrations/codex/README.md",
    "integrations/work/README.md",
    "docs/domain-practices.md",
    "docs/taxonomy-and-classification.md",
    "docs/sample-workflow-coastal-surveillance-radar.md",
    "docs/output-standards.md",
    "docs/artifact-model.md",
    "examples/workflows/coastal-surveillance-radar-bangladesh-navy.json",
    "tests/fixtures/sample-output.json",
    "tests/unit",
    "tests/conformance",
    "tests/regression",
    "tests/integration",
    "tools/package/build_release.py",
    ".github/workflows/validate.yml",
    ".github/workflows/release.yml",
    ".github/dependabot.yml",
)

STRUCTURED_GLOBS = (
    "atlas-os.yaml",
    "spec/*.yaml",
    "registries/*.yaml",
    "migration/*.yaml",
)


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    checked_files: int = 0

    def error(self, message: str) -> None:
        self.errors.append(message)


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _validate_required(root: Path, report: ValidationReport) -> None:
    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            report.error(f"missing required path: {relative}")


def _parse_all(root: Path, report: ValidationReport) -> dict[str, Any]:
    documents: dict[str, Any] = {}
    for pattern in ("**/*.yaml", "**/*.yml", "**/*.json"):
        for path in sorted(root.glob(pattern)):
            if any(part in {".git", "dist", "__pycache__"} for part in path.parts):
                continue
            relative = _relative(root, path)
            if relative in documents:
                continue
            try:
                documents[relative] = _load(path)
                report.checked_files += 1
            except Exception as exc:  # parse diagnostics need the concrete file
                report.error(f"cannot parse {relative}: {exc}")
    return documents


def _validate_schemas(root: Path, documents: dict[str, Any], report: ValidationReport) -> None:
    for relative, document in documents.items():
        if not relative.startswith("schemas/") or not relative.endswith(".json"):
            continue
        try:
            jsonschema.Draft202012Validator.check_schema(document)
        except Exception as exc:
            report.error(f"invalid JSON Schema {relative}: {exc}")

    structured: set[str] = set()
    for pattern in STRUCTURED_GLOBS:
        structured.update(_relative(root, path) for path in root.glob(pattern))
    for relative in sorted(structured):
        document = documents.get(relative)
        if not isinstance(document, dict):
            report.error(f"structured document must be an object: {relative}")
            continue
        schema_path = document.get("schema")
        if not schema_path:
            report.error(f"structured document lacks schema declaration: {relative}")
            continue
        schema = documents.get(schema_path)
        if schema is None:
            report.error(f"{relative} references missing schema: {schema_path}")
            continue
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            report.error(f"schema violation {relative}:{location}: {error.message}")


def _collect_registry_ids(documents: dict[str, Any], report: ValidationReport) -> tuple[set[str], dict[str, dict[str, Any]]]:
    ids: set[str] = set()
    items: dict[str, dict[str, Any]] = {}
    for relative, document in documents.items():
        if not relative.startswith("registries/") or not isinstance(document, dict):
            continue
        for item in document.get("items", []):
            identifier = item.get("id")
            if identifier in ids:
                report.error(f"duplicate registry item id: {identifier}")
            elif identifier:
                ids.add(identifier)
                items[identifier] = item
    return ids, items


def _validate_references(root: Path, documents: dict[str, Any], report: ValidationReport) -> None:
    ids, items = _collect_registry_ids(documents, report)
    for identifier, item in sorted(items.items()):
        for field_name in ("requires", "conflicts_with", "dependencies"):
            for reference in item.get(field_name, []):
                if reference not in ids:
                    report.error(f"unresolved registry reference {identifier}.{field_name}: {reference}")
        fallback = item.get("fallback")
        if fallback and fallback not in ids:
            report.error(f"unresolved registry fallback {identifier}: {fallback}")
        for surface in item.get("applies_to", []):
            if surface not in ids:
                report.error(f"unresolved surface reference {identifier}: {surface}")
        for path_field in ("path", "source"):
            candidate = item.get(path_field)
            if candidate and candidate.startswith(("spec/", "migration/", "integrations/")):
                if not (root / candidate).is_file():
                    report.error(f"missing registry {path_field} for {identifier}: {candidate}")

    controls = {identifier for identifier in ids if identifier.startswith("INV-")}
    for relative, document in documents.items():
        if relative.startswith("spec/") and isinstance(document, dict):
            for invariant in document.get("invariants", []):
                if invariant not in controls:
                    report.error(f"unresolved invariant in {relative}: {invariant}")
            for reference in document.get("references", []):
                if not (root / reference).exists():
                    report.error(f"missing specification reference in {relative}: {reference}")

    framework_registry = documents.get("registries/frameworks.yaml", {})
    for item in framework_registry.get("items", []) if isinstance(framework_registry, dict) else []:
        identifier = item.get("id", "<unknown>")
        if item.get("authority") not in {"international-standard", "professional-framework", "official-primary"}:
            report.error(f"framework lacks authoritative classification: {identifier}")
        if not item.get("domains"):
            report.error(f"framework lacks domain applicability: {identifier}")
        if not str(item.get("official_source", "")).startswith("https://"):
            report.error(f"framework lacks HTTPS official source: {identifier}")
        if item.get("version_policy") == "current-official" and item.get("version") != "current-official":
            report.error(f"current-official framework has conflicting version: {identifier}")

    taxonomy_registry = documents.get("registries/taxonomies.yaml", {})
    for item in taxonomy_registry.get("items", []) if isinstance(taxonomy_registry, dict) else []:
        identifier = item.get("id", "<unknown>")
        if item.get("authority") not in {"international-standard", "professional-framework", "official-primary", "canonical"}:
            report.error(f"taxonomy lacks authoritative classification: {identifier}")
        if not item.get("classification_scope"):
            report.error(f"taxonomy lacks classification scope: {identifier}")
        if not str(item.get("official_source", "")).startswith("https://"):
            report.error(f"taxonomy lacks HTTPS official source: {identifier}")
        if item.get("version_policy") == "current-official" and item.get("version") != "current-official":
            report.error(f"current-official taxonomy has conflicting version: {identifier}")

    classification_registry = documents.get("registries/classifications.yaml", {})
    for item in classification_registry.get("items", []) if isinstance(classification_registry, dict) else []:
        identifier = item.get("id", "<unknown>")
        for required in ("taxonomy", "facet", "code", "label", "version", "source"):
            if not item.get(required):
                report.error(f"classification lacks {required}: {identifier}")
        taxonomy = item.get("taxonomy")
        if taxonomy and taxonomy not in ids:
            report.error(f"classification has unresolved taxonomy: {identifier}: {taxonomy}")
        if not item.get("triggers") and not item.get("match_all"):
            report.error(f"classification lacks match terms: {identifier}")

    output_schema = documents.get("schemas/output.schema.json", {})
    output_fields = set(output_schema.get("properties", {})) if isinstance(output_schema, dict) else set()
    output_registry = documents.get("registries/output-profiles.yaml", {})
    output_items = output_registry.get("items", []) if isinstance(output_registry, dict) else []
    for item in output_items:
        identifier = item.get("id", "<unknown>")
        if not str(identifier).startswith("output."):
            report.error(f"output profile has invalid id: {identifier}")
        for required in (
            "format", "supported_formats", "required_fields", "task_classes",
            "outcome_first", "citations", "visuals", "max_initial_sections",
            "machine_readable", "validation_checks", "standards",
            "library_collection", "file_extensions",
        ):
            if required not in item:
                report.error(f"output profile lacks {required}: {identifier}")
        if item.get("format") not in item.get("supported_formats", []):
            report.error(f"output profile default format is unsupported: {identifier}")
        missing_extensions = set(item.get("supported_formats", [])) - set(item.get("file_extensions", {}))
        if missing_extensions:
            report.error(f"output profile lacks file extensions {identifier}: {sorted(missing_extensions)}")
        unknown_fields = set(item.get("required_fields", [])) - output_fields
        if unknown_fields:
            report.error(f"output profile has unknown required fields {identifier}: {sorted(unknown_fields)}")
        overlap = set(item.get("required_fields", [])) & set(item.get("optional_fields", []))
        if overlap:
            report.error(f"output profile repeats required fields as optional {identifier}: {sorted(overlap)}")

    profile_ids = {item.get("id") for item in output_items}
    if "output.answer-concise" not in profile_ids:
        report.error("output profile registry lacks the concise-answer fallback")
    output_spec = documents.get("spec/output.yaml", {})
    for identifier in output_spec.get("contract", {}).get("profiles", []) if isinstance(output_spec, dict) else []:
        if identifier not in profile_ids:
            report.error(f"output specification references missing profile: {identifier}")

    domain_method_registry = documents.get("registries/domain-methods.yaml", {})
    domain_methods = domain_method_registry.get("items", []) if isinstance(domain_method_registry, dict) else []
    for item in domain_methods:
        identifier = item.get("id", "<unknown>")
        for required in (
            "capabilities", "requires", "conflicts_with", "fallback", "authority",
            "permission", "risk_class", "priority", "version", "source", "source_commit",
            "contract_version", "contract_sha256", "task_classes", "activation_authority",
            "consumer_id", "requires_domain_handoff",
            "accepted_handoff_states", "blocked_handoff_execution", "owns_execution_spine",
            "owns_planning", "owns_approvals",
        ):
            if required not in item:
                report.error(f"domain method lacks {required}: {identifier}")
        if item.get("activation_authority") != "ATLAS_OS":
            report.error(f"domain method activation authority is not ATLAS_OS: {identifier}")
        if "BLOCKED" in item.get("accepted_handoff_states", []):
            report.error(f"domain method accepts BLOCKED handoff: {identifier}")
        if any(item.get(field) for field in ("owns_execution_spine", "owns_planning", "owns_approvals")):
            report.error(f"domain method claims ATLAS governance ownership: {identifier}")
        if item.get("source_commit") not in item.get("source", ""):
            report.error(f"domain method source is not immutable: {identifier}")


def _validate_authority_and_release(root: Path, documents: dict[str, Any], report: ValidationReport) -> None:
    manifest = documents.get("atlas-os.yaml")
    if not isinstance(manifest, dict):
        report.error("atlas-os.yaml is unavailable or invalid")
        return
    product = manifest.get("product", {})
    version = product.get("version", "")
    status = product.get("status")
    channel = product.get("release_channel")

    if (root / "VERSION").read_text(encoding="utf-8").strip() != "atlas-os.yaml#/product/version":
        report.error("VERSION must point to atlas-os.yaml instead of declaring a competing version")

    for relative, document in documents.items():
        if relative == "atlas-os.yaml" or not isinstance(document, dict):
            continue
        if isinstance(document.get("product"), dict) and "version" in document["product"]:
            report.error(f"competing product version authority: {relative}")

    if status == "RELEASED" and channel != "stable":
        report.error("RELEASED product must use the stable channel")
    if status == "CANDIDATE" and channel != "candidate":
        report.error("CANDIDATE product must use the candidate channel")
    if status == "CANDIDATE" and not re.search(r"-[0-9A-Za-z.-]+$", version):
        report.error("candidate status requires a prerelease version")
    if status == "RELEASED" and re.search(r"-[0-9A-Za-z.-]+$", version):
        report.error("released status cannot use a prerelease version")

    migrations = {
        document.get("id"): document
        for relative, document in documents.items()
        if relative.startswith("migration/") and isinstance(document, dict) and document.get("id")
    }
    blockers = manifest.get("release", {}).get("blocking_controls", [])
    for blocker in blockers:
        if blocker not in migrations:
            report.error(f"release blocker has no migration record: {blocker}")
        elif not migrations[blocker].get("release_blocking"):
            report.error(f"manifest blocker is not marked release-blocking: {blocker}")
    open_blockers = [
        blocker for blocker in blockers
        if blocker in migrations and migrations[blocker].get("status") != "CLOSED"
    ]
    if status == "RELEASED" and open_blockers:
        report.error(f"RELEASED state has open blockers: {', '.join(open_blockers)}")

    readme = (root / "README.md").read_text(encoding="utf-8")
    if open_blockers and re.search(r"Release status:\*\*\s*\*\*RELEASED", readme, re.IGNORECASE):
        report.error("README claims RELEASED while release blockers are open")


def _validate_distribution_controls(root: Path, documents: dict[str, Any], report: ValidationReport) -> None:
    manifest = documents.get("atlas-os.yaml", {})
    version = manifest.get("product", {}).get("version") if isinstance(manifest, dict) else None
    instructions = root / "integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md"
    if instructions.exists():
        text = instructions.read_text(encoding="utf-8")
        if version and f"Version: `{version}`" not in text:
            report.error("ChatGPT instructions do not match the manifest version")
        for required in ("ATLAS/chatgpt", "Control revision:", "CAPABILITY_UNAVAILABLE"):
            if required not in text:
                report.error(f"ChatGPT instructions lack required control: {required}")

    lock_path = root / "requirements.lock"
    if lock_path.exists():
        lock_text = lock_path.read_text(encoding="utf-8")
        if "--hash=sha256:" not in lock_text:
            report.error("requirements.lock is not hash locked")

    for relative in (".github/workflows/validate.yml", ".github/workflows/release.yml"):
        path = root / relative
        if not path.exists():
            continue
        workflow = path.read_text(encoding="utf-8")
        for reference in re.findall(r"uses:\s*[^@\s]+@([^\s#]+)", workflow):
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                report.error(f"workflow action is not commit-pinned: {relative}: {reference}")
        if "pip install --require-hashes --requirement requirements.lock" not in workflow:
            report.error(f"workflow does not install the hash-locked dependency graph: {relative}")


def validate_repository(root: Path) -> ValidationReport:
    root = root.resolve()
    report = ValidationReport()
    _validate_required(root, report)
    documents = _parse_all(root, report)
    _validate_schemas(root, documents, report)
    _validate_references(root, documents, report)
    _validate_authority_and_release(root, documents, report)
    _validate_distribution_controls(root, documents, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    args = parser.parse_args(argv)
    report = validate_repository(args.root)
    if report.errors:
        print(f"ATLAS repository validation FAILED ({len(report.errors)} errors)")
        for error in report.errors:
            print(f"- {error}")
        return 1
    print(f"ATLAS repository validation PASSED ({report.checked_files} structured files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

