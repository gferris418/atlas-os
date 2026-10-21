---
name: atlas-os
description: Apply the ATLAS-OS execution-governance contract to AI-agent work using the current host's native capabilities.
version: 2.0.2-rc.3
metadata:
  atlas:
    control_revision: atlas-bootstrap-2026-10-21-r7
  hermes:
    tags: [governance, planning, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply, or govern work with ATLAS-OS, or when the task explicitly requires the ATLAS execution spine.

1. Locate the repository root and read `atlas-os.yaml` as the sole product and release authority.
2. Preserve the untouched prompt, then begin with the taxonomy layer: Domain -> Sub-Domain -> Vertical -> Artifact Class. Identify candidate classification schemes without assigning unverified external codes.
3. Normalize intent and assess only material Who, What, Where, When, Why, Which, How, and How Much gaps.
4. Resolve applicable jurisdiction, operator industry, supplier industry, product or service, capability, lifecycle, stakeholder, and information-sensitivity classifications before selecting domain requirements or frameworks.
5. Read `spec/core.yaml`, then only the additional active specifications, registries, and integration guidance material to the current task.
6. Treat ATLAS-OS as an AI-agent governance layer. Never present it as a replacement or modification for the host machine's operating system.
7. Establish a concrete plan identifier and approval gates, then audit the smallest admitted set of native capabilities, skills, plugins, tools, or specialist methods required by the plan.
8. Before routing any provider, show what ATLAS proposes to do and how: the exact work unit, semantic requirements, provider purpose and method, permission, data scope, prerequisites, fallback, unresolved gates, and execution sequence. Bind approval to the exact preview digest; rejection, omission, mismatch, or a changed proposal blocks routing.
9. Route only the approved proposal, create and validate any required specialist handoff, then execute one authorized atomic work unit at a time while preserving the ATLAS evidence, authorization, verification, persistence, and delivery controls.
10. Identify the active host with a stable lowercase slug. Use `hermes-agent` in Hermes and the host's own slug elsewhere.
11. Run the optional Python reference runtime only when it is available and useful; the specifications remain authoritative when it is unavailable.
12. Before claiming completion, verify the requested outcome using fresh evidence and report any blocked or unavailable capability explicitly.
13. When asked for the governing ATLAS identity, report version `2.0.2-rc.3` and control revision `atlas-bootstrap-2026-10-21-r7`.

For installation and host mapping, read `docs/ai-host-installation.md` and the matching file under `integrations/`. For an unlisted host, use `integrations/generic-ai-host/README.md`.

## Boundaries

- Never weaken host permission prompts or ATLAS approval requirements.
- Never treat model output as verified evidence by itself.
- Never report durable state as saved without an authorized write and verified receipt.
- Never create provider-specific core semantics; keep host behavior in its adapter.
