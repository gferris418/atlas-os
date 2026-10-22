# Install ATLAS-OS in an AI host

ATLAS-OS is a portable AI operating and governance layer. It is not a device operating system, bootable image, or replacement for a host model. Installation means making the canonical ATLAS contracts available to an AI host and configuring that host to enter the ATLAS orchestration seam before substantive execution.

The same architecture is intended for ChatGPT, Hermes Agent, Claude, Codex, browser agents, terminal agents, containers, remote servers and other compatible AI systems.

## Portable installation contract

Every conformant installation must:

1. Resolve [`atlas-ai.yaml`](../atlas-ai.yaml) as the machine discovery entrypoint and [`atlas-os.yaml`](../atlas-os.yaml) as product/release authority.
2. Resolve the host's schema-valid `integrations/<surface>/adapter.yaml` from [`registries/surfaces.yaml`](../registries/surfaces.yaml).
3. Apply the active contracts under [`spec/`](../spec/) without copying or redefining their semantics.
4. Enter ATLAS through the portable orchestration seam before substantive execution.
5. Initialize or bind task/plan identity, Mission Control, Control Plane state, Observability and the compact Dashboard.
6. Preserve exactly three preprocessing steps: Understand + Normalize, Minimal Domain Framing, Route.
7. Treat `collection_mode` as ARGUS need only. For `ARGUS_COLLECTION` or `HYBRID`, obtain explicit user authorization before any ARGUS handoff or activation.
8. Pass authorization explicitly; never infer it from silence, prior tasks, previous ARGUS use or route selection.
9. Use the host's native model, conversation, tools, files, storage and UI where useful, while keeping ATLAS governance authoritative.
10. Report unavailable capabilities rather than pretending an action, save, collection or verification occurred.
11. Preserve evidence, verification, persistence, provider-admission and specialist-boundary controls.

The Python runtime is a reference implementation and conformance aid. A host may implement ATLAS directly from the machine contracts when it cannot execute Python.

## Host responsibilities

The host supplies execution capabilities such as:

- generation/reasoning;
- search/browser;
- files;
- code execution;
- databases;
- plugins/connectors/MCP servers;
- persistence;
- external actions.

ATLAS supplies:

- Mission Control semantics;
- Control Plane governance;
- task lifecycle;
- routing and approval semantics;
- explicit ARGUS authorization;
- provider admission;
- Evidence Governance;
- verification;
- persistence policy;
- delivery semantics.

The host may change presentation, not authority.

## Explicit ARGUS approval integration

A conformant adapter must maintain separate fields:

```text
routing_approval_status
argus_approval_status
routing_preview_digest
```

When the route is `ARGUS_COLLECTION` or `HYBRID`, the host must stop and obtain an explicit user decision before ARGUS runs.

For a good UX, the host may present one approval interaction such as:

```text
ATLAS requires ARGUS collection for this task.
Scope: <bounded collection mission>
Providers: <proposed providers>
Data scope: <authorized scope>
Approve ARGUS for this task? Yes / No
```

If the user approves the exact proposal, the adapter may submit both:

```text
routing_approval_status = APPROVED
argus_approval_status = APPROVED
routing_preview_digest = <the exact reviewed digest>
```

The Control Plane still treats routing approval and ARGUS authorization as separate states.

## Python reference integration

```python
from atlas_runtime import ExecutionEnvelope, execute

first = execute(ExecutionEnvelope(
    objective="ST Engineering",
    plan_id="plan-request",
    task_id="TASK-REQUEST",
    work_units=({"id": "collect", "status": "PENDING", "dependencies": []},),
    surface="my-ai-tool",
))

# If first.state == "AWAITING_APPROVAL", show the bounded proposal to the user.
# After explicit approval of that exact preview:
approved = execute(ExecutionEnvelope(
    objective="ST Engineering",
    plan_id="plan-request",
    task_id="TASK-REQUEST",
    work_units=({"id": "collect", "status": "PENDING", "dependencies": []},),
    surface="my-ai-tool",
    routing_approval_status="APPROVED",
    argus_approval_status="APPROVED",
    routing_preview_digest=first.routing_preview["digest"],
))
```

A host should not automatically turn a pending approval into approved state.

## ChatGPT

Supported patterns include:

- attach the repository to a Project/conversation and start discovery at [`atlas-ai.yaml`](../atlas-ai.yaml);
- paste or upload [`ATLAS-CHATGPT-INSTRUCTIONS.md`](../integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md) when the repository is not available;
- install a verified repository snapshot in ChatGPT Library using [`chatgpt-library-install.md`](chatgpt-library-install.md).

When repository files are available, `integrations/chatgpt/adapter.yaml` governs surface mapping and `integrations/chatgpt/release-verification.yaml` governs external proof. ChatGPT UI features may render approvals/dashboard state, but they do not become ATLAS authority.

## Hermes Agent

The repository includes [`.agents/skills/atlas-os/SKILL.md`](../.agents/skills/atlas-os/SKILL.md).

1. Clone/open this repository in an environment supported by Hermes Agent.
2. Start Hermes from the repository directory.
3. Review the project skill and trust it using Hermes' project-skill mechanism.
4. Resolve `atlas-ai.yaml` and `integrations/hermes-agent/adapter.yaml` before governed execution.
5. Invoke `/atlas-os <request>`, or allow Hermes to select the skill when appropriate.
6. Use `hermes-agent` as the runtime surface identifier.
7. Ensure the Hermes interaction layer explicitly asks the user before ARGUS activation whenever the route requires ARGUS.

Local, container, SSH or remote execution must not change ATLAS semantics.

## Claude, Codex and other hosts

For systems supporting project/user Agent Skills, expose [`.agents/skills/atlas-os/`](../.agents/skills/atlas-os/) and keep the repository accessible so the skill can resolve canonical machine contracts.

For a host without skill discovery:

1. load `atlas-ai.yaml` then `atlas-os.yaml`;
2. load only the active machine contracts necessary for the task;
3. map native host capabilities through the generic adapter contract;
4. initialize ATLAS task/control/dashboard state before substantive execution;
5. preserve the three-step preprocessing and explicit ARGUS approval boundary;
6. use a stable lowercase surface identifier.

## Conformance principle

A host is ATLAS-conformant because it preserves the canonical **state and authority semantics**, not because it reproduces a particular ChatGPT or Hermes UI.

Required invariants include:

- one ATLAS execution spine;
- one authoritative Control Plane;
- one Mission Control human-command boundary;
- exactly three preprocessing steps;
- no ARGUS activation without explicit user authorization;
- no provider self-activation;
- no invented persistence or verification;
- no host-specific redefinition of ATLAS authority.

## Disable or uninstall

Remove/disable the host instruction, project/user skill, adapter configuration or Library snapshot. ATLAS does not replace device OS files, boot configuration or hardware drivers.
