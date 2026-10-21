# Install ATLAS-OS in an AI host

ATLAS-OS is an execution-governance layer for AI agents. It is not a device operating system, a bootable image, or a Windows/macOS/Linux customization. Installation means making the canonical ATLAS contract available to an AI host and configuring that host to apply it. The same repository works from a browser-only service, a desktop agent, a terminal agent, a container, or a remote server.

## Portable installation contract

Every installation in any AI host must:

1. Resolve [`atlas-os.yaml`](../atlas-os.yaml) as the product and release authority.
2. Apply the active contracts under [`spec/`](../spec/) without copying or redefining their semantics.
3. Use the host's native model, conversation, tools, storage, and approval mechanisms when available.
4. Report unavailable capabilities rather than pretending an action, save, or verification occurred.
5. Identify the host with a lowercase surface slug such as `chatgpt`, `hermes-agent`, or `my-ai-tool`.
6. Preserve user authorization, evidence, verification, persistence, and specialist-boundary controls.

The Python runtime is an optional conformance reference. An AI host can apply ATLAS directly from the specifications even when it cannot execute Python.

## ChatGPT

Use one of these supported patterns:

- Attach the repository to a Project or conversation and identify [`atlas-os.yaml`](../atlas-os.yaml) as the authority.
- Paste or upload [`ATLAS-CHATGPT-INSTRUCTIONS.md`](../integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md) when the full repository is not available.
- Install a verified repository snapshot in ChatGPT Library by following [`chatgpt-library-install.md`](chatgpt-library-install.md).

The compatibility profile is a compact bootstrap, not a competing ATLAS definition.

## Hermes Agent

This repository includes a platform-neutral project skill at [`.agents/skills/atlas-os/SKILL.md`](../.agents/skills/atlas-os/SKILL.md). Hermes Agent discovers `.agents/skills/` when it starts inside a Git checkout.

1. Clone or open this repository from any environment supported by Hermes Agent.
2. Start Hermes from the repository directory.
3. Review the project skill, then run `hermes skills trust` to enable project-local skills.
4. Invoke `/atlas-os <request>`, or let Hermes select the skill when a task calls for ATLAS governance.
5. Use `hermes-agent` as the runtime surface identifier.

The skill deliberately has no operating-system restriction. Hermes may execute locally, in a container, over SSH, or on remote infrastructure without changing ATLAS semantics. See the [Hermes Agent adapter notes](../integrations/hermes-agent/README.md) for capability and approval boundaries.

## Any AI host

For any AI host that supports the cross-tool Agent Skills convention, expose [`.agents/skills/atlas-os/`](../.agents/skills/atlas-os/) as a project or user skill directory. Keep the repository available because the skill resolves the canonical manifest and specifications from the checkout.

For a host without skill discovery:

1. Add the project skill's instructions to the host's system, project, or agent instructions.
2. Attach or retrieve `atlas-os.yaml` and only the specifications needed for the current task.
3. Map the host's tools, approvals, and storage through the generic adapter contract in [`integrations/generic-ai-host/README.md`](../integrations/generic-ai-host/README.md).
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
