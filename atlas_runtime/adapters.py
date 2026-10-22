"""Executable host seams sharing the portable ATLAS orchestration contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from .orchestration import ExecutionEnvelope, execute
from .runtime import prepare_library_record
from .surfaces import validate_surface_id


class LibraryStorage(Protocol):
    def save(self, record: dict[str, Any], content: str | bytes) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SurfaceAdapter:
    """Host adapter that supplies capabilities without owning ATLAS governance."""

    surface_id: str

    def start_prompt(
        self,
        objective: str,
        tasks: Iterable[dict[str, Any]],
        *,
        plan_id: str,
        clarification_status: str = "NOT_REQUIRED",
        task_id: str | None = None,
        capability_requirements: Iterable[str] = (),
        provider_inventory: Mapping[str, Iterable[dict[str, Any]]] | None = None,
        routing_approval_status: str = "PENDING",
        routing_preview_digest: str | None = None,
        argus_approval_status: str = "PENDING",
        timestamp: str | None = None,
        timezone_name: str = "UTC",
    ) -> dict[str, Any]:
        return execute(ExecutionEnvelope(
            objective=objective,
            plan_id=plan_id,
            work_units=tasks,
            surface=self.surface_id,
            timestamp=timestamp,
            timezone_name=timezone_name,
            clarification_status=clarification_status,
            task_id=task_id,
            capability_requirements=capability_requirements,
            provider_inventory=provider_inventory,
            routing_approval_status=routing_approval_status,
            routing_preview_digest=routing_preview_digest,
            argus_approval_status=argus_approval_status,
        )).dashboard

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


def get_surface_adapter(surface_id: str) -> SurfaceAdapter:
    """Return the shared adapter seam for any valid AI-host identifier."""

    return SurfaceAdapter(validate_surface_id(surface_id))
