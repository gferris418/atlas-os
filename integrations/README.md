# Surface integrations

Adapters translate surface capabilities into the common ATLAS execution contract. They may describe availability, limitations, tool models, persistence, approval behavior, startup behavior, and unsupported features; they must not copy or redefine core semantics.

The executable reference seam is `atlas_runtime.get_surface_adapter(surface_id)`. It validates a provider-neutral AI-host slug, a concrete plan, and material-clarification state before selecting work, creates the common dashboard, and delivers through an authorized persistence adapter when one is present. Known hosts have documented registrations, while any valid host slug can use the generic seam without a core release. This local seam does not replace independent host bootstrap and propagation evidence.

Supported surface adapters:

- [ChatGPT](chatgpt/README.md)
- [Codex](codex/README.md)
- [ChatGPT Work](work/README.md)
- [Hermes Agent](hermes-agent/README.md)
- [Any other AI host](generic-ai-host/README.md)

Business integration overlays:

- [Access Asia opportunity lifecycle](access-asia/README.md) — preserves one permanent opportunity ID while routing working files from Business Intelligence to REV/OPP only at `SUBMISSION_ACTIVE`, then to OPS/PRJ on award/contract activation.

Conformance remains candidate-level while MIG-029 and MIG-037 are open.
