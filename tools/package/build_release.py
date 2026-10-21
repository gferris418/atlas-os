#!/usr/bin/env python3
"""Build deterministic ATLAS-OS release-candidate archives."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import stat
import subprocess
import sys
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import yaml


def _run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tracked_files(root: Path) -> list[Path]:
    output = _run(["git", "ls-files", "-z"], root)
    return sorted(root / name for name in output.split("\0") if name)


def _assert_clean(root: Path) -> None:
    changes = _run(["git", "status", "--porcelain", "--untracked-files=no"], root)
    if changes:
        raise RuntimeError("tracked files are dirty; commit the intended source before packaging")


def _payload(root: Path, files: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]


def _open_release_blockers(root: Path, manifest: dict[str, object]) -> list[str]:
    blockers = manifest.get("release", {}).get("blocking_controls", [])
    open_blockers: list[str] = []
    for blocker in blockers:
        matches = [
            path for path in (root / "migration").glob("*.yaml")
            if yaml.safe_load(path.read_text(encoding="utf-8")).get("id") == blocker
        ]
        if not matches:
            open_blockers.append(str(blocker))
            continue
        record = yaml.safe_load(matches[0].read_text(encoding="utf-8"))
        if record.get("status") != "CLOSED":
            open_blockers.append(str(blocker))
    return open_blockers


def validate_release_tag(
    manifest: dict[str, object], tag: str, open_blockers: list[str]
) -> str:
    """Bind a publication tag to manifest identity and release governance."""
    product = manifest["product"]
    version = str(product["version"])
    expected = f"v{version}"
    if tag != expected:
        raise RuntimeError(f"release tag {tag!r} does not match manifest version {expected!r}")

    status = product["status"]
    channel = product["release_channel"]
    prerelease = "-" in version
    if prerelease:
        if status not in {"CANDIDATE", "VERIFIED"} or channel != "candidate":
            raise RuntimeError("prerelease tag requires candidate channel and candidate/verified status")
    else:
        if status != "RELEASED" or channel != "stable":
            raise RuntimeError("stable tag requires RELEASED status on the stable channel")
        if open_blockers:
            raise RuntimeError(
                "stable tag is forbidden with open release blockers: " + ", ".join(open_blockers)
            )
    return expected


def _build_tar(root: Path, output: Path, prefix: str, files: list[Path], epoch: int) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in files:
                    relative = path.relative_to(root).as_posix()
                    info = archive.gettarinfo(str(path), arcname=f"{prefix}/{relative}")
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = epoch
                    with path.open("rb") as handle:
                        archive.addfile(info, handle)


def _build_zip(root: Path, output: Path, prefix: str, files: list[Path], epoch: int) -> None:
    moment = datetime.fromtimestamp(max(epoch, 315532800), tz=UTC)
    stamp = (moment.year, moment.month, moment.day, moment.hour, moment.minute, moment.second)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{relative}", stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = stat.S_IFREG | (0o755 if os.access(path, os.X_OK) else 0o644)
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _validate_release_source(root: Path) -> None:
    for script in (
        "tools/validate/validate_repository.py",
        "tools/validate/validate_machine_contracts.py",
        "tools/validate/validate_output_contracts.py",
    ):
        subprocess.run([sys.executable, script, "."], cwd=root, check=True)


def build(root: Path, output_dir: Path, *, release_tag: str | None = None) -> list[Path]:
    root = root.resolve()
    output_dir = (root / output_dir).resolve() if not output_dir.is_absolute() else output_dir.resolve()
    _validate_release_source(root)

    manifest = yaml.safe_load((root / "atlas-os.yaml").read_text(encoding="utf-8"))
    if release_tag is not None:
        validate_release_tag(manifest, release_tag, _open_release_blockers(root, manifest))
    _assert_clean(root)
    version = manifest["product"]["version"]
    status = manifest["product"]["status"]
    commit = _run(["git", "rev-parse", "HEAD"], root)
    epoch = int(_run(["git", "show", "-s", "--format=%ct", "HEAD"], root))
    files = _tracked_files(root)
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"atlas-os-{version}"
    tar_path = output_dir / f"{prefix}.tar.gz"
    zip_path = output_dir / f"{prefix}.zip"
    manifest_path = output_dir / f"{prefix}.manifest.json"
    checksums_path = output_dir / "SHA256SUMS"

    _build_tar(root, tar_path, prefix, files, epoch)
    _build_zip(root, zip_path, prefix, files, epoch)
    release_manifest = {
        "product": "atlas-os",
        "version": version,
        "status": status,
        "source_commit": commit,
        "source_date_epoch": epoch,
        "payload": _payload(root, files),
        "artifacts": [
            {"name": tar_path.name, "sha256": _sha256(tar_path)},
            {"name": zip_path.name, "sha256": _sha256(zip_path)},
        ],
    }
    manifest_path.write_text(json.dumps(release_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksum_targets = [tar_path, zip_path, manifest_path]
    checksums_path.write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in checksum_targets), encoding="utf-8"
    )
    return [tar_path, zip_path, manifest_path, checksums_path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("output", nargs="?", default="dist", type=Path)
    parser.add_argument("--tag", help="publication tag, which must match manifest release truth")
    args = parser.parse_args(argv)
    try:
        outputs = build(args.root, args.output, release_tag=args.tag)
    except (RuntimeError, subprocess.CalledProcessError, KeyError, OSError) as exc:
        print(f"ATLAS release build FAILED: {exc}", file=sys.stderr)
        return 1
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
