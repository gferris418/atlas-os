"""Small public execution interface over the ATLAS governance primitives."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Iterable

import yaml

from .runtime import (
    align_domain_practices,
    assess_completeness,
    audit_capability_providers,
    build_plan,
    classify_domain_context,
    classify_task,
    create_dashboard,
    normalize_intent,
    route_taxonomy_layer,
    select_next_work_unit,
)
from .surfaces import validate_surface_id


@dataclass(frozen=True)
class ExecutionEnvelope:
    """The minimum context required to begin one governed ATLAS execution."""

    objective: str
    plan_id: str
    work_units: Iterable[dict[str, Any]]
    surface: str = "core"
    clarification_status: str = "NOT_REQUIRED"
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
        object.__setattr__(self, "work_units", work_units)


@dataclass(frozen=True)
class ExecutionResult:
    """One state-derived view of the current ATLAS execution."""

    state: str
    normalized_intent: str
    task_classes: tuple[str, ...]
    plan: tuple[str, ...]
    active_unit: str | None
    dashboard: dict[str, Any]
    taxonomy_route: dict[str, Any]
    completeness: dict[str, Any]
    domain_classification: dict[str, Any]
    domain_alignment: dict[str, Any]
    capability_audit: dict[str, Any]
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


def execute(envelope: ExecutionEnvelope) -> ExecutionResult:
    """Compile current ATLAS state through one stable public interface.

    The function deliberately returns the next atomic work unit instead of
    performing host-specific work. Surface adapters and hosts execute that
    unit, then call this interface again with the updated work-unit states.
    """

    started = perf_counter_ns()
    work_units = deepcopy(list(envelope.work_units))
    repository_root = Path(__file__).resolve().parents[1]

    def registry_items(name: str) -> list[dict[str, Any]]:
        path = repository_root / "registries" / f"{name}.yaml"
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return list(payload["items"])

    taxonomies = registry_items("taxonomies")
    taxonomy_route = route_taxonomy_layer(
        envelope.objective,
        registry_items("taxonomy-routes"),
        taxonomies,
    )
    normalized = normalize_intent(envelope.objective)["normalized"]
    task_classes = tuple(classify_task(normalized))
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
    plan = tuple(build_plan(work_units))
    capability_audit = audit_capability_providers(registry_items("capabilities"))
    blocking_stage: str | None = None
    blocker: str | None = None
    if substantive and envelope.clarification_status != "RESOLVED":
        if not completeness["complete"]:
            blocking_stage = "MATERIAL_CONTEXT_MATRIX"
            blocker = (
                "Clarify material context: "
                + ", ".join(completeness["questions"])
            )
        elif domain_classification["status"] != "CLASSIFIED":
            blocking_stage = "DOMAIN_CLASSIFICATION"
            blocker = domain_classification["next_action"]
        elif domain_alignment["status"] == "RESEARCH_REQUIRED":
            blocking_stage = "DOMAIN_FRAMEWORK_ALIGNMENT"
            blocker = domain_alignment["next_action"]

    plan_status = "BLOCKED" if blocking_stage else "READY"
    clarification_status = "PENDING" if blocking_stage else envelope.clarification_status
    active_unit = None
    if not blocking_stage:
        active_unit = select_next_work_unit(
            work_units,
            plan_id=envelope.plan_id,
            plan_status=plan_status,
            clarification_status=clarification_status,
        )
    completed = sum(item.get("status") == "COMPLETED" for item in work_units)
    state = "BLOCKED" if blocking_stage else ("COMPLETED" if active_unit is None else "READY")
    preflight_trace = (
        "TAXONOMY_ROUTING",
        "INTENT_NORMALIZATION",
        "MATERIAL_CONTEXT_MATRIX",
        "DOMAIN_CLASSIFICATION",
        "DOMAIN_FRAMEWORK_ALIGNMENT",
        "PLANNING",
        "CAPABILITY_AUDIT",
    )
    if blocking_stage:
        execution_trace = preflight_trace
    else:
        execution_trace = preflight_trace + (
            "EXECUTION" if active_unit is not None else "DELIVERY",
        )
    processing_summary = (
        f"Taxonomy {taxonomy_route['status']}; context "
        f"{'COMPLETE' if completeness['complete'] else 'PARTIAL'}; classification "
        f"{domain_classification['status']}; capability audit {capability_audit['status']}; "
        "plan validated"
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
            "Resolve material clarification"
            if blocking_stage
            else active_unit or "Plan complete"
        ),
        completed_units=completed,
        total_units=len(work_units),
        progress=round(100 * completed / len(work_units)),
        clarification_status=clarification_status,
        processing_summary=processing_summary,
        quality_gate=(
            "BLOCKED" if state == "BLOCKED" else "PASS" if state == "COMPLETED" else "PENDING"
        ),
        blocker=blocker,
    )
    dashboard["duration_ms"] = max(0, round((perf_counter_ns() - started) / 1_000_000))
    return ExecutionResult(
        state=state,
        normalized_intent=normalized,
        task_classes=task_classes,
        plan=plan,
        active_unit=active_unit,
        dashboard=dashboard,
        taxonomy_route=taxonomy_route,
        completeness=completeness,
        domain_classification=domain_classification,
        domain_alignment=domain_alignment,
        capability_audit=capability_audit,
        execution_trace=execution_trace,
    )
