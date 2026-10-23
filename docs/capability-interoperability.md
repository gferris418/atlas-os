# Capability Interoperability Layer

ATLAS remains the control plane. External systems are providers of capabilities; they do not acquire orchestration authority by being connected.

## Goals

1. Keep capability semantics independent of provider brands and host UI.
2. Let MCP servers, plugins, APIs, databases, filesystems, and native host tools declare what they provide.
3. Admit providers only after validation and evidence/provenance checks.
4. Resolve primary and fallback providers through bindings rather than hard-coded workflows.
5. Let specialist systems such as ARGUS declare requirements while ATLAS selects providers.

## Four registries

- `registries/capabilities.yaml`: coarse ATLAS execution classes.
- `registries/fine-grained-capabilities.yaml`: portable task-level capability IDs.
- `registries/providers.yaml`: execution mechanisms and authority boundaries.
- `registries/bindings.yaml`: preferred and fallback provider resolution.

`registries/surfaces.yaml` remains the host/surface exposure registry.

## Provider admission

Provider lifecycle:

`DISCOVERED -> VALIDATED -> CERTIFIED -> ACTIVE -> DEGRADED -> DISABLED`

Minimum certification checks are schema validity, capability mapping, permission declaration, and provenance support. Deployment adapters may add authentication, security, classification, health, contract, and conformance checks before ACTIVE status.

## Provider manifest

Providers should expose data conforming to `contracts/provider-manifest-v1.schema.json`. A provider manifest declares protocol, fine-grained capabilities, permission behavior, evidence support, health metadata, and classification handling.

## Binding rules

Bindings are policy, not authority. A binding may nominate a primary and ordered fallbacks. Runtime availability, provider admission state, user approval boundaries, data classification, and the canonical ATLAS execution contract remain authoritative.

## ARGUS boundary

ARGUS must declare the fine-grained capabilities required for an intelligence workflow. It must not hard-code a general external-provider architecture. ATLAS resolves the requirements to admitted providers and returns specialist results to Mission Control.

## Security

The existing ATLAS remote capability contract remains the execution-security boundary for delegated remote execution. Fine-grained capability discovery and binding do not weaken task binding, intent binding, TTL, replay protection, approval, or return-to-ATLAS requirements.
