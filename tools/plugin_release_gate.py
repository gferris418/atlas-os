#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import yaml


def load_policy(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _matches_exact_or_prefix(path: str, rules: dict) -> bool:
    exact = set(rules.get("exact", []))
    prefixes = tuple(rules.get("prefixes", []))
    return path in exact or any(path.startswith(prefix) for prefix in prefixes)


def classify_paths(changed_paths: list[str], policy: dict) -> dict:
    normalized = sorted({path.strip() for path in changed_paths if path and path.strip()})
    impact = policy.get("impact", {})
    release_rules = impact.get("release_required", {})
    review_rules = impact.get("review_required", {})

    release_matches = [path for path in normalized if _matches_exact_or_prefix(path, release_rules)]
    review_matches = [
        path
        for path in normalized
        if path not in release_matches and _matches_exact_or_prefix(path, review_rules)
    ]

    return {
        "release_required": bool(release_matches),
        "review_required": bool(release_matches or review_matches),
        "release_matches": release_matches,
        "review_matches": review_matches,
        "changed_paths": normalized,
    }


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"ARGUS checkout is not a readable Git worktree: {root}") from exc


def validate_argus_checkout(argus_root: Path, policy: dict, *, atlas_root: Path | None = None) -> dict:
    """Validate the actual pinned ARGUS checkout against the ATLAS release policy.

    This is deliberately stronger than copying configured commit/version strings into
    release metadata: the checked-out Git HEAD and contract files must independently
    match the policy and the ATLAS plugin release being validated.
    """
    argus_root = Path(argus_root).resolve()
    atlas_root = Path(atlas_root or Path.cwd()).resolve()
    compatibility = policy.get("argus_compatibility", {})

    expected_commit = compatibility.get("compatible_commit")
    if not isinstance(expected_commit, str) or len(expected_commit) != 40:
        raise ValueError("policy must pin a 40-character ARGUS compatible_commit")
    actual_commit = _git_head(argus_root)
    if actual_commit != expected_commit:
        raise ValueError(f"ARGUS checkout HEAD mismatch: {actual_commit} != {expected_commit}")

    contract_relative = compatibility.get("contract_path")
    if not isinstance(contract_relative, str) or not contract_relative:
        raise ValueError("policy must declare argus_compatibility.contract_path")
    contract_path = argus_root / contract_relative
    if not contract_path.is_file():
        raise FileNotFoundError(f"pinned ARGUS contract missing: {contract_relative}")
    descriptor = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    expected_contract_version = compatibility.get("contract_version")
    actual_contract_version = descriptor.get("version")
    if actual_contract_version != expected_contract_version:
        raise ValueError(
            f"ARGUS contract version mismatch: {actual_contract_version} != {expected_contract_version}"
        )
    if descriptor.get("status") != "CURRENT":
        raise ValueError("pinned ARGUS integration contract must have status CURRENT")

    plugin_manifest = json.loads((atlas_root / policy["plugin"]["manifest"]).read_text(encoding="utf-8"))
    atlas_descriptor = descriptor.get("atlas", {})
    if atlas_descriptor.get("repository") != policy["plugin"]["canonical_repository"]:
        raise ValueError("ARGUS contract references a different ATLAS repository")
    if atlas_descriptor.get("version") != plugin_manifest.get("version"):
        raise ValueError(
            "ARGUS contract ATLAS version does not match the plugin release version: "
            f"{atlas_descriptor.get('version')} != {plugin_manifest.get('version')}"
        )

    contract = descriptor.get("contract", {})
    required_contract = {
        "prompt_entry": "MISSION_CONTROL_FIRST",
        "prompt_entry_scope": "every_user_prompt_while_atlas_active",
        "capability": "intelligence_collection",
        "provider": "argus",
        "approval_key": "ARGUS_ACTIVATION",
        "activation_authority": "ATLAS",
        "next_step_authority": "ATLAS",
        "provider_return_target": "ATLAS",
        "explicit_user_approval_required": True,
        "pre_execution_flow": ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
    }
    for key, expected in required_contract.items():
        if contract.get(key) != expected:
            raise ValueError(f"pinned ARGUS contract invariant mismatch for {key}")

    expected_impact_relative = compatibility.get("release_impact_path")
    actual_impact_relative = contract.get("plugin_release_impact")
    if actual_impact_relative != expected_impact_relative:
        raise ValueError("ARGUS integration contract does not reference the release-impact contract pinned by policy")
    impact_path = argus_root / expected_impact_relative
    if not impact_path.is_file():
        raise FileNotFoundError(f"pinned ARGUS release-impact contract missing: {expected_impact_relative}")
    impact = yaml.safe_load(impact_path.read_text(encoding="utf-8"))
    if impact.get("status") != "CURRENT":
        raise ValueError("pinned ARGUS release-impact contract must have status CURRENT")
    boundary = impact.get("boundary_changes", {})
    if boundary.get("plugin_review_required") is not True or boundary.get("atlas_release_decision_required") is not True:
        raise ValueError("ARGUS release-impact contract must require ATLAS review and release decision for boundary changes")

    return {
        "commit": actual_commit,
        "contract_version": actual_contract_version,
        "atlas_version": atlas_descriptor.get("version"),
        "contract_path": contract_relative,
        "release_impact_path": expected_impact_relative,
        "validated": True,
    }


