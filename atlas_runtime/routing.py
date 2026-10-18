"""One routing policy for native capabilities and specialist domain methods."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Iterable

from .handoff import (
    ExecutionContext,
    execution_context_mismatches,
    verify_domain_context_handoff,
)

_AUTHORITY = {
    "user": 7,
    "connected": 6,
    "specialist-contract": 5,
    "official": 4,
    "canonical": 3,
    "secondary": 2,
    "community": 1,
    "model": 0,
}


def _eligible(
    requirement: str,
    item: dict[str, Any],
    *,
    execution_context: ExecutionContext | None,
    allowed_statuses: set[str] | None = None,
) -> bool:
    if allowed_statuses is not None and item.get("status") not in allowed_statuses:
        return False
    if item.get("available", True) is False:
        return False
    if requirement not in item.get("capabilities", []):
        return False
    if item.get("permission", "read") == "denied":
        return False
    if execution_context is None:
        return not item.get("requires") and not item.get("conflicts_with")
    if item.get("task_classes") and execution_context.task_class not in item["task_classes"]:
        return False
    if not set(item.get("requires", [])).issubset(execution_context.available_capabilities):
        return False
    if set(item.get("conflicts_with", [])) & execution_context.active_capabilities:
        return False
    return True


def route_capability(
    requirement: str,
    capabilities: Iterable[dict[str, Any]],
    *,
    execution_context: ExecutionContext | None = None,
) -> dict[str, Any]:
    candidates = [
        item for item in capabilities
        if _eligible(requirement, item, execution_context=execution_context)
    ]
    if not candidates:
        raise LookupError(f"no available capability satisfies {requirement}")
    return max(candidates, key=lambda item: (
        _AUTHORITY.get(item.get("authority", "model"), -1),
        -item.get("risk", 0),
        -item.get("latency", 0),
        item["id"],
    ))


def _validate_domain_method(method: dict[str, Any]) -> None:
    method_id = method.get("id")
    if method.get("activation_authority") != "ATLAS_OS":
        raise ValueError(f"domain method has invalid activation authority: {method_id}")
    if any(method.get(field) for field in ("owns_execution_spine", "owns_planning", "owns_approvals")):
        raise ValueError(f"domain method claims ATLAS governance ownership: {method_id}")
    if method.get("requires_domain_handoff") and not method.get("blocked_handoff_execution"):
        raise ValueError(f"domain method does not reject BLOCKED handoffs: {method_id}")
    source_commit = str(method.get("source_commit", ""))
    contract_sha256 = str(method.get("contract_sha256", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError(f"domain method lacks immutable source commit: {method_id}")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", contract_sha256):
        raise ValueError(f"domain method lacks contract digest: {method_id}")
    if source_commit not in str(method.get("source", "")):
        raise ValueError(f"domain method source is not commit-pinned: {method_id}")


def route_domain_method(
    requirement: str,
    methods: Iterable[dict[str, Any]],
    *,
    execution_context: ExecutionContext,
    handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select a governed specialist for the current correlated work unit."""
    candidates = [
        method for method in methods
        if _eligible(
            requirement,
            method,
            execution_context=execution_context,
            allowed_statuses={"active", "available"},
        )
    ]
    candidates.sort(key=lambda method: (
        -method.get("priority", 0),
        -_AUTHORITY.get(method.get("authority", "model"), -1),
        method.get("id", ""),
    ))
    if not candidates:
        raise LookupError(f"no available domain method satisfies {requirement}")

    method = candidates[0]
    method_id = method.get("id")
    _validate_domain_method(method)

    if method.get("requires_domain_handoff"):
        if handoff is None:
            return {"status": "BLOCKED", "reason": "HANDOFF_REQUIRED", "method_id": method_id}
        verify_domain_context_handoff(handoff)
        mismatches = execution_context_mismatches(handoff, execution_context)
        if mismatches:
            return {
                "status": "BLOCKED",
                "reason": "HANDOFF_EXECUTION_CONTEXT_MISMATCH",
                "method_id": method_id,
                "mismatches": mismatches,
            }
        if handoff.get("consumer") != method.get("consumer_id"):
            return {"status": "BLOCKED", "reason": "HANDOFF_CONSUMER_MISMATCH", "method_id": method_id}
        if handoff.get("state") == "BLOCKED" or handoff.get("state") not in method.get("accepted_handoff_states", []):
            return {"status": "BLOCKED", "reason": "HANDOFF_STATE_NOT_ACCEPTED", "method_id": method_id}

    return {
        "status": "ACTIVATE",
        "method_id": method_id,
        "requirement": requirement,
        "task_id": execution_context.task_id,
        "plan_id": execution_context.plan_id,
        "work_unit_id": execution_context.work_unit_id,
        "handoff_id": handoff.get("handoff_id") if handoff else None,
        "unresolved_material": deepcopy(handoff.get("unresolved_material", [])) if handoff else [],
    }
