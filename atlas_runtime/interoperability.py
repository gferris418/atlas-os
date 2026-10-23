from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
        if not isinstance(protocol, str) or not protocol.strip():
            raise ValueError("protocol must be a non-empty string")
        if not isinstance(provides, list) or not provides or not all(
            isinstance(item, str) and item.strip() for item in provides
        ):
            raise ValueError("provides must contain at least one capability id")
        if "permissions" not in value:
            raise ValueError("permissions is required")
        if "evidence" not in value:
            raise ValueError("evidence is required")
        permissions = value["permissions"]
        evidence = value["evidence"]
        if not isinstance(permissions, dict) or not isinstance(evidence, dict):
            raise ValueError("permissions and evidence must be objects")
        return cls(
            provider_id=provider_id,
            protocol=protocol,
            capabilities=tuple(dict.fromkeys(provides)),
            permissions=dict(permissions),
            evidence={key: bool(item) for key, item in evidence.items()},
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
        "schema": bool(manifest.provider_id and manifest.protocol and manifest.capabilities),
        "capability_map": all("." in item for item in manifest.capabilities),
        "permissions": isinstance(manifest.permissions, dict),
        "provenance": bool(manifest.evidence.get("provenance")),
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
