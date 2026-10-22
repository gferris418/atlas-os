"""ATLAS-OS v3 reference runtime."""

from .adapters import SurfaceAdapter, get_surface_adapter
from .models import ExecutionEnvelope, ExecutionResult, RouteDecision
from .router import ARGUS_APPROVAL, EXTERNAL_ACTION_APPROVAL, PRE_EXECUTION_FLOW, choose_route, minimal_domain_framing, normalize_objective
from .runtime import execute

__all__ = [
    "ARGUS_APPROVAL",
    "EXTERNAL_ACTION_APPROVAL",
    "PRE_EXECUTION_FLOW",
    "ExecutionEnvelope",
    "ExecutionResult",
    "RouteDecision",
    "SurfaceAdapter",
    "choose_route",
    "execute",
    "get_surface_adapter",
    "minimal_domain_framing",
    "normalize_objective",
]
