"""Small public execution interface over the ATLAS governance primitives."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Iterable, Mapping

import yaml

from .capabilities import plan_canonical_capabilities
from .collection import build_collection_mission
from .handoff import ExecutionContext, prepare_domain_context_handoff
from .routing import build_routing_preview, route_capability, route_domain_method
from .runtime import (
    align_domain_practices,
    assess_completeness,
    audit_capability_providers,
    build_plan,
    classify_domain_context,
    classify_task,
    classify_task_intent,
    create_dashboard,
    normalize_intent,
    route_taxonomy_layer,
    select_next_work_unit,
)
from .surfaces import validate_surface_id
from .triage import triage_request


DOMAIN_CONTEXT_TERMS = (
    "compliance",
    "standard",
    "regulation",
    "regulatory",
    " law",
    "legal",
    "export control",
    "classification",
    "taxonomy",
    "safety",
    "defense",
    "defence",
    "navy",
    "radar",
    "medical",
    "cybersecurity",
)

_ARGUS_COLLECTION_MODES = {"ARGUS_COLLECTION", "HYBRID"}
_LEGACY_INTELLIGENCE_REQUIREMENTS = {
    "intelligence_analysis",
    "government_public_sector_opportunity_intelligence",
}


@dataclass(frozen=True)
class ExecutionEnvelope:
    """The minimum context required to begin one governed ATLAS execution."""

    objective: str
    plan_id: str
    work_units: Iterable[dict[str, Any]]
    surface: str = "core"
    clarification_status: str = "NOT_REQUIRED"
    task_id: str | None = None
    capability_requirements: Iterable[str] = ()
    provider_inventory: Mapping[str, Iterable[dict[str, Any]]] | None = None
    routing_approval_status: str = "PENDING"
    routing_preview_digest: str | None = None
    timestamp: str | None = None
    timezone_name: str = "UTC"

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("execution objective is required")
        if not self.plan_id.strip():
            raise ValueError("execution plan_id is required")
        validate_surface_id(self.surface)
        work_units = tuple(deepcopy(list(self.work_units)))
        if not work_units:
            raise ValueError("execution requires at least one work unit")
        if self.routing_approval_status not in {"PENDING", "APPROVED", "REJECTED"}:
            raise ValueError("invalid routing approval status")
        requirements = tuple(dict.fromkeys(
            requirement.strip()
            for requirement in self.capability_requirements
            if requirement.strip()
        ))
        provider_inventory = {
            str(provider_type): tuple(deepcopy(list(records)))
            for provider_type, records in (self.provider_inventory or {}).items()
        }
        object.__setattr__(self, "work_units", work_units)
        object.__setattr__(self, "capability_requirements", requirements)
        object.__setattr__(self, "provider_inventory", provider_inventory)


@dataclass(frozen=True)
class ExecutionResult:
    """One state-derived view of the current ATLAS execution."""

    state: str
    request_route: str
    request_triage: dict[str, Any]
    normalized_intent: str
    semantic_context: dict[str, Any]
    task_classes: tuple[str, ...]
    plan: tuple[str, ...]
    active_unit: str | None
    dashboard: dict[str, Any]
    taxonomy_route: dict[str, Any]
    completeness: dict[str, Any]
    domain_classification: dict[str, Any]
    domain_alignment: dict[str, Any]
    capability_audit: dict[str, Any]
    capability_plan: dict[str, Any]
    intent_profile: dict[str, Any]
    behavioral_learning_state: dict[str, Any]
    routing_preview: dict[str, Any]
    routing_decisions: tuple[dict[str, Any], ...]
    execution_trace: tuple[str, ...]

    @property
    def compact_status(self) -> str:
        dashboard = self.dashboard
        library = dashboard["library"]
        return "\n".join((
            f"ATLAS/{dashboard['surface']} {dashboard['progress_visual']} | {dashboard['timestamp']} | "
            f"{dashboard['duration_ms']} ms | Goal {dashboard['goal']} | "
            f"Task {dashboard['completed_units']}/{dashboard['total_units']} · {dashboard['active_stage']}: {dashboard['task']}",
            f"Input {dashboard['input_summary']} | Processing {dashboard['processing_summary']} | "
            f"Output {dashboard['output_summary']}",
            f"Playbook {dashboard['playbook']} | Framework {', '.join(dashboard['frameworks'])} | "
            f"SOP {dashboard['sop']}",
            f"Plan {dashboard['plan_id']}:{dashboard['plan_status']} | State {self.state} | "
            f"Quality {dashboard['quality_gate']} | Library {library['status']} | "
            f"Blocker {dashboard['blocker_or_approval']}",
        ))


def _needs_direct_domain_context(text: str) -> bool:
    lowered = f" {' '.join(text.lower().split())} "
    return any(term in lowered for term in DOMAIN_CONTEXT_TERMS)


def _deferred_taxonomy_route() -> dict[str, Any]:
    return {
        "status": "UNRESOLVED",
        "route_id": None,
        "hierarchy": None,
        "candidate_taxonomies": [],
        "required_facets": [],
        "material_dimensions": [],
    }


def _partial_intelligence_classification() -> dict[str, Any]:
    return {
        "status": "PARTIAL",
        "classification_sequence": [],
        "facets": {},
        "taxonomy_references": [],
        "risk_flags": [],
        "unresolved_facets": ["intelligence-domain-context"],
        "conditional_candidates": [],
        "evidence": [],
        "next_action": "ARGUS enriches non-sensitive collection context after governed activation.",
    }


def _partial_intelligence_alignment() -> dict[str, Any]:
    return {
        "domain": "intelligence",
        "status": "PARTIAL",
        "frameworks": [],
        "compliance": "NOT_ASSESSED",
        "deviations": [],
        "next_action": "ARGUS may enrich collection evidence; ATLAS retains canonical framework authority.",
    }


def _semantic_context(
    original: str,
    normalized: str,
    domain_classification: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the fast whole-context snapshot used for specialist handoff.

    The runtime does not convert downstream research gaps into semantic ambiguity.
    Explicit material clarification remains a separate control-plane concern.
    """
    notes = [] if original.strip() == normalized else [
        "Whitespace and surface form normalized without changing intended meaning."
    ]
    return {
        "status": "READY",
        "original_input": original,
        "normalized_input": normalized,
        "whole_context_summary": normalized,
        "normalization_notes": notes,
        "meaning_ambiguities": [],
        "unresolved_context": list(dict.fromkeys(domain_classification.get("unresolved_facets", []))),
    }


