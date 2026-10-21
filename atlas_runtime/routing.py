"""One routing policy for native capabilities and specialist domain methods."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
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


def build_routing_preview(
    text: str,
    *,
    task_classes: Iterable[str],
    taxonomy_route: Mapping[str, Any],
    surface: str,
    task_id: str | None,
    plan_id: str,
    plan: Iterable[str],
    work_unit: str | None,
    domain_methods: Mapping[str, Any],
    skills: Iterable[dict[str, Any]],
    tools: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Describe proposed provider routing without activating a provider."""
    lowered = " ".join(text.lower().split())
    classes = set(task_classes)
    hierarchy = taxonomy_route.get("hierarchy") or {}
    requirements: list[str] = []
    if (
        hierarchy.get("domain") == "government-public-sector"
        and "opportunit" in lowered
        and classes & {"RESEARCH", "ANALYSIS", "DECISION", "MONITORING"}
    ):
        requirements.append("government_public_sector_opportunity_intelligence")
    if "RESEARCH" in classes and "public" in lowered:
        requirements.append("public_research")

    provider_groups = (
        ("domain-method", domain_methods.get("items", [])),
        ("skill", skills),
        ("tool", tools),
    )
    providers: list[dict[str, Any]] = []
    for requirement in requirements:
        for provider_type, records in provider_groups:
            for record in records:
                if record.get("status") not in {"active", "available"}:
                    continue
                if record.get("permission") == "denied":
                    continue
                if requirement not in record.get("capabilities", []):
                    continue
                surfaces = set(record.get("applies_to", []))
                if surfaces and f"surface.{surface}" not in surfaces:
                    continue
                prerequisites = list(record.get("requires", []))
                providers.append({
                    "id": record["id"],
                    "type": provider_type,
                    "name": record["name"],
                    "requirement": requirement,
                    "purpose": record["description"],
                    "method": (
                        f"Use {record['name']} after validating "
                        f"{', '.join(prerequisites) if prerequisites else 'its admission record'}; "
                        "return its result to the ATLAS plan for verification."
                    ),
                    "permission": record.get("permission", "read"),
                    "data_scope": (
                        "Original prompt, governed domain context, and public-source evidence only"
                        if record.get("permission", "read") == "read"
                        else "Only the resources explicitly approved for this work unit"
                    ),
                    "fallback": record.get("fallback"),
                })

    preview = {
        "status": "PROPOSED" if providers else "NOT_REQUIRED",
        "objective": text,
        "task_id": task_id,
        "plan_id": plan_id,
        "surface": surface,
        "plan": list(plan),
        "work_unit": work_unit,
        "requirements": requirements,
        "providers": providers,
        "steps": [
            {
                "stage": "ROUTING",
                "description": "Validate each proposed provider against its exact semantic requirement and prerequisites.",
            },
            {
                "stage": "EXECUTION",
                "description": "Invoke only approved providers for the active atomic work unit.",
            },
            {
                "stage": "VERIFICATION",
                "description": "Verify provider results and preserve evidence before delivery.",
            },
        ],
        "approval_prompt": (
            "Review the providers, purpose, method, permissions, data scope, and fallbacks before routing."
            if providers else None
        ),
    }
    encoded = json.dumps(preview, sort_keys=True, separators=(",", ":")).encode("utf-8")
    preview["digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
    return preview


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
    if method.get("permission") != "read":
        raise ValueError(f"domain method has invalid permission: {method_id}")
    if any(method.get(field) for field in ("owns_execution_spine", "owns_planning", "owns_approvals")):
        raise ValueError(f"domain method claims ATLAS governance ownership: {method_id}")
    if method.get("requires_domain_handoff") is not True or method.get("blocked_handoff_execution") is not True:
        raise ValueError(f"domain method must use the governed handoff: {method_id}")
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
    registry: Mapping[str, Any],
    *,
    execution_context: ExecutionContext,
    handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select a governed specialist for the current correlated work unit."""
    metadata = registry.get("registry")
    if not isinstance(metadata, Mapping) or metadata.get("type") != "domain-method":
        raise ValueError("domain method routing requires a domain-method registry")
    if metadata.get("status") != "active":
        raise LookupError("domain method registry is not active")
    methods = registry.get("items")
    if not isinstance(methods, list):
        raise ValueError("domain method registry requires an items list")
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
        "handoff_id": handoff["handoff_id"],
        "unresolved_material": deepcopy(handoff.get("unresolved_material", [])),
    }
