# Integration model

Every surface adapter documents capabilities, limitations, tool and persistence models, approval behavior, startup behavior, unsupported features, and conformance status. Adapters consume core contracts in a shared discovery order and never declare a competing product version.

The reference runtime exposes executable `chatgpt`, `codex`, and `work` configurations through one shared adapter boundary. Integration tests verify common plan gating, dashboard initialization, authorization behavior, real filesystem delivery, and explicit unavailable-storage reporting. Actual host installation and cross-surface propagation remain external conformance requirements.

Availability is runtime evidence: a registry entry says what a capability means, while the active surface determines whether it is actually exposed. Fallbacks are explicit and cannot pretend an unavailable action occurred.

See `integrations/` for the active adapter contracts.

