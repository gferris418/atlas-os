"""Executable surface seams sharing the ATLAS planning and delivery contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol

from .runtime import build_plan, create_dashboard, prepare_library_record, select_next_work_unit


class LibraryStorage(Protocol):
    def save(self, record: dict[str, Any], content: str | bytes) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SurfaceAdapter:
    surface_id: str

    def start_prompt(
        self,
        objective: str,
        tasks: Iterable[dict[str, Any]],
        *,
        plan_id: str,
        clarification_status: str = "NOT_REQUIRED",
        timestamp: str | None = None,
    ) -> dict[str, Any]:
        records = list(tasks)
        if not records:
            raise ValueError("surface startup requires at least one planned work unit")
        build_plan(records)
        active_unit = select_next_work_unit(
            records,
            plan_id=plan_id,
            plan_status="READY",
            clarification_status=clarification_status,
        )
        completed = sum(item.get("status") == "COMPLETED" for item in records)
        return create_dashboard(
            objective,
            plan_id=plan_id,
            plan_status="READY",
            surface=self.surface_id,
            timestamp=timestamp,
            active_stage="PLANNING" if active_unit is None else "EXECUTION",
            active_unit=active_unit or "Plan complete",
            completed_units=completed,
            total_units=len(records),
            progress=round(100 * completed / len(records)),
            clarification_status=clarification_status,
            processing_summary="Plan validated; next atomic work unit selected",
        )

    def deliver(
        self,
        output_id: str,
        profile: dict[str, Any],
        content: str | bytes,
        *,
        storage: LibraryStorage | None = None,
        timestamp: str | None = None,
        timezone_name: str = "UTC",
        authorized: bool = True,
        sensitivity_allowed: bool = True,
    ) -> dict[str, Any]:
        record = prepare_library_record(
            output_id,
            profile,
            capability_available=storage is not None,
            authorized=authorized,
            sensitivity_allowed=sensitivity_allowed,
            timestamp=timestamp,
            timezone_name=timezone_name,
        )
        if storage is None or record["delivery_status"] != "READY":
            return record
        return storage.save(record, content)


_SURFACES = {
    surface: SurfaceAdapter(surface)
    for surface in ("chatgpt", "codex", "work")
}


def get_surface_adapter(surface_id: str) -> SurfaceAdapter:
    try:
        return _SURFACES[surface_id]
    except KeyError as error:
        raise LookupError(f"unsupported ATLAS surface: {surface_id}") from error