def build_metadata(
    *,
    policy: dict,
    changed_paths: list[str],
    atlas_commit: str,
    argus_commit: str | None = None,
    argus_contract_version: str | None = None,
    argus_contract_validated: bool = False,
) -> dict:
    classification = classify_paths(changed_paths, policy)
    argus = policy.get("argus_compatibility", {})
    compatible_commit = argus_commit or argus.get("compatible_commit")
    contract_version = argus_contract_version or argus.get("contract_version")

    return {
        "schema_version": "1.0.0",
        "plugin": {
            "name": policy["plugin"]["name"],
            "canonical_repository": policy["plugin"]["canonical_repository"],
            "manifest": policy["plugin"]["manifest"],
            "primary_skill": policy["plugin"]["primary_skill"],
        },
        "publication": {
            "automatic": bool(policy["publication"]["automatic"]),
            "mechanism": policy["publication"]["mechanism"],
            "preserve_plugin_identity": bool(policy["publication"]["preserve_plugin_identity"]),
        },
        "release_required": classification["release_required"],
        "review_required": classification["review_required"],
        "impact": {
            "release_matches": classification["release_matches"],
            "review_matches": classification["review_matches"],
            "changed_paths": classification["changed_paths"],
        },
        "source": {
            "atlas_commit": atlas_commit,
            "argus_compatible_commit": compatible_commit,
            "argus_contract_version": contract_version,
            "argus_contract_validated": bool(argus_contract_validated),
        },
    }


def _safe_bundle_source(root: Path, relative: object) -> tuple[Path, Path]:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("bundle paths must be non-empty relative paths")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"bundle path escapes repository: {relative}")
    root = root.resolve()
    source = (root / candidate).resolve()
    if not source.is_relative_to(root) or source == root or (root / candidate).is_symlink():
        raise ValueError(f"bundle path escapes repository: {relative}")
    return source, candidate


def _safe_output_relative(relative: object, *, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"{label} must be a non-empty relative path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"{label} must stay inside the bundle directory")
    return candidate


def write_bundle(root: Path, policy: dict, metadata: dict, output_dir: Path) -> Path:
    root = root.resolve()
    output_dir = output_dir.resolve()
    bundle_root = output_dir / "plugin"
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"bundle output is not a directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    if bundle_root.is_symlink():
        bundle_root.unlink()
    elif bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True, exist_ok=True)

    for relative in policy["bundle"]["paths"]:
        source, destination_relative = _safe_bundle_source(root, relative)
        if not source.is_file():
            raise FileNotFoundError(f"bundle path missing: {relative}")
        destination = bundle_root / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    metadata_name = _safe_output_relative(
        policy["bundle"].get("metadata_file", "plugin-release-metadata.json"),
        label="bundle metadata path",
    )
    metadata_path = output_dir / metadata_name
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    archive_path = output_dir / "atlas-os-chatgpt-plugin.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root))
    return archive_path


def _read_changed_paths(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"changed-path input missing: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify ATLAS changes for ChatGPT plugin release impact.")
    parser.add_argument("--policy", default=".github/plugin-release-policy.yaml")
    parser.add_argument("--changed-path-file", required=True)
    parser.add_argument("--atlas-commit", required=True)
    parser.add_argument("--argus-commit")
    parser.add_argument("--argus-contract-version")
    parser.add_argument("--argus-root")
    parser.add_argument("--metadata-output", default="plugin-release-metadata.json")
    parser.add_argument("--bundle-dir")
    args = parser.parse_args(argv)

    root = Path.cwd()
    policy = load_policy(root / args.policy)
    changed_paths = _read_changed_paths(Path(args.changed_path_file))

    validation: dict | None = None
    if args.argus_root:
        validation = validate_argus_checkout(Path(args.argus_root), policy, atlas_root=root)

    metadata = build_metadata(
        policy=policy,
        changed_paths=changed_paths,
        atlas_commit=args.atlas_commit,
        argus_commit=validation["commit"] if validation else args.argus_commit,
        argus_contract_version=validation["contract_version"] if validation else args.argus_contract_version,
        argus_contract_validated=bool(validation),
    )

    Path(args.metadata_output).write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.bundle_dir and metadata["release_required"]:
        write_bundle(root, policy, metadata, Path(args.bundle_dir))

    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
