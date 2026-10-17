"""Durable persistence adapters for canonical ATLAS library outputs."""

from __future__ import annotations

import hashlib
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .runtime import PersistenceReceipt, confirm_library_save


class FileSystemLibraryAdapter:
    """Atomically persist, read back, and checksum outputs inside a library root."""

    def __init__(self, workspace_root: Path, library_root: str = "library") -> None:
        logical_root = PurePosixPath(library_root)
        if logical_root.is_absolute() or not logical_root.parts or any(
            part in {"", ".", ".."} for part in logical_root.parts
        ):
            raise ValueError("library root must be a safe relative path")
        self.workspace_root = workspace_root.resolve()
        self.logical_root = logical_root
        self.storage_root = (self.workspace_root / Path(*logical_root.parts)).resolve()

    def _target(self, location: str) -> Path:
        logical_path = PurePosixPath(location)
        if logical_path.is_absolute() or any(part in {"", ".", ".."} for part in logical_path.parts):
            raise ValueError("library location must be a safe relative path")
        target = (self.workspace_root / Path(*logical_path.parts)).resolve()
        if not target.is_relative_to(self.storage_root):
            raise ValueError("library location escapes the configured root")
        return target

    def save(self, record: dict[str, Any], content: str | bytes) -> dict[str, Any]:
        if record.get("delivery_status") != "READY" or not record.get("location"):
            raise ValueError("filesystem persistence requires a READY library record")
        payload = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        target = self._target(record["location"])
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            if target.read_bytes() != payload:
                raise FileExistsError(f"refusing to overwrite canonical output: {record['location']}")
        else:
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.link(temporary_path, target)
                temporary_path.unlink()
                directory_descriptor = os.open(target.parent, os.O_RDONLY)
                try:
                    os.fsync(directory_descriptor)
                finally:
                    os.close(directory_descriptor)
            finally:
                temporary_path.unlink(missing_ok=True)

        verified_payload = target.read_bytes()
        if verified_payload != payload:
            raise OSError("durable output failed read-back verification")
        checksum = hashlib.sha256(verified_payload).hexdigest()
        receipt = PersistenceReceipt(
            adapter="filesystem",
            location=record["location"],
            checksum=f"sha256:{checksum}",
            bytes_written=len(verified_payload),
            verified_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        return confirm_library_save(deepcopy(record), receipt)
