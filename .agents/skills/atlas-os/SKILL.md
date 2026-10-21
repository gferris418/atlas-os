---
name: atlas-os
description: Apply the ATLAS-OS execution-governance contract to AI-agent work using the current host's native capabilities.
version: 2.0.1
metadata:
  hermes:
    tags: [governance, planning, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply, or govern work with ATLAS-OS, or when the task explicitly requires the ATLAS execution spine.

1. Locate the repository root and read `atlas-os.yaml` as the sole product and release authority.
2. Read `spec/core.yaml`, then only the additional active specifications, registries, and integration guidance material to the current task.
3. Treat ATLAS-OS as an AI-agent governance layer. Never present it as a replacement or modification for the host machine's operating system.
4. Use the current AI host's native language, reasoning, conversation, tool, approval, and storage capabilities. Do not claim a capability exists until the current session exposes it.
5. Establish a concrete plan identifier, resolve material clarification, select one atomic work unit, and preserve the ATLAS evidence, authorization, verification, persistence, and delivery controls.
6. Identify the active host with a stable lowercase slug. Use `hermes-agent` in Hermes and the host's own slug elsewhere.
7. Run the optional Python reference runtime only when it is available and useful; the specifications remain authoritative when it is unavailable.
8. Before claiming completion, verify the requested outcome using fresh evidence and report any blocked or unavailable capability explicitly.

For installation and host mapping, read `docs/ai-host-installation.md` and the matching file under `integrations/`. For an unlisted host, use `integrations/generic-ai-host/README.md`.

## Boundaries

- Never weaken host permission prompts or ATLAS approval requirements.
- Never treat model output as verified evidence by itself.
- Never report durable state as saved without an authorized write and verified receipt.
- Never create provider-specific core semantics; keep host behavior in its adapter.
