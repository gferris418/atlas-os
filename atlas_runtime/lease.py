"""ATLAS-governed execution leases for specialist handoffs."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .handoff import verify_domain_context_handoff

LEASE_CONTRACT_VERSION = "1.0.0"


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be RFC 3339") from error
    if moment.tzinfo is None:
        raise ValueError(f"{field} requires a timezone offset")
    return moment


def _required_handoff_identity(handoff: dict[str, Any]) -> None:
    required = {
        "handoff_id",
        "payload_sha256",
        "source_task_id",
        "source_plan_id",
        "source_work_unit_id",
        "producer",
        "consumer",
    }
    missing = sorted(required - set(handoff))
    if missing:
        raise ValueError(f"execution lease requires handoff identity: missing {missing}")
    if handoff["producer"] != "ATLAS_OS":
        raise ValueError("execution lease requires an ATLAS handoff")


def prepare_execution_lease(
    handoff: dict[str, Any],
    *,
    execution_lease_id: str,
    issued_at: str,
    lease_expires_at: str,
    supersedes_lease_id: str | None = None,
) -> dict[str, Any]:
    """Create an ATLAS control record that authorizes continued specialist execution."""
    verify_domain_context_handoff(handoff)
    _required_handoff_identity(handoff)
    if not re.fullmatch(r"LEASE-[A-Z0-9][A-Z0-9-]{2,95}", execution_lease_id):
        raise ValueError("execution lease requires a valid execution_lease_id")
    if supersedes_lease_id is not None:
        if not re.fullmatch(r"LEASE-[A-Z0-9][A-Z0-9-]{2,95}", supersedes_lease_id):
            raise ValueError("execution lease supersedes_lease_id is invalid")
        if supersedes_lease_id == execution_lease_id:
            raise ValueError("execution lease cannot supersede itself")
    issued = _parse_timestamp(issued_at, "issued_at")
    expires = _parse_timestamp(lease_expires_at, "lease_expires_at")
    if expires <= issued:
        raise ValueError("execution lease expiry must be after issue time")
    return {
        "contract_version": LEASE_CONTRACT_VERSION,
        "execution_lease_id": execution_lease_id,
        "handoff_id": handoff["handoff_id"],
        "handoff_payload_sha256": handoff["payload_sha256"],
        "source_task_id": handoff["source_task_id"],
        "source_plan_id": handoff["source_plan_id"],
        "source_work_unit_id": handoff["source_work_unit_id"],
        "producer": "ATLAS_OS",
        "consumer": handoff["consumer"],
        "issued_at": issued_at,
        "lease_expires_at": lease_expires_at,
        "supersedes_lease_id": supersedes_lease_id,
    }


def verify_execution_lease(
    lease: dict[str, Any],
    handoff: dict[str, Any],
    *,
    verified_at: str | datetime | None = None,
    expected_lease_id: str | None = None,
) -> bool:
    """Validate lease lifetime and exact correlation to one ATLAS handoff."""
    verify_domain_context_handoff(handoff)
    _required_handoff_identity(handoff)
    required = {
        "contract_version",
        "execution_lease_id",
        "handoff_id",
        "handoff_payload_sha256",
        "source_task_id",
        "source_plan_id",
        "source_work_unit_id",
        "producer",
        "consumer",
        "issued_at",
        "lease_expires_at",
        "supersedes_lease_id",
    }
    missing = sorted(required - set(lease))
    if missing:
        raise ValueError(f"execution lease integrity check failed: missing {missing}")
    if lease["contract_version"] != LEASE_CONTRACT_VERSION:
        raise ValueError("execution lease integrity check failed: contract_version")
    if not re.fullmatch(r"LEASE-[A-Z0-9][A-Z0-9-]{2,95}", str(lease["execution_lease_id"])):
        raise ValueError("execution lease integrity check failed: execution_lease_id")
    if lease["producer"] != "ATLAS_OS":
        raise ValueError("execution lease integrity check failed: producer")
    supersedes = lease["supersedes_lease_id"]
    if supersedes is not None and not re.fullmatch(r"LEASE-[A-Z0-9][A-Z0-9-]{2,95}", str(supersedes)):
        raise ValueError("execution lease integrity check failed: supersedes_lease_id")
    if expected_lease_id is not None and lease["execution_lease_id"] != expected_lease_id:
        raise ValueError("execution lease is stale or superseded")
    expected = {
        "handoff_id": handoff["handoff_id"],
        "handoff_payload_sha256": handoff["payload_sha256"],
        "source_task_id": handoff["source_task_id"],
        "source_plan_id": handoff["source_plan_id"],
        "source_work_unit_id": handoff["source_work_unit_id"],
        "consumer": handoff["consumer"],
    }
    if any(lease.get(field) != value for field, value in expected.items()):
        raise ValueError("execution lease does not belong to the active handoff")
    issued = _parse_timestamp(str(lease["issued_at"]), "issued_at")
    expires = _parse_timestamp(str(lease["lease_expires_at"]), "lease_expires_at")
    if expires <= issued:
        raise ValueError("execution lease lifetime is invalid")
    if verified_at is None:
        current = datetime.now(timezone.utc)
    elif isinstance(verified_at, datetime):
        if verified_at.tzinfo is None:
            raise ValueError("verified_at requires a timezone offset")
        current = verified_at
    else:
        current = _parse_timestamp(verified_at, "verified_at")
    if current < issued:
        raise ValueError("execution lease is not yet active")
    if current > expires:
        raise ValueError("execution lease has expired")
    return True