def execute(envelope: ExecutionEnvelope) -> ExecutionResult:
    """Compile current ATLAS state through one stable public interface.

    ATLAS reads and normalizes the whole context first, then performs only the
    high-confidence classification and framing needed for reliable downstream
    work. Structured collection activates ARGUS through the Collection-Need Gate,
    bounded collection mission, governed whole-context handoff, and approved
    provider preview. Downstream unknowns remain visible but do not become normal
    semantic blockers.
    """

    started = perf_counter_ns()
    work_units = deepcopy(list(envelope.work_units))
    repository_root = Path(__file__).resolve().parents[1]

    def registry_payload(name: str) -> dict[str, Any]:
        path = repository_root / "registries" / f"{name}.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def registry_items(name: str) -> list[dict[str, Any]]:
        return list(registry_payload(name)["items"])

    normalized = normalize_intent(envelope.objective)["normalized"]
    task_classes = tuple(classify_task(normalized))
    request_triage = triage_request(normalized, task_classes=task_classes)
    capability_plan = plan_canonical_capabilities(
        envelope.objective,
        task_classes=task_classes,
        collection_mode=request_triage["collection_mode"],
        collection_types=request_triage["collection_types"],
    )
    collection_route = request_triage["collection_mode"] in _ARGUS_COLLECTION_MODES
    intelligence_route = request_triage["route"] == "INTELLIGENCE"
    material_domain_context = _needs_direct_domain_context(normalized)

    taxonomies = registry_items("taxonomies")
    taxonomy_route = _deferred_taxonomy_route()
    if material_domain_context:
        taxonomy_route = route_taxonomy_layer(
            envelope.objective,
            registry_items("taxonomy-routes"),
            taxonomies,
        )

    intent_profile = classify_task_intent(
        normalized,
        task_classes=task_classes,
        taxonomy_route=taxonomy_route,
    )
    candidate_requirements = list(intent_profile["candidate_requirements"])
    if collection_route:
        candidate_requirements = [
            requirement for requirement in candidate_requirements
            if requirement not in _LEGACY_INTELLIGENCE_REQUIREMENTS
        ]
    intent_profile = {
        **intent_profile,
        "candidate_requirements": candidate_requirements,
        "request_route": request_triage["route"],
        "intelligence_types": list(request_triage["intelligence_types"]),
        "collection_mode": request_triage["collection_mode"],
        "collection_required": request_triage["collection_required"],
        "collection_types": list(request_triage["collection_types"]),
        "collection_depth": request_triage["collection_depth"],
    }
    behavioral_learning_state = {
        "mode": "DISABLED",
        "persistence": "NOT_AUTHORIZED",
        "applied_preferences": [],
        "proposed_updates": [],
    }

    if material_domain_context:
        substantive = taxonomy_route["status"] == "ROUTED"
        material_dimensions = taxonomy_route["material_dimensions"] or ["what"]
        completeness = assess_completeness({
            "what": normalized,
            "material_dimensions": material_dimensions,
        })
        domain_classification = classify_domain_context(
            normalized,
            registry_items("classifications"),
            taxonomies=taxonomies,
            substantive=substantive,
            required_facets=taxonomy_route["required_facets"] if substantive else (),
        )
        domain_name = (
            taxonomy_route["hierarchy"]["sub_domain"]
            if taxonomy_route["hierarchy"] else "general"
        )
        domain_alignment = align_domain_practices(
            domain_name,
            registry_items("frameworks"),
            substantive=substantive,
        )
        # Collection-bound work carries unresolved classification/framework context
        # forward rather than forcing a research loop inside ATLAS.
        if collection_route and envelope.clarification_status in {"RESOLVED", "NOT_REQUIRED"}:
            if domain_classification.get("status") == "RESEARCH_REQUIRED":
                domain_classification = {
                    **domain_classification,
                    "status": "PARTIAL",
                    "next_action": "Carry unresolved context into the bounded collection mission.",
                }
            if domain_alignment.get("status") == "RESEARCH_REQUIRED":
                domain_alignment = {
                    **domain_alignment,
                    "status": "PARTIAL",
                    "next_action": "Carry unresolved framework applicability downstream without transferring ATLAS authority.",
                }
    elif intelligence_route:
        substantive = False
        completeness = assess_completeness({
            "what": normalized,
            "material_dimensions": ["what"],
        })
        domain_classification = _partial_intelligence_classification()
        domain_alignment = _partial_intelligence_alignment()
    else:
        substantive = False
        completeness = assess_completeness({
            "what": normalized,
            "material_dimensions": ["what"],
        })
        domain_classification = classify_domain_context(
            normalized,
            registry_items("classifications"),
            taxonomies=taxonomies,
            substantive=False,
            required_facets=(),
        )
        domain_alignment = align_domain_practices(
            "general",
            registry_items("frameworks"),
            substantive=False,
        )

    semantic_context = _semantic_context(
        envelope.objective,
        normalized,
        domain_classification,
    )

    collection_mission: dict[str, Any] | None = None
    if collection_route and envelope.task_id is not None:
        collection_mission = build_collection_mission(
            envelope.objective,
            task_id=envelope.task_id,
            plan_id=envelope.plan_id,
            request_triage=request_triage,
            risk_flags=domain_classification.get("risk_flags", []),
        )

    plan = tuple(build_plan(work_units))
    capability_audit = audit_capability_providers(registry_items("capabilities"))
    preview_active_unit = select_next_work_unit(
        work_units,
        plan_id=envelope.plan_id,
        plan_status="READY",
        clarification_status="RESOLVED",
    )
    routing_preview = build_routing_preview(
        normalized,
        task_classes=task_classes,
        taxonomy_route=taxonomy_route,
        surface=envelope.surface,
        task_id=envelope.task_id,
        plan_id=envelope.plan_id,
        plan=plan,
        work_unit=preview_active_unit,
        timestamp=envelope.timestamp,
        domain_methods=registry_payload("domain-methods"),
        skills=registry_items("skills"),
        tools=registry_items("tools"),
        capabilities=registry_items("capabilities"),
        available_capabilities=capability_audit["admitted"],
        domain_classification=domain_classification,
        domain_alignment=domain_alignment,
        additional_provider_groups=envelope.provider_inventory,
        requested_requirements=(
            *envelope.capability_requirements,
            *request_triage["capability_requirements"],
            *intent_profile["candidate_requirements"],
        ),
        intent_profile=intent_profile,
        collection_mission=collection_mission,
    )
    blocking_stage: str | None = None
    blocker: str | None = None
    routing_decisions: list[dict[str, Any]] = []
    candidate_active_unit: str | None = None

    # Classification completeness and framework applicability are informational at
    # this seam. Only an explicit unresolved material clarification blocks routing.
    if (
        routing_preview["status"] == "PROPOSED"
        and envelope.clarification_status == "PENDING"
    ):
        blocking_stage = "MATERIAL_CONTEXT_MATRIX"
        blocker = "Resolve material clarification before provider routing or execution."
    if blocking_stage is None and routing_preview["status"] == "PROPOSED":
        if envelope.routing_approval_status == "PENDING":
            blocking_stage = "ROUTING_PREVIEW"
            blocker = routing_preview["approval_prompt"]
        elif envelope.routing_approval_status == "REJECTED":
            blocking_stage = "ROUTING_PREVIEW"
            blocker = "Routing proposal rejected; revise the plan or providers before execution."
        elif envelope.routing_preview_digest != routing_preview["digest"]:
            blocking_stage = "ROUTING_PREVIEW"
            blocker = "Routing approval does not match the current proposal; review the new preview."
        elif envelope.task_id is None:
            blocking_stage = "ROUTING_PREVIEW"
            blocker = "Approved routing requires a concrete task_id."
        else:
            candidate_active_unit = routing_preview["work_unit"]
            if routing_preview["unmatched_requirements"]:
                blocking_stage = "ROUTING"
                blocker = "No admitted provider satisfies: " + ", ".join(routing_preview["unmatched_requirements"])
            elif routing_preview["cyclic_provider_ids"]:
                blocking_stage = "ROUTING"
                blocker = "Provider prerequisite cycle: " + ", ".join(routing_preview["cyclic_provider_ids"])
            elif routing_preview["conflicting_provider_pairs"]:
                blocking_stage = "ROUTING"
                blocker = "Conflicting providers cannot be routed together."
            elif routing_preview["missing_prerequisite_providers"]:
                blocking_stage = "ROUTING"
                blocker = "Provider prerequisites are unavailable: " + ", ".join(routing_preview["missing_prerequisite_providers"])
            elif candidate_active_unit is not None:
                available_capabilities = frozenset(
                    set(capability_audit["admitted"])
                    | {provider["id"] for provider in routing_preview["providers"]}
                )
                records = {
                    item["id"]: item
                    for name in ("skills", "tools", "capabilities")
                    for item in registry_items(name)
                }
                for provider_type, provider_records in envelope.provider_inventory.items():
                    if provider_type == "domain-method":
                        continue
                    for item in provider_records:
                        if item["id"] in records:
                            raise ValueError(f"provider id is registered more than once: {item['id']}")
                        records[item["id"]] = item
                domain_registry = registry_payload("domain-methods")
                domain_registry["items"] = [
                    *domain_registry["items"],
                    *deepcopy(list(envelope.provider_inventory.get("domain-method", ()))),
                ]
                domain_records = {item["id"]: item for item in domain_registry["items"]}
                for provider in routing_preview["providers"]:
                    provider_record = (
                        domain_records[provider["id"]]
                        if provider["type"] == "domain-method"
                        else records[provider["id"]]
                    )
                    routing_class = provider["routing_task_class"]
                    if routing_class is None:
                        routing_decisions.append({
                            "status": "BLOCKED",
                            "provider_id": provider["id"],
                            "provider_type": provider["type"],
                            "requirement": provider["requirement"],
                            "reason": "TASK_CLASS_INCOMPATIBLE",
                            "preview_digest": routing_preview["digest"],
                        })
                        continue
                    context = ExecutionContext(
                        task_id=envelope.task_id,
                        plan_id=envelope.plan_id,
                        work_unit_id=candidate_active_unit,
                        task_class=routing_class,
                        available_capabilities=available_capabilities,
                    )
                    if provider["type"] == "domain-method":
                        method_record = provider_record
                        handoff = None
                        if envelope.timestamp is not None:
                            handoff = prepare_domain_context_handoff(
                                {
                                    "id": envelope.task_id,
                                    "inputs": [{"type": "user_prompt", "value": envelope.objective}],
                                    "semantic_context": semantic_context,
                                    "domain_classification": domain_classification,
                                    "domain_alignment": domain_alignment,
                                },
                                execution_context=context,
                                consumer=method_record["consumer_id"],
                                handoff_id=(
                                    "HANDOFF-"
                                    + envelope.task_id.removeprefix("TASK-")
                                    + "-"
                                    + candidate_active_unit.upper().replace("_", "-")
                                ),
                                created_at=envelope.timestamp,
                            )
                        decision = route_domain_method(
                            provider["requirement"],
                            {**domain_registry, "items": [method_record]},
                            execution_context=context,
                            handoff=handoff,
                            collection_mission=routing_preview.get("collection_mission"),
                        )
                        routing_decisions.append({
                            "status": "ROUTED" if decision["status"] == "ACTIVATE" else decision["status"],
                            "provider_id": decision["method_id"],
                            "provider_type": provider["type"],
                            "requirement": provider["requirement"],
                            "reason": decision.get("reason"),
                            "handoff_id": handoff["handoff_id"] if handoff else None,
                            "collection_mission_id": decision.get("collection_mission_id"),
                            "preview_digest": routing_preview["digest"],
                        })
                    else:
                        selected = route_capability(
                            provider["requirement"],
                            [records[provider["id"]]],
                            execution_context=context,
                        )
                        routing_decisions.append({
                            "status": "ROUTED",
                            "provider_id": selected["id"],
                            "provider_type": provider["type"],
                            "requirement": provider["requirement"],
                            "reason": None,
                            "preview_digest": routing_preview["digest"],
                        })
                rejected = next((decision for decision in routing_decisions if decision["status"] != "ROUTED"), None)
                if rejected:
                    blocking_stage = "ROUTING"
                    blocker = f"{rejected['provider_id']} routing blocked: {rejected['reason']}"

    plan_status = "BLOCKED" if blocking_stage else "READY"
    clarification_status = (
        "PENDING" if blocking_stage == "MATERIAL_CONTEXT_MATRIX" else envelope.clarification_status
    )
    active_unit = None
    if not blocking_stage:
        active_unit = candidate_active_unit
        if routing_preview["status"] != "PROPOSED":
            active_unit = select_next_work_unit(
                work_units,
                plan_id=envelope.plan_id,
                plan_status=plan_status,
                clarification_status=clarification_status,
            )
    completed = sum(item.get("status") == "COMPLETED" for item in work_units)
    state = "BLOCKED" if blocking_stage else ("COMPLETED" if active_unit is None else "READY")

    preflight_trace: tuple[str, ...] = (
        "REQUEST_TRIAGE",
        "INTENT_NORMALIZATION",
        "CAPABILITY_PLANNING",
    )
    if material_domain_context:
        preflight_trace += (
            "TAXONOMY_ROUTING",
            "MATERIAL_CONTEXT_MATRIX",
            "DOMAIN_CLASSIFICATION",
            "DOMAIN_FRAMEWORK_ALIGNMENT",
        )
    elif intelligence_route:
        preflight_trace += ("SPECIALIST_HANDOFF_PREPARATION",)
    if collection_route:
        preflight_trace += ("COLLECTION_MISSION",)
    preflight_trace += ("PLANNING", "CAPABILITY_AUDIT")
    if routing_preview["status"] == "PROPOSED":
        preflight_trace += ("ROUTING_PREVIEW",)
    if routing_decisions or blocking_stage == "ROUTING":
        preflight_trace += ("ROUTING",)
    if blocking_stage:
        execution_trace = preflight_trace
    else:
        execution_trace = preflight_trace + ("EXECUTION" if active_unit is not None else "DELIVERY",)

    processing_summary = (
        f"Route {request_triage['route']}; collection {request_triage['collection_mode']}; "
        f"domain context {'ON_DEMAND' if not material_domain_context else taxonomy_route['status']}; "
        f"intent {intent_profile['category']}; capability audit {capability_audit['status']}; "
        f"routing {envelope.routing_approval_status if routing_decisions else routing_preview['status']}; plan validated"
    )
    dashboard = create_dashboard(
        envelope.objective,
        plan_id=envelope.plan_id,
        plan_status=plan_status,
        surface=envelope.surface,
        timestamp=envelope.timestamp,
        timezone_name=envelope.timezone_name,
        active_stage=blocking_stage or ("DELIVERY" if active_unit is None else "EXECUTION"),
        active_unit=(
            "Review routing proposal"
            if blocking_stage in {"ROUTING_PREVIEW", "ROUTING"}
            else "Resolve material clarification" if blocking_stage else active_unit or "Plan complete"
        ),
        completed_units=completed,
        total_units=len(work_units),
        progress=round(100 * completed / len(work_units)),
        clarification_status=clarification_status,
        processing_summary=processing_summary,
        quality_gate="BLOCKED" if state == "BLOCKED" else "PASS" if state == "COMPLETED" else "PENDING",
        blocker=blocker,
    )
    dashboard["request_triage"] = deepcopy(request_triage)
    dashboard["capability_plan"] = deepcopy(capability_plan)
    dashboard["routing_preview"] = deepcopy(routing_preview)
    dashboard["routing_decisions"] = deepcopy(routing_decisions)
    dashboard["intent_profile"] = deepcopy(intent_profile)
    dashboard["behavioral_learning_state"] = deepcopy(behavioral_learning_state)
    dashboard["duration_ms"] = max(0, round((perf_counter_ns() - started) / 1_000_000))
    return ExecutionResult(
        state=state,
        request_route=request_triage["route"],
        request_triage=request_triage,
        normalized_intent=normalized,
        semantic_context=semantic_context,
        task_classes=task_classes,
        plan=plan,
        active_unit=active_unit,
        dashboard=dashboard,
        taxonomy_route=taxonomy_route,
        completeness=completeness,
        domain_classification=domain_classification,
        domain_alignment=domain_alignment,
        capability_audit=capability_audit,
        capability_plan=capability_plan,
        intent_profile=intent_profile,
        behavioral_learning_state=behavioral_learning_state,
        routing_preview=routing_preview,
        routing_decisions=tuple(routing_decisions),
        execution_trace=execution_trace,
    )
