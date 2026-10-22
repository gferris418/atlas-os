from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class ValidationError(ValueError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: expected a mapping")
    return data


def _assertion_passes(assertion: dict[str, Any], observed: dict[str, Any]) -> bool:
    property_name = assertion["property"]
    operator = assertion["operator"]
    expected = assertion.get("expected")
    present = property_name in observed
    value = observed.get(property_name)

    if operator == "equals":
        return present and value == expected
    if operator == "contains":
        if not present:
            return False
        if isinstance(value, (list, tuple, set, str)):
            return expected in value
        return False
    if operator == "present":
        return present and (expected is not True or value is not None)
    if operator == "absent":
        return not present
    if operator == "one-of":
        return present and isinstance(expected, list) and value in expected
    if operator == "requires-approval":
        return present and bool(value) is bool(expected)
    raise ValidationError(f"unsupported assertion operator: {operator}")


def validate_external_evidence(root: Path, evidence_path: Path) -> None:
    evidence_schema = json.loads(
        (root / "schemas/external-proof-evidence.schema.json").read_text(encoding="utf-8")
    )
    evidence = _load_yaml(evidence_path)
    jsonschema.validate(
        evidence,
        evidence_schema,
        format_checker=jsonschema.FormatChecker(),
    )

    surface = evidence["surface"]
    contract_path = root / "integrations" / surface / "release-verification.yaml"
    if not contract_path.is_file():
        raise ValidationError(f"no release verification contract for surface {surface}")
    contract = _load_yaml(contract_path)

    if evidence["verification_id"] != contract["id"]:
        raise ValidationError("verification_id does not match release contract")
    if evidence["product_version"] != contract["product_version"]:
        raise ValidationError("product_version does not match release contract")
    if evidence["control_revision"] != contract["control_revision"]:
        raise ValidationError("control_revision does not match release contract")
    if contract.get("fresh_session_required") and not evidence["fresh_session"]:
        raise ValidationError("fresh_session must be true for this release contract")
    if contract.get("independent_evidence_required") and not evidence["independent"]:
        raise ValidationError("independent must be true for this release contract")
    expected_authority = contract.get("authority", {}).get("product_manifest")
    if expected_authority and evidence["resolved_authority"] != expected_authority:
        raise ValidationError("resolved_authority does not match product authority")

    contract_checks = {item["id"]: item for item in contract["checks"]}
    evidence_checks = {item["check_id"]: item for item in evidence["checks"]}
    if set(evidence_checks) != set(contract_checks):
        missing = sorted(set(contract_checks) - set(evidence_checks))
        extra = sorted(set(evidence_checks) - set(contract_checks))
        raise ValidationError(f"check set mismatch; missing={missing}, extra={extra}")

    failed_checks: list[str] = []
    for check_id, contract_check in contract_checks.items():
        captured = evidence_checks[check_id]
        missing_evidence = [
            field for field in contract_check["required_evidence"]
            if field not in captured["evidence"]
        ]
        if missing_evidence:
            raise ValidationError(
                f"{check_id}: missing required evidence fields: {', '.join(missing_evidence)}"
            )

        assertion_failures = [
            assertion["id"]
            for assertion in contract_check["assertions"]
            if not _assertion_passes(assertion, captured["observed"])
        ]
        if assertion_failures:
            failed_checks.append(f"{check_id}({','.join(assertion_failures)})")
            continue
        if captured["result"] != "PASS":
            failed_checks.append(f"{check_id}(recorded={captured['result']})")

    if failed_checks:
        raise ValidationError("assertion failure: " + ", ".join(failed_checks))
    if evidence["overall_result"] != "PASS":
        raise ValidationError("overall_result must be PASS when all required checks pass")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate independent ATLAS external-proof evidence")
    parser.add_argument("root", help="ATLAS repository root")
    parser.add_argument("evidence", help="Captured external-proof evidence YAML")
    args = parser.parse_args(argv)

    try:
        validate_external_evidence(Path(args.root).resolve(), Path(args.evidence).resolve())
    except (OSError, ValidationError, jsonschema.ValidationError) as exc:
        print(f"external proof evidence invalid: {exc}", file=sys.stderr)
        return 1
    print("external proof evidence valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
