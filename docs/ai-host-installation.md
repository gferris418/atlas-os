# Install ATLAS-OS in an AI host

ATLAS-OS is an execution-governance layer for AI agents. It is not a device operating system, a bootable image, or a Windows/macOS/Linux customization. Installation means making the canonical ATLAS contract available to an AI host and configuring that host to apply it. The same repository works from a browser-only service, a desktop agent, a terminal agent, a container, or a remote server.

## Portable installation contract

Every installation in any AI host must:

1. Resolve [`atlas-ai.yaml`](../atlas-ai.yaml) as the machine discovery entrypoint, then [`atlas-os.yaml`](../atlas-os.yaml) as the sole product/release authority.
2. Resolve the host's schema-valid `integrations/<surface>/adapter.yaml` from [`registries/surfaces.yaml`](../registries/surfaces.yaml); Markdown adapter documents are human companions only.
3. Apply the active contracts under [`spec/`](../spec/) without copying or redefining their semantics.
4. Use the host's native model, conversation, tools, storage, and approval mechanisms when available.
5. Report unavailable capabilities rather than pretending an action, save, or verification occurred.
6. Identify the host with a lowercase surface slug such as `chatgpt`, `hermes-agent`, or `my-ai-tool`.
7. Preserve user authorization, evidence, verification, persistence, and specialist-boundary controls.

The Python runtime is an optional conformance reference. An AI host can apply ATLAS directly from the machine contracts even when it cannot execute Python.

## ChatGPT

Use one of these supported patterns:

- Attach the repository to a Project or conversation and start discovery at [`atlas-ai.yaml`](../atlas-ai.yaml).
- Paste or upload [`ATLAS-CHATGPT-INSTRUCTIONS.md`](../integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md) when the full repository is not available.
- Install a verified repository snapshot in ChatGPT Library by following [`chatgpt-library-install.md`](chatgpt-library-install.md).

When repository files are available, `integrations/chatgpt/adapter.yaml` governs the surface contract and `integrations/chatgpt/release-verification.yaml` governs external verification. The compatibility profile is a compact bootstrap, not a competing ATLAS definition.

## Hermes Agent

This repository includes a platform-neutral project skill at [`.agents/skills/atlas-os/SKILL.md`](../.agents/skills/atlas-os/SKILL.md). Hermes Agent discovers `.agents/skills/` when it starts inside a Git checkout.

1. Clone or open this repository from any environment supported by Hermes Agent.
2. Start Hermes from the repository directory.
3. Review the project skill, then run `hermes skills trust` to enable project-local skills.
4. Resolve `atlas-ai.yaml` and `integrations/hermes-agent/adapter.yaml` before governed execution.
5. Invoke `/atlas-os <request>`, or let Hermes select the skill when a task calls for ATLAS governance.
6. Use `hermes-agent` as the runtime surface identifier.

The skill deliberately has no operating-system restriction. Hermes may execute locally, in a container, over SSH, or on remote infrastructure without changing ATLAS semantics. See the [Hermes Agent adapter notes](../integrations/hermes-agent/README.md) for human guidance.

## Any AI host

For any AI host that supports the cross-tool Agent Skills convention, expose [`.agents/skills/atlas-os/`](../.agents/skills/atlas-os/) as a project or user skill directory. Keep the repository available because the skill resolves the canonical machine contracts from the checkout.

For a host without skill discovery:

1. Load `atlas-ai.yaml`, then `atlas-os.yaml`, then only the machine contracts needed for the task.
2. Map the host's tools, approvals, and storage through [`integrations/generic-ai-host/adapter.yaml`](../integrations/generic-ai-host/adapter.yaml).
3. Add the project skill's instructions to the host's system, project, or agent instructions only as a human/LLM compatibility layer.
4. Use a stable lowercase host identifier when creating an `ExecutionEnvelope` or dashboard.

Hosts that can run Python may optionally call:

```python
from atlas_runtime import ExecutionEnvelope, execute

result = execute(ExecutionEnvelope(
    objective="Handle the user's request",
    plan_id="plan-request",
    work_units=({"id": "respond", "status": "PENDING", "dependencies": []},),
    surface="my-ai-tool",
))
```

This interface selects the governed next unit; the AI host still performs the actual reasoning and tool use.

## Uninstall or disable

Remove or disable the host instruction, Library snapshot, or project/user skill. No device operating system files, boot configuration, or hardware drivers are replaced by ATLAS-OS.
