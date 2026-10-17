"""Durable persistence adapters for canonical ATLAS library outputs."""

from __future__ import annotations

import hashlib
import os
import secrets
from copy import deepcopy
from datetime import UTC, datetime
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
        self.storage_root = self.workspace_root / Path(*logical_root.parts)
        cursor = self.workspace_root
        for part in logical_root.parts:
            cursor /= part
            if cursor.is_symlink():
                raise ValueError("library root must not contain symlinks")
        if not self.storage_root.resolve().is_relative_to(self.workspace_root):
            raise ValueError("library root escapes the configured workspace")
        if not getattr(os, "O_NOFOLLOW", 0) or not getattr(os, "O_DIRECTORY", 0):
            raise OSError("filesystem persistence requires secure no-follow directory operations")

    def _location_parts(self, location: str) -> tuple[str, ...]:
        logical_path = PurePosixPath(location)
        if logical_path.is_absolute() or any(part in {"", ".", ".."} for part in logical_path.parts):
            raise ValueError("library location must be a safe relative path")
        root_parts = self.logical_root.parts
        if logical_path.parts[:len(root_parts)] != root_parts:
            raise ValueError("library location escapes the configured root")
        relative = logical_path.parts[len(root_parts):]
        if len(relative) < 2:
            raise ValueError("library location requires a collection and filename")
        return relative

    @staticmethod
    def _directory_flags() -> int:
        return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW

    @classmethod
    def _open_child_directory(cls, parent_fd: int, name: str, boundary: str) -> int:
        try:
            os.mkdir(name, mode=0o755, dir_fd=parent_fd)
        except FileExistsError:
            pass
        try:
            return os.open(name, cls._directory_flags(), dir_fd=parent_fd)
        except OSError as error:
            raise ValueError(f"{boundary} must contain only real directories") from error

    def _open_parent(self, relative: tuple[str, ...]) -> tuple[int, str]:
        current_fd = os.open(self.workspace_root, self._directory_flags())
        try:
            for part in self.logical_root.parts:
                next_fd = self._open_child_directory(current_fd, part, "library root")
                os.close(current_fd)
                current_fd = next_fd
            for part in relative[:-1]:
                next_fd = self._open_child_directory(current_fd, part, "library location")
                os.close(current_fd)
                current_fd = next_fd
            return current_fd, relative[-1]
        except Exception:
            os.close(current_fd)
            raise

    @staticmethod
    def _read_file(parent_fd: int, filename: str) -> bytes:
        descriptor = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        with os.fdopen(descriptor, "rb") as handle:
            return handle.read()

    def _parent_is_stable(self, parent_fd: int, parent_parts: tuple[str, ...]) -> bool:
        current_fd = os.open(self.workspace_root, self._directory_flags())
        try:
            for part in (*self.logical_root.parts, *parent_parts):
                next_fd = os.open(part, self._directory_flags(), dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd
            current = os.fstat(current_fd)
            held = os.fstat(parent_fd)
            return current.st_dev == held.st_dev and current.st_ino == held.st_ino
        except OSError:
            return False
        finally:
            os.close(current_fd)

    def save(self, record: dict[str, Any], content: str | bytes) -> dict[str, Any]:
        if record.get("delivery_status") != "READY" or not record.get("location"):
            raise ValueError("filesystem persistence requires a READY library record")
        payload = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        relative = self._location_parts(record["location"])
        parent_fd, filename = self._open_parent(relative)
        published = False
        try:
            try:
                verified_payload = self._read_file(parent_fd, filename)
            except FileNotFoundError:
                verified_payload = None
            if verified_payload is not None:
                if not self._parent_is_stable(parent_fd, relative[:-1]):
                    raise OSError("library path changed during persistence")
                if verified_payload != payload:
                    raise FileExistsError(
                        f"refusing to overwrite canonical output: {record['location']}"
                    )
            else:
                temporary_name = f".{filename}.{secrets.token_hex(16)}"
                descriptor = os.open(
                    temporary_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=parent_fd,
                )
                try:
                    handle = os.fdopen(descriptor, "wb")
                    descriptor = -1
                    with handle:
                        handle.write(payload)
                        handle.flush()
                        os.fsync(handle.fileno())
                    try:
                        os.link(
                            temporary_name,
                            filename,
                            src_dir_fd=parent_fd,
                            dst_dir_fd=parent_fd,
                            follow_symlinks=False,
                        )
                        published = True
                        os.fsync(parent_fd)
                    except FileExistsError:
                        pass
                finally:
                    if descriptor >= 0:
                        os.close(descriptor)
                    try:
                        os.unlink(temporary_name, dir_fd=parent_fd)
                    except FileNotFoundError:
                        pass

                if not self._parent_is_stable(parent_fd, relative[:-1]):
                    if published:
                        os.unlink(filename, dir_fd=parent_fd)
                        os.fsync(parent_fd)
                    raise OSError("library path changed during persistence")

                verified_payload = self._read_file(parent_fd, filename)
                if verified_payload != payload:
                    if published:
                        os.unlink(filename, dir_fd=parent_fd)
                        os.fsync(parent_fd)
                    raise FileExistsError(
                        f"refusing to overwrite canonical output: {record['location']}"
                    )
        finally:
            os.close(parent_fd)

        checksum = hashlib.sha256(verified_payload).hexdigest()
        receipt = PersistenceReceipt(
            adapter="filesystem",
            location=record["location"],
            checksum=f"sha256:{checksum}",
            bytes_written=len(verified_payload),
            verified_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        return confirm_library_save(deepcopy(record), receipt)
