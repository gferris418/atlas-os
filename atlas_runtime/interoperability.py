from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any


_ALLOWED_PROTOCOLS = {"native", "mcp", "plugin", "api", "database", "filesystem"}
_ALLOWED_PERMISSION_VALUES = {"automatic", "approval_required", "forbidden"}
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_-]*(\.[a-z][a-z0-9_-]*)+$")


class AdmissionState(str, Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATED = "VALIDATED"
    CERTIFIED = "CERTIFIED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class ProviderManifest:
    provider_id: str
    protocol: str
    capabilities: tuple[str, ...]
    permissions: dict[str, str]
    evidence: dict[str, bool]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ProviderManifest":
        provider_id = value.get("provider_id")
        protocol = value.get("protocol")
        provides = value.get("provides")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if protocol not in _ALLOWED_PROTOCOLS:
            raise ValueError("protocol is not supported")
        if not isinstance(provides, list) or not provides or not all(
            isinstance(item, str) and _CAPABILITY_ID.fullmatch(item) for item in provides
        ):
            raise ValueError("provides must contain valid capability ids")
        if "permissions" not in value:
            raise ValueError("permissions is required")
        if "evidence" not in value:
            raise ValueError("evidence is required")
        permissions = value["permissions"]
        evidence = value["evidence"]
        if not isinstance(permissions, dict) or not all(
            isinstance(key, str) and item in _ALLOWED_PERMISSION_VALUES
            for key, item in permissions.items()
        ):
            raise ValueError("permissions must use allowed values")
        if not isinstance(evidence, dict) or "provenance" not in evidence:
            raise ValueError("evidence.provenance is required")
        if not all(isinstance(item, bool) for item in evidence.values()):
            raise ValueError("evidence values must be booleans")
        return cls(
            provider_id=provider_id,
            protocol=protocol,
            capabilities=tuple(dict.fromkeys(provides)),
            permissions=dict(permissions),
            evidence=dict(evidence),
        )

    def provides(self, capability_id: str) -> bool:
        return capability_id in self.capabilities


@dataclass(frozen=True)
class AdmissionReceipt:
    provider_id: str
    state: AdmissionState
    checks: dict[str, bool]


def admit_provider(manifest: ProviderManifest) -> AdmissionReceipt:
    checks = {
        "schema": True,
        "capability_map": all(_CAPABILITY_ID.fullmatch(item) is not None for item in manifest.capabilities),
        "permissions": all(item in _ALLOWED_PERMISSION_VALUES for item in manifest.permissions.values()),
        "provenance": manifest.evidence.get("provenance") is True,
    }
    state = AdmissionState.CERTIFIED if all(checks.values()) else AdmissionState.VALIDATED
    return AdmissionReceipt(manifest.provider_id, state, checks)


@dataclass(frozen=True)
class BindingRegistry:
    bindings: dict[str, tuple[str, ...]]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "BindingRegistry":
        bindings: dict[str, tuple[str, ...]] = {}
        for capability_id, config in value.items():
            if not isinstance(config, dict):
                raise ValueError(f"binding {capability_id} must be an object")
            primary = config.get("primary")
            fallbacks = config.get("fallbacks", [])
            if not isinstance(primary, str) or not primary.strip():
                raise ValueError(f"binding {capability_id} requires primary")
            if not isinstance(fallbacks, list) or not all(isinstance(item, str) for item in fallbacks):
                raise ValueError(f"binding {capability_id} fallbacks must be strings")
            bindings[capability_id] = tuple(dict.fromkeys([primary, *fallbacks]))
        return cls(bindings)

    def candidates(self, capability_id: str) -> tuple[str, ...]:
        return self.bindings.get(capability_id, ())


__all__ = [
    "AdmissionReceipt",
    "AdmissionState",
    "BindingRegistry",
    "ProviderManifest",
    "admit_provider",
]
