"""Governed domain-context handoff between ATLAS and specialist domain methods."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime
from typing import Any, Iterable

CONTRACT_VERSION = "1.0.0"


def _validate_timestamp(value: str, field: str) -> None:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be RFC 3339") from error
    if moment.tzinfo is None:
        raise ValueError(f"{field} requires a timezone offset")


def _state_for(classification: dict[str, Any], alignment: dict[str, Any]) -> str:
    if classification.get("status") == "RESEARCH_REQUIRED" or alignment.get("status") == "RESEARCH_REQUIRED":
        return "BLOCKED"
    if classification.get("status") == "CLASSIFIED" and alignment.get("status") in {"ALIGNED", "NOT_APPLICABLE"}:
        return "READY"
    return "PARTIAL"


def _digest_payload(handoff: dict[str, Any]) -> str:
    payload = {key: value for key, value in handoff.items() if key != "payload_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prepare_domain_context_handoff(
    task: dict[str, Any], *, consumer: str, handoff_id: str, created_at: str
) -> dict[str, Any]:
    """Create an immutable snapshot of ATLAS-owned domain context for a specialist.

    The specialist may enrich this context for its domain purpose but must not
    silently redefine the ATLAS classification or framework-alignment snapshot.
    """
    if not str(task.get("id", "")).strip():
        raise ValueError("domain handoff requires source task id")
    if "domain_classification" not in task:
        raise ValueError("domain handoff requires domain_classification")
    if "domain_alignment" not in task:
        raise ValueError("domain handoff requires domain_alignment")
    if not consumer.strip():
        raise ValueError("domain handoff requires consumer")
    if not handoff_id.strip():
        raise ValueError("domain handoff requires handoff_id")
    _validate_timestamp(created_at, "created_at")

    classification = deepcopy(task["domain_classification"])
    alignment = deepcopy(task["domain_alignment"])
    handoff = {
        "contract_version": CONTRACT_VERSION,
        "handoff_id": handoff_id,
        "source_task_id": task["id"],
        "producer": "ATLAS_OS",
        "consumer": consumer,
        "created_at": created_at,
        "state": _state_for(classification, alignment),
        "domain_classification": classification,
        "domain_alignment": alignment,
        "unresolved_material": deepcopy(classification.get("unresolved_facets", [])),
        "risk_flags": deepcopy(classification.get("risk_flags", [])),
    }
    handoff["payload_sha256"] = _digest_payload(handoff)
    return handoff


def verify_domain_context_handoff(handoff: dict[str, Any]) -> bool:
    """Reject mutation, stale correlation metadata, or internally inconsistent copies."""
    required = {
        "contract_version", "handoff_id", "source_task_id", "producer", "consumer",
        "created_at", "state", "domain_classification", "domain_alignment",
        "unresolved_material", "risk_flags", "payload_sha256",
    }
    missing = sorted(required - set(handoff))
    if missing:
        raise ValueError(f"domain handoff integrity check failed: missing {missing}")
    if handoff["contract_version"] != CONTRACT_VERSION:
        raise ValueError("domain handoff integrity check failed: contract_version")
    if handoff["producer"] != "ATLAS_OS":
        raise ValueError("domain handoff integrity check failed: producer")
    _validate_timestamp(handoff["created_at"], "created_at")
    classification = handoff["domain_classification"]
    alignment = handoff["domain_alignment"]
    if handoff["unresolved_material"] != classification.get("unresolved_facets", []):
        raise ValueError("domain handoff integrity check failed: unresolved_material")
    if handoff["risk_flags"] != classification.get("risk_flags", []):
        raise ValueError("domain handoff integrity check failed: risk_flags")
    if handoff["state"] != _state_for(classification, alignment):
        raise ValueError("domain handoff integrity check failed: state")
    if handoff["payload_sha256"] != _digest_payload(handoff):
        raise ValueError("domain handoff integrity check failed: payload_sha256")
    return True


def verify_domain_handoff_receipt(handoff: dict[str, Any], receipt: dict[str, Any]) -> bool:
    """Require exact return correlation before ATLAS accepts a specialist result."""
    verify_domain_context_handoff(handoff)
    for field in ("contract_version", "handoff_id", "payload_sha256", "consumer"):
        if receipt.get(field) != handoff.get(field):
            raise ValueError(f"domain handoff receipt mismatch: {field}")
    if receipt.get("status") != "ACCEPTED":
        raise ValueError("domain handoff receipt must be ACCEPTED")
    _validate_timestamp(str(receipt.get("received_at", "")), "received_at")
    return True


def route_domain_method(
    requirement: str,
    methods: Iterable[dict[str, Any]],
    *,
    handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select a specialist only from an explicit structured capability requirement.

    Raw prompt keywords are deliberately outside this seam. Classification and
    planning establish the capability requirement first; this router then applies
    the registered handoff and ownership controls.
    """
    candidates = [
        method
        for method in methods
        if method.get("status") in {"active", "available"}
        and requirement in method.get("capabilities", [])
    ]
    candidates.sort(key=lambda method: (-method.get("priority", 0), method.get("id", "")))
    if not candidates:
        raise LookupError(f"no available domain method satisfies {requirement}")

    method = candidates[0]
    method_id = method.get("id")
    if method.get("activation_authority") != "ATLAS_OS":
        raise ValueError(f"domain method has invalid activation authority: {method_id}")
    if any(method.get(field) for field in ("owns_execution_spine", "owns_planning", "owns_approvals")):
        raise ValueError(f"domain method claims ATLAS governance ownership: {method_id}")
    if method.get("requires_domain_handoff", False) and not method.get("blocked_handoff_execution", False):
        raise ValueError(f"domain method does not reject BLOCKED handoffs: {method_id}")

    if method.get("requires_domain_handoff", False):
        if handoff is None:
            return {"status": "BLOCKED", "reason": "HANDOFF_REQUIRED", "method_id": method_id}
        verify_domain_context_handoff(handoff)
        if handoff.get("consumer") != method.get("consumer_id"):
            return {"status": "BLOCKED", "reason": "HANDOFF_CONSUMER_MISMATCH", "method_id": method_id}
        if handoff.get("state") == "BLOCKED" or handoff.get("state") not in method.get("accepted_handoff_states", []):
            return {"status": "BLOCKED", "reason": "HANDOFF_STATE_NOT_ACCEPTED", "method_id": method_id}

    return {
        "status": "ACTIVATE",
        "method_id": method_id,
        "requirement": requirement,
        "handoff_id": handoff.get("handoff_id") if handoff else None,
        "unresolved_material": deepcopy(handoff.get("unresolved_material", [])) if handoff else [],
    }
