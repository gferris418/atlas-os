# Surface integrations

AI hosts discover canonical surface behavior from `atlas-ai.yaml` and `registries/surfaces.yaml`. Each registered host has a schema-validated `integrations/<surface>/adapter.yaml`; those YAML files are the canonical adapter contracts. The corresponding `README.md` files are human companions only.

Adapters translate surface capabilities into the common ATLAS execution contract. They may declare availability, limitations, tool models, persistence, approval behavior, startup behavior, and unsupported features; they must not copy or redefine core semantics.

The executable reference seam is `atlas_runtime.get_surface_adapter(surface_id)`. It validates a provider-neutral AI-host slug, a concrete plan, and material-clarification state before selecting work, creates the common dashboard, and delivers through an authorized persistence adapter when one is present. Known hosts have machine registrations, while any valid host slug can use the generic seam without a core release. This local seam does not replace independent host bootstrap and propagation evidence.

Supported machine adapters:

- `chatgpt/adapter.yaml` — ChatGPT conversational and research surface.
- `codex/adapter.yaml` — repository, execution, test, and validation surface.
- `work/adapter.yaml` — connected-app multi-step work surface.
- `hermes-agent/adapter.yaml` — project-skill agent surface.
- `generic-ai-host/adapter.yaml` — provider-neutral fallback for an unlisted AI host.

External conformance procedures for supported proof surfaces are machine-readable at `integrations/<surface>/release-verification.yaml`. A verification contract being present is readiness evidence only; it is not proof that an external host resolved or applied the current control revision.

Business integration overlays:

- `access-asia/opportunity-lifecycle.yaml` — canonical machine lifecycle contract for the Access Asia opportunity/project routing overlay. `access-asia/README.md` is its human companion.

Conformance remains candidate-level while MIG-029 and MIG-037 are open.
