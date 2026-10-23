#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import yaml


REQUIRED_CONTRACT = {
    "prompt_entry": "MISSION_CONTROL_FIRST",
    "capability": "intelligence_collection",
    "provider": "argus",
    "approval_key": "ARGUS_ACTIVATION",
    "activation_authority": "ATLAS",
    "next_step_authority": "ATLAS",
    "provider_return_target": "ATLAS",
    "explicit_user_approval_required": True,
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def verify(atlas_root: Path, argus_root: Path) -> list[str]:
    errors: list[str] = []
    policy = _load_yaml(atlas_root / ".github" / "plugin-release-policy.yaml")
    atlas_manifest = _load_yaml(atlas_root / "atlas-os.yaml")
    atlas_plugin = json.loads((atlas_root / "plugin.json").read_text(encoding="utf-8"))
    pin = policy["argus_compatibility"]

    revision = _git(argus_root, "rev-parse", "HEAD")
    if revision.returncode != 0:
        return [f"cannot resolve ARGUS checkout revision: {revision.stderr.strip()}"]
    actual_commit = revision.stdout.strip()
    if actual_commit != pin["compatible_commit"]:
        errors.append(
            f"ARGUS checkout mismatch: expected {pin['compatible_commit']}, got {actual_commit}"
        )

    descriptor = _load_yaml(argus_root / pin["contract_path"])
    impact = _load_yaml(argus_root / pin["release_impact_path"])
    argus_manifest = _load_yaml(argus_root / "argus-intelligence.yaml")

    if descriptor.get("version") != pin["contract_version"]:
        errors.append("ARGUS current-integration version differs from the ATLAS policy pin")
    if descriptor.get("status") != "CURRENT":
        errors.append("ARGUS current-integration descriptor is not CURRENT")

    expected_atlas_version = atlas_manifest.get("product", {}).get("version")
    if atlas_plugin.get("version") != expected_atlas_version:
        errors.append("ATLAS plugin and product versions differ")
    if descriptor.get("atlas", {}).get("repository") != policy["plugin"]["canonical_repository"]:
        errors.append("ARGUS descriptor names a different ATLAS repository")
    if descriptor.get("atlas", {}).get("version") != expected_atlas_version:
        errors.append("ARGUS descriptor names a different ATLAS product version")

    release_commit = str(descriptor.get("atlas", {}).get("commit", ""))
    ancestor = _git(atlas_root, "merge-base", "--is-ancestor", release_commit, "HEAD")
    if not release_commit or ancestor.returncode != 0:
        errors.append("ARGUS descriptor does not pin an ancestor of the checked ATLAS revision")

    contract = descriptor.get("contract", {})
    for key, expected in REQUIRED_CONTRACT.items():
        if contract.get(key) != expected:
            errors.append(f"ARGUS current-integration contract mismatch for {key}")
    if contract.get("pre_execution_flow") != [
        "UNDERSTAND_AND_NORMALIZE",
        "MINIMAL_DOMAIN_FRAMING",
        "ROUTE",
    ]:
        errors.append("ARGUS current-integration preprocessing flow differs from ATLAS")

    if impact.get("status") != "CURRENT":
        errors.append("ARGUS plugin-release-impact descriptor is not CURRENT")
    if impact.get("chatgpt_plugin", {}).get("name") != policy["plugin"]["name"]:
        errors.append("ARGUS release-impact contract names a different plugin")
    if impact.get("chatgpt_plugin", {}).get("release_owner") != "ATLAS":
        errors.append("ARGUS release-impact contract does not retain ATLAS release authority")
    if (
        argus_manifest.get("authority", {}).get("atlas_current_integration")
        != pin["contract_path"]
    ):
        errors.append("ARGUS manifest does not point to the pinned current-integration contract")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the exact ATLAS-to-ARGUS compatibility pin.")
    parser.add_argument("--atlas-root", type=Path, default=Path("."))
    parser.add_argument("--argus-root", type=Path, required=True)
    args = parser.parse_args(argv)

    errors = verify(args.atlas_root.resolve(), args.argus_root.resolve())
    if errors:
        print(f"ARGUS compatibility verification FAILED ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("ARGUS compatibility verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
