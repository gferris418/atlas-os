"""ATLAS-OS v3 reference runtime."""

from .adapters import SurfaceAdapter, get_surface_adapter
from .capabilities import (
    CapabilityError,
    CapabilityReplayError,
    InMemoryReplayGuard,
    issue_remote_capability,
    verify_remote_capability,
)
from .contract import ARGUS_APPROVAL, EXECUTION_CONTRACT, PRE_EXECUTION_FLOW
from .models import ExecutionEnvelope, ExecutionResult, RouteDecision
from .router import EXTERNAL_ACTION_APPROVAL, choose_route, minimal_domain_framing, normalize_objective
from .runtime import execute

__all__ = [
    "ARGUS_APPROVAL",
    "EXTERNAL_ACTION_APPROVAL",
    "EXECUTION_CONTRACT",
    "PRE_EXECUTION_FLOW",
    "CapabilityError",
    "CapabilityReplayError",
    "ExecutionEnvelope",
    "ExecutionResult",
    "InMemoryReplayGuard",
    "RouteDecision",
    "SurfaceAdapter",
    "choose_route",
    "execute",
    "get_surface_adapter",
    "issue_remote_capability",
    "minimal_domain_framing",
    "normalize_objective",
    "verify_remote_capability",
]
