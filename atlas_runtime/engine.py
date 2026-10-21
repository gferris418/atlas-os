"""Small public execution interface over the ATLAS governance primitives."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any, Iterable

from .runtime import (
    build_plan,
    classify_task,
    create_dashboard,
    normalize_intent,
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
    normalized = normalize_intent(envelope.objective)["normalized"]
    plan = tuple(build_plan(work_units))
    active_unit = select_next_work_unit(
        work_units,
        plan_id=envelope.plan_id,
        plan_status="READY",
        clarification_status=envelope.clarification_status,
    )
    completed = sum(item.get("status") == "COMPLETED" for item in work_units)
    state = "COMPLETED" if active_unit is None else "READY"
    dashboard = create_dashboard(
        envelope.objective,
        plan_id=envelope.plan_id,
        plan_status="READY",
        surface=envelope.surface,
        timestamp=envelope.timestamp,
        timezone_name=envelope.timezone_name,
        active_stage="DELIVERY" if active_unit is None else "EXECUTION",
        active_unit=active_unit or "Plan complete",
        completed_units=completed,
        total_units=len(work_units),
        progress=round(100 * completed / len(work_units)),
        clarification_status=envelope.clarification_status,
        processing_summary="Plan validated; next atomic work unit selected",
        quality_gate="PASS" if state == "COMPLETED" else "PENDING",
    )
    dashboard["duration_ms"] = max(0, round((perf_counter_ns() - started) / 1_000_000))
    return ExecutionResult(
        state=state,
        normalized_intent=normalized,
        task_classes=tuple(classify_task(normalized)),
        plan=plan,
        active_unit=active_unit,
        dashboard=dashboard,
    )
