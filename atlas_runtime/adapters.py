from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .models import ExecutionEnvelope, ExecutionResult
from .runtime import execute


@dataclass(frozen=True)
class SurfaceAdapter:
    host: str

    def start(
        self,
        objective: str,
        *,
        task_id: str | None = None,
        context: Mapping[str, Any] | None = None,
        approvals: tuple[str, ...] = (),
        provider_result: Mapping[str, Any] | None = None,
    ) -> ExecutionResult:
        return execute(ExecutionEnvelope(
            objective=objective,
            task_id=task_id,
            host=self.host,
            context=context or {},
            approvals=approvals,
            provider_result=provider_result,
        ))


def get_surface_adapter(host: str) -> SurfaceAdapter:
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")
    return SurfaceAdapter(host.strip())
