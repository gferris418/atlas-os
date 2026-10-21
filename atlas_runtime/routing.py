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

_PROVIDER_TYPES = {
    "capability", "domain-method", "function", "model", "plugin", "skill", "subagent", "tool",
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
    timestamp: str | None,
    domain_methods: Mapping[str, Any],
    skills: Iterable[dict[str, Any]],
    tools: Iterable[dict[str, Any]],
    capabilities: Iterable[dict[str, Any]] = (),
    available_capabilities: Iterable[str] = (),
    domain_classification: Mapping[str, Any] | None = None,
    domain_alignment: Mapping[str, Any] | None = None,
    additional_provider_groups: Mapping[str, Iterable[dict[str, Any]]] | None = None,
    requested_requirements: Iterable[str] = (),
    intent_profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe proposed provider routing without activating a provider."""
    lowered = " ".join(text.lower().split())
    classes = set(task_classes)
    hierarchy = taxonomy_route.get("hierarchy") or {}
    requirements = [
        str(requirement).strip()
        for requirement in requested_requirements
        if str(requirement).strip()
    ]
    if (
        hierarchy.get("domain") == "government-public-sector"
        and "opportunit" in lowered
        and classes & {"RESEARCH", "ANALYSIS", "DECISION", "MONITORING"}
    ):
        requirements.append("government_public_sector_opportunity_intelligence")
    if "RESEARCH" in classes and "public" in lowered:
        requirements.append("public_research")
    if classes & {"CODING", "DEBUGGING"}:
        requirements.append("execute")
    if "EXTERNAL_ACTION" in classes:
        requirements.append("external_write")

    requirements = list(dict.fromkeys(requirements))

    built_in_provider_groups: list[tuple[str, list[dict[str, Any]]]] = [
        ("domain-method", list(domain_methods.get("items", []))),
        ("skill", list(skills)),
        ("tool", list(tools)),
        ("capability", list(capabilities)),
    ]
    host_provider_groups: list[tuple[str, list[dict[str, Any]]]] = []
    if additional_provider_groups:
        unknown_types = set(additional_provider_groups) - _PROVIDER_TYPES
        if unknown_types:
            raise ValueError(
                "unsupported provider type: " + ", ".join(sorted(unknown_types))
            )
        host_provider_groups.extend(
            (provider_type, list(records))
            for provider_type, records in additional_provider_groups.items()
        )
    provider_groups = built_in_provider_groups + host_provider_groups
    required_host_fields = {
        "id", "name", "description", "status", "authority", "permission",
        "risk_class", "version", "source", "capabilities", "requires", "data_scope",
        "conflicts_with", "fallback",
    }
    seen_provider_ids: dict[str, str] = {}
    for provider_type, records in host_provider_groups:
        for record in records:
            provider_id = str(record.get("id", ""))
            missing = required_host_fields - set(record)
            if missing:
                raise ValueError(
                    f"host provider {provider_id or '<unknown>'} lacks admission fields: "
                    + ", ".join(sorted(missing))
                )
            if record.get("authority") not in _AUTHORITY:
                raise ValueError(f"host provider has invalid authority: {provider_id}")
            if record.get("permission") not in {"read", "write"}:
                raise ValueError(f"host provider has invalid permission: {provider_id}")
            if record.get("status") not in {"active", "available"}:
                raise ValueError(f"host provider is not available: {provider_id}")
    for provider_type, records in provider_groups:
        for record in records:
            provider_id = str(record.get("id", ""))
            if not provider_id:
                raise ValueError("provider id is required")
            if provider_id in seen_provider_ids:
                raise ValueError(f"provider id is registered more than once: {provider_id}")
            seen_provider_ids[provider_id] = provider_type
    if work_unit is None:
        requirements = []
    providers: list[dict[str, Any]] = []
    for requirement in requirements:
        for provider_type, records in provider_groups:
            for record in records:
                if record.get("status") not in {"active", "available", "required"}:
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
                    "authority": record.get("authority", "model"),
                    "risk_class": record.get("risk_class", "unknown"),
                    "version": str(record.get("version", "unknown")),
                    "source": record.get("source", "unknown"),
                    "prerequisites": prerequisites,
                    "conflicts_with": list(record.get("conflicts_with", [])),
                    "unresolved_gates": [],
                    "data_scope": (
                        record.get("data_scope")
                        or "Original prompt, governed domain context, and public-source evidence only"
                        if record.get("permission", "read") == "read"
                        else record.get("data_scope")
                        or "Only the resources explicitly approved for this work unit"
                    ),
                    "fallback": record.get("fallback"),
                })

    candidate_ids = {provider["id"] for provider in providers}
    admitted_ids = set(available_capabilities)
    classification = domain_classification or {}
    alignment = domain_alignment or {}
    domain_records = {
        record["id"]: record for record in domain_methods.get("items", [])
    }
    for provider in providers:
        unresolved = [
            f"missing_prerequisite:{prerequisite}"
            for prerequisite in provider["prerequisites"]
            if prerequisite not in admitted_ids and prerequisite not in candidate_ids
        ]
        if provider["type"] == "domain-method":
            if task_id is None:
                unresolved.append("task_id:REQUIRED")
            if timestamp is None:
                unresolved.append("domain_handoff_timestamp:REQUIRED")
            if classification.get("status") == "RESEARCH_REQUIRED" or alignment.get("status") == "RESEARCH_REQUIRED":
                handoff_state = "BLOCKED"
            elif classification.get("status") == "CLASSIFIED" and alignment.get("status") in {"ALIGNED", "NOT_APPLICABLE"}:
                handoff_state = "READY"
            else:
                handoff_state = "PARTIAL"
            if handoff_state not in set(
                domain_records[provider["id"]].get("accepted_handoff_states", [])
            ):
                unresolved.append(f"domain_handoff_state:{handoff_state}")
            unresolved.extend(
                f"domain_classification:{facet}"
                for facet in classification.get("unresolved_facets", [])
            )
        provider["unresolved_gates"] = list(dict.fromkeys(unresolved))

    conflicting_provider_pairs = sorted({
        tuple(sorted((provider["id"], conflict)))
        for provider in providers
        for conflict in provider["conflicts_with"]
        if conflict in candidate_ids and conflict != provider["id"]
    })

    ordered: list[dict[str, Any]] = []
    remaining = list(providers)
    cyclic_provider_ids: list[str] = []
    while remaining:
        remaining_ids = {provider["id"] for provider in remaining}
        ready = next((
            provider for provider in remaining
            if not (set(provider["prerequisites"]) & remaining_ids)
        ), None)
        if ready is None:
            cyclic_provider_ids = sorted(remaining_ids)
            break
        ordered.append(ready)
        remaining.remove(ready)
    providers = ordered + sorted(remaining, key=lambda provider: provider["id"])
    matched_requirements = {provider["requirement"] for provider in providers}
    unmatched_requirements = [
        requirement for requirement in requirements
        if requirement not in matched_requirements
    ]
    unresolved_gates = [
        f"{provider['id']}:{gate}"
        for provider in providers
        for gate in provider["unresolved_gates"]
    ]
    unresolved_gates.extend(
        f"requirement:{requirement}:NO_ADMITTED_PROVIDER"
        for requirement in unmatched_requirements
    )
    if cyclic_provider_ids:
        unresolved_gates.append(
            "provider_dependency_cycle:" + ",".join(cyclic_provider_ids)
        )
    unresolved_gates.extend(
        "provider_conflict:" + ",".join(pair)
        for pair in conflicting_provider_pairs
    )
    missing_prerequisite_providers = sorted(
        provider["id"]
        for provider in providers
        if any(
            gate.startswith("missing_prerequisite:")
            for gate in provider["unresolved_gates"]
        )
    )

    preview = {
        "status": "PROPOSED" if requirements else "NOT_REQUIRED",
        "objective": text,
        "task_id": task_id,
        "plan_id": plan_id,
        "surface": surface,
        "plan": list(plan),
        "work_unit": work_unit,
        "requirements": requirements,
        "intent_profile": deepcopy(intent_profile or {}),
        "providers": providers,
        "unmatched_requirements": unmatched_requirements,
        "cyclic_provider_ids": cyclic_provider_ids,
        "conflicting_provider_pairs": [list(pair) for pair in conflicting_provider_pairs],
        "missing_prerequisite_providers": missing_prerequisite_providers,
        "unresolved_gates": unresolved_gates,
        "execution_sequence": [provider["id"] for provider in ordered],
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
            "Review the providers, purpose, method, permissions, data scope, prerequisites, "
            "unresolved gates, execution sequence, and fallbacks before routing."
            if requirements else None
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
