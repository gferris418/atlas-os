---
name: atlas-os
description: Apply the ATLAS-OS execution-governance contract to AI-agent work using the current host's native capabilities.
version: 2.0.2-rc.4
metadata:
  atlas:
    control_revision: atlas-bootstrap-2026-10-22-r8
    ai_entrypoint: atlas-ai.yaml
  hermes:
    tags: [governance, planning, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply, or govern work with ATLAS-OS, or when the task explicitly requires the ATLAS execution spine.

1. Locate the repository root, read `atlas-ai.yaml` as the machine discovery entrypoint, then read `atlas-os.yaml` as the sole product and release authority.
2. Preserve the untouched prompt, then run the lightweight request-triage gate before deep domain work: `GENERAL_SEARCH`, `GENERAL_TASK`, or `INTELLIGENCE`.
3. Keep `GENERAL_SEARCH` and `GENERAL_TASK` on the direct ATLAS path. Resolve taxonomy, classification, law, standards, frameworks, or other domain context only when they can materially change correctness, authorization, safety, or the requested outcome.
4. For `INTELLIGENCE`, route the canonical `intelligence_analysis` requirement to governed ARGUS after routing/approval gates. A `READY` or `PARTIAL` domain-context handoff may proceed; ARGUS enriches unresolved intelligence context while ATLAS retains authority, permissions, planning, approvals, verification, persistence authorization, and final delivery.
5. Normalize intent and assess only material Who, What, Where, When, Why, Which, How, and How Much gaps needed by the selected path.
6. Read `spec/core.yaml`, then only the additional active machine contracts, specifications, registries, migration controls, and integration guidance material to the current task.
7. Treat ATLAS-OS as an AI-agent governance layer. Never present it as a replacement or modification for the host machine's operating system.
8. Establish a concrete plan identifier and approval gates, then audit and route the smallest admitted set of native capabilities, skills, plugins, tools, or specialist methods required by the plan.
9. Execute one authorized atomic work unit at a time, preserving the ATLAS evidence, authorization, verification, persistence, and delivery controls.
10. Treat Mission Control as the human command/intervention surface, Control Plane as authoritative machine governance, Dashboard/Observability as derived read-only state, and Domain Intelligence as conditional context rather than universal preflight.
11. Identify the active host with a stable lowercase slug. Use `hermes-agent` in Hermes and the host's own slug elsewhere.
12. Run the optional Python reference runtime only when it is available and useful; the specifications remain authoritative when it is unavailable.
13. Before claiming completion, verify the requested outcome using fresh evidence and report any blocked or unavailable capability explicitly.
14. When asked for the governing ATLAS identity, resolve it from `atlas-os.yaml` and report version `2.0.2-rc.4` and control revision `atlas-bootstrap-2026-10-22-r8`.

For installation and host mapping, read `docs/ai-host-installation.md` and the matching file under `integrations/`. For an unlisted host, use `integrations/generic-ai-host/README.md`. For external conformance testing, use the machine-readable `integrations/<surface>/release-verification.yaml`; Markdown verification documents are human companions only.

## Boundaries

- Never weaken host permission prompts or ATLAS approval requirements.
- Never treat model output as verified evidence by itself.
- Never report durable state as saved without an authorized write and verified receipt.
- Never create provider-specific core semantics; keep host behavior in its adapter.
- Never activate ARGUS merely because a government body, tender, company, market, person, or political subject is mentioned; an intelligence objective or explicit admissible ARGUS request is required.
- Never allow downstream intent/provider logic to silently override a `GENERAL_SEARCH` or `GENERAL_TASK` triage decision into ARGUS activation.
- Never close an external-proof migration from repository-local or self-generated evidence.
