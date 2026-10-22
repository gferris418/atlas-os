"""Governed domain-context handoff between ATLAS and specialist domain methods."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

CONTRACT_VERSION = "1.3.0"
ACTIVATION_WINDOW = timedelta(hours=24)


@dataclass(frozen=True)
class ExecutionContext:
    """Identity and routing facts for one active ATLAS work unit."""

    task_id: str
    plan_id: str
    work_unit_id: str
    task_class: str
    available_capabilities: frozenset[str] = field(default_factory=frozenset)
    active_capabilities: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not re.fullmatch(r"TASK-[A-Z0-9][A-Z0-9-]{2,63}", self.task_id):
            raise ValueError("execution context requires a valid task_id")
        for field_name in ("plan_id", "work_unit_id", "task_class"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"execution context requires {field_name}")


def _parse_timestamp(value: str, field: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be RFC 3339") from error
    if moment.tzinfo is None:
        raise ValueError(f"{field} requires a timezone offset")
    return moment


def _validate_timestamp(value: str, field: str) -> None:
    _parse_timestamp(value, field)


def _source_input(task: dict[str, Any]) -> str:
    for item in task.get("inputs", []):
        if isinstance(item, dict) and item.get("type") == "user_prompt":
            return str(item.get("value", ""))
    return str(task.get("objective", ""))


def _semantic_context_for(task: dict[str, Any]) -> dict[str, Any]:
    supplied = task.get("semantic_context")
    if isinstance(supplied, dict):
        return deepcopy(supplied)
    original = _source_input(task)
    normalized = " ".join(original.split())
    classification = task.get("domain_classification") or {}
    return {
        "status": "READY",
        "original_input": original,
        "normalized_input": normalized,
        "whole_context_summary": normalized or None,
        "normalization_notes": [],
        "meaning_ambiguities": [],
        "unresolved_context": list(dict.fromkeys(classification.get("unresolved_facets", []))),
    }


def _state_for(semantic_context: dict[str, Any]) -> str:
    return "BLOCKED" if semantic_context.get("status") == "AMBIGUOUS" else "READY"


def _unresolved_material(
    semantic_context: dict[str, Any], classification: dict[str, Any]
) -> list[str]:
    return list(dict.fromkeys([
        *semantic_context.get("unresolved_context", []),
        *classification.get("unresolved_facets", []),
    ]))


def _digest_payload(handoff: dict[str, Any]) -> str:
    payload = {key: value for key, value in handoff.items() if key != "payload_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prepare_domain_context_handoff(
    task: dict[str, Any], *, execution_context: ExecutionContext,
    consumer: str, handoff_id: str, created_at: str,
) -> dict[str, Any]:
    """Create an immutable whole-context snapshot for an authorized specialist.

    Semantic clarity controls handoff readiness. Downstream unknowns are preserved
    rather than converted into blocking state.
    """
    if not str(task.get("id", "")).strip():
        raise ValueError("domain handoff requires source task id")
    if task["id"] != execution_context.task_id:
        raise ValueError("domain handoff task does not match execution context")
    if "domain_classification" not in task:
        raise ValueError("domain handoff requires domain_classification")
    if "domain_alignment" not in task:
        raise ValueError("domain handoff requires domain_alignment")
    if not consumer.strip():
        raise ValueError("domain handoff requires consumer")
    if not handoff_id.strip():
        raise ValueError("domain handoff requires handoff_id")
    created = _parse_timestamp(created_at, "created_at")

    semantic_context = _semantic_context_for(task)
    classification = deepcopy(task["domain_classification"])
    alignment = deepcopy(task["domain_alignment"])
    handoff = {
        "contract_version": CONTRACT_VERSION,
        "handoff_id": handoff_id,
        "source_task_id": task["id"],
        "source_plan_id": execution_context.plan_id,
        "source_work_unit_id": execution_context.work_unit_id,
        "producer": "ATLAS_OS",
        "consumer": consumer,
        "created_at": created_at,
        "activation_expires_at": (created + ACTIVATION_WINDOW).isoformat(),
        "state": _state_for(semantic_context),
        "semantic_context": semantic_context,
        "domain_classification": classification,
        "domain_alignment": alignment,
        "unresolved_material": _unresolved_material(semantic_context, classification),
        "risk_flags": deepcopy(classification.get("risk_flags", [])),
    }
    handoff["payload_sha256"] = _digest_payload(handoff)
    return handoff


def verify_domain_context_handoff(handoff: dict[str, Any]) -> bool:
    """Reject mutation, stale correlation metadata, or internally inconsistent copies."""
    required = {
        "contract_version", "handoff_id", "source_task_id", "source_plan_id",
        "source_work_unit_id", "producer", "consumer", "created_at",
        "activation_expires_at", "state", "semantic_context", "domain_classification",
        "domain_alignment", "unresolved_material", "risk_flags", "payload_sha256",
    }
    missing = sorted(required - set(handoff))
    if missing:
        raise ValueError(f"domain handoff integrity check failed: missing {missing}")
    if handoff["contract_version"] != CONTRACT_VERSION:
        raise ValueError("domain handoff integrity check failed: contract_version")
    if handoff["producer"] != "ATLAS_OS":
        raise ValueError("domain handoff integrity check failed: producer")
    created = _parse_timestamp(handoff["created_at"], "created_at")
    activation_expires = _parse_timestamp(handoff["activation_expires_at"], "activation_expires_at")
    if activation_expires - created != ACTIVATION_WINDOW:
        raise ValueError("domain handoff integrity check failed: activation_expires_at")
    semantic_context = handoff["semantic_context"]
    classification = handoff["domain_classification"]
    if handoff["unresolved_material"] != _unresolved_material(semantic_context, classification):
        raise ValueError("domain handoff integrity check failed: unresolved_material")
    if handoff["risk_flags"] != classification.get("risk_flags", []):
        raise ValueError("domain handoff integrity check failed: risk_flags")
    if handoff["state"] != _state_for(semantic_context):
        raise ValueError("domain handoff integrity check failed: state")
    if handoff["payload_sha256"] != _digest_payload(handoff):
        raise ValueError("domain handoff integrity check failed: payload_sha256")
    return True


def execution_context_mismatches(
    handoff: dict[str, Any], execution_context: ExecutionContext,
) -> list[str]:
    """Return identity fields that do not belong to the active work unit."""
    expected = {
        "task_id": (handoff.get("source_task_id"), execution_context.task_id),
        "plan_id": (handoff.get("source_plan_id"), execution_context.plan_id),
        "work_unit_id": (handoff.get("source_work_unit_id"), execution_context.work_unit_id),
    }
    return [name for name, (observed, current) in expected.items() if observed != current]


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
