"""Detached ATLAS control-plane attestations for cross-system records."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def _canonical_record(record: Mapping[str, Any]) -> bytes:
    return json.dumps(
        record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be RFC 3339") from error
    if moment.tzinfo is None:
        raise ValueError(f"{field} requires a timezone offset")
    return moment


def canonical_record_sha256(record: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical_record(record)).hexdigest()


def attest_control_record(
    record: Mapping[str, Any], *, key_id: str, private_key: bytes
) -> dict[str, str]:
    """Sign a complete control record with an operator-managed Ed25519 key."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", key_id):
        raise ValueError("attestation requires a valid key_id")
    try:
        signer = Ed25519PrivateKey.from_private_bytes(private_key)
    except ValueError as error:
        raise ValueError("attestation requires a 32-byte Ed25519 private key") from error
    payload = _canonical_record(record)
    return {
        "version": "1",
        "issuer": "ATLAS_OS",
        "algorithm": "Ed25519",
        "key_id": key_id,
        "record_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "signature": base64.b64encode(signer.sign(payload)).decode("ascii"),
    }


def resolve_trusted_public_key(
    registry: Mapping[str, Any],
    *,
    key_id: str,
    record_class: str,
    verified_at: str | datetime | None = None,
) -> bytes:
    """Resolve one lifecycle-governed ATLAS public key or fail closed."""
    if registry.get("registry_version") != "1.0.0" or registry.get("issuer") != "ATLAS_OS":
        raise ValueError("unsupported ATLAS signing-key registry")
    keys = registry.get("keys")
    if not isinstance(keys, list):
        raise ValueError("ATLAS signing-key registry requires keys")
    matches = [entry for entry in keys if isinstance(entry, Mapping) and entry.get("key_id") == key_id]
    if len(matches) != 1:
        raise ValueError("ATLAS attestation key is not trusted")
    entry = matches[0]
    if entry.get("algorithm") != "Ed25519" or entry.get("issuer") != "ATLAS_OS":
        raise ValueError("unsupported ATLAS signing key")
    if entry.get("status") != "ACTIVE":
        raise ValueError("ATLAS signing key is not active")
    allowed = entry.get("allowed_record_classes")
    if not isinstance(allowed, list) or record_class not in allowed:
        raise ValueError("ATLAS signing key is out of scope for record class")
    activated_at = _parse_timestamp(str(entry.get("activated_at", "")), "activated_at")
    expires_at = _parse_timestamp(str(entry.get("expires_at", "")), "expires_at")
    if expires_at <= activated_at:
        raise ValueError("ATLAS signing key lifecycle is invalid")
    if verified_at is None:
        current = datetime.now(timezone.utc)
    elif isinstance(verified_at, datetime):
        if verified_at.tzinfo is None:
            raise ValueError("verified_at requires a timezone offset")
        current = verified_at
    else:
        current = _parse_timestamp(verified_at, "verified_at")
    if current < activated_at:
        raise ValueError("ATLAS signing key is not yet active")
    if current > expires_at:
        raise ValueError("ATLAS signing key has expired")
    try:
        public_key = base64.b64decode(str(entry.get("public_key_base64", "")), validate=True)
        Ed25519PublicKey.from_public_bytes(public_key)
    except (ValueError, TypeError) as error:
        raise ValueError("ATLAS signing key material is invalid") from error
    return public_key


def verify_control_record_attestation(
    record: Mapping[str, Any],
    attestation: Mapping[str, Any],
    *,
    trusted_public_keys: Mapping[str, bytes],
) -> bool:
    """Verify record integrity and ATLAS provenance against pinned public keys.

    This legacy compatibility path verifies cryptographic pinning only. Production
    consumers should use ``verify_control_record_attestation_with_registry`` so
    key activation, expiry, revocation and record-class scope are enforced.
    """
    expected_fields = {
        "version", "issuer", "algorithm", "key_id", "record_sha256", "signature"
    }
    if set(attestation) != expected_fields:
        raise ValueError("invalid ATLAS attestation shape")
    if (
        attestation.get("version") != "1"
        or attestation.get("issuer") != "ATLAS_OS"
        or attestation.get("algorithm") != "Ed25519"
    ):
        raise ValueError("unsupported ATLAS attestation")
    key_id = str(attestation.get("key_id", ""))
    public_key_bytes = trusted_public_keys.get(key_id)
    if public_key_bytes is None:
        raise ValueError("ATLAS attestation key is not trusted")
    payload = _canonical_record(record)
    if attestation.get("record_sha256") != "sha256:" + hashlib.sha256(payload).hexdigest():
        raise ValueError("ATLAS attestation digest mismatch")
    try:
        signature = base64.b64decode(str(attestation["signature"]), validate=True)
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature, payload)
    except (KeyError, ValueError, InvalidSignature) as error:
        raise ValueError("ATLAS attestation signature invalid") from error
    return True


def verify_control_record_attestation_with_registry(
    record: Mapping[str, Any],
    attestation: Mapping[str, Any],
    *,
    trusted_key_registry: Mapping[str, Any],
    record_class: str,
    verified_at: str | datetime | None = None,
) -> bool:
    """Verify an ATLAS attestation using lifecycle-governed trust metadata."""
    key_id = str(attestation.get("key_id", ""))
    public_key = resolve_trusted_public_key(
        trusted_key_registry,
        key_id=key_id,
        record_class=record_class,
        verified_at=verified_at,
    )
    return verify_control_record_attestation(
        record,
        attestation,
        trusted_public_keys={key_id: public_key},
    )
