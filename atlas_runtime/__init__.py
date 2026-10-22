"""ATLAS-OS v3 reference runtime."""

from .adapters import SurfaceAdapter, get_surface_adapter
from .models import ExecutionEnvelope, ExecutionResult, RouteDecision
from .quality import (
    QUALITY_REQUIREMENTS,
    QUALITY_TIERS,
    determine_required_quality_tier,
    evaluate_quality_gate,
    max_quality_tier,
    quality_rank,
    quality_requirements,
)
from .router import ARGUS_APPROVAL, EXTERNAL_ACTION_APPROVAL, PRE_EXECUTION_FLOW, choose_route, minimal_domain_framing, normalize_objective
from .runtime import execute

__all__ = [
    "ARGUS_APPROVAL",
    "EXTERNAL_ACTION_APPROVAL",
    "PRE_EXECUTION_FLOW",
    "QUALITY_REQUIREMENTS",
    "QUALITY_TIERS",
    "ExecutionEnvelope",
    "ExecutionResult",
    "RouteDecision",
    "SurfaceAdapter",
    "choose_route",
    "determine_required_quality_tier",
    "evaluate_quality_gate",
    "execute",
    "get_surface_adapter",
    "max_quality_tier",
    "minimal_domain_framing",
    "normalize_objective",
    "quality_rank",
    "quality_requirements",
]
