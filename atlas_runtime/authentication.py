"""Detached ATLAS control-plane attestations for cross-system records."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
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


def verify_control_record_attestation(
    record: Mapping[str, Any],
    attestation: Mapping[str, Any],
    *,
    trusted_public_keys: Mapping[str, bytes],
) -> bool:
    """Verify record integrity and ATLAS provenance against pinned public keys."""
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
