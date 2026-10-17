# Surface integrations

Adapters translate surface capabilities into the common ATLAS execution contract. They may describe availability, limitations, tool models, persistence, approval behavior, startup behavior, and unsupported features; they must not copy or redefine core semantics.

The executable reference seam is `atlas_runtime.get_surface_adapter(surface_id)`. It validates a concrete plan and material-clarification state before selecting work, creates the common dashboard, and delivers through an authorized persistence adapter when one is present. This local seam does not replace independent host bootstrap and propagation evidence.

Supported adapters:

- [ChatGPT](chatgpt/README.md)
- [Codex](codex/README.md)
- [ChatGPT Work](work/README.md)

Conformance remains candidate-level while MIG-029 and MIG-037 are open.

