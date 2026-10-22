#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
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


def build_metadata(
    *,
    policy: dict,
    changed_paths: list[str],
    atlas_commit: str,
    argus_commit: str | None = None,
    argus_contract_version: str | None = None,
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
        },
    }


def write_bundle(root: Path, policy: dict, metadata: dict, output_dir: Path) -> Path:
    bundle_root = output_dir / "plugin"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    bundle_root.mkdir(parents=True, exist_ok=True)

    for relative in policy["bundle"]["paths"]:
        source = root / relative
        if not source.is_file():
            raise FileNotFoundError(f"bundle path missing: {relative}")
        destination = bundle_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    metadata_name = policy["bundle"].get("metadata_file", "plugin-release-metadata.json")
    (output_dir / metadata_name).write_text(
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
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify ATLAS changes for ChatGPT plugin release impact.")
    parser.add_argument("--policy", default=".github/plugin-release-policy.yaml")
    parser.add_argument("--changed-path-file", required=True)
    parser.add_argument("--atlas-commit", required=True)
    parser.add_argument("--argus-commit")
    parser.add_argument("--argus-contract-version")
    parser.add_argument("--metadata-output", default="plugin-release-metadata.json")
    parser.add_argument("--bundle-dir")
    args = parser.parse_args(argv)

    root = Path.cwd()
    policy = load_policy(root / args.policy)
    changed_paths = _read_changed_paths(Path(args.changed_path_file))
    metadata = build_metadata(
        policy=policy,
        changed_paths=changed_paths,
        atlas_commit=args.atlas_commit,
        argus_commit=args.argus_commit,
        argus_contract_version=args.argus_contract_version,
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
