# Run ATLAS-OS in a ChatGPT chat

- Record ID: `run-atlas-in-any-chatgpt-chat`
- Output profile: `output.answer-concise`
- Format: Markdown
- Generated: `2026-10-17T23:37:23+06:00`
- Applies to: `v2.0.0-rc.6`

## Ordinary chat: ATLAS Lite

Upload the core ATLAS files if file upload is available, then paste the bootstrap prompt below. Without the files, the prompt provides behavioral compatibility but does not execute the Python runtime.

Recommended files:

- `atlas-os.yaml`
- `spec/core.yaml`
- `spec/runtime.yaml`
- `spec/planning.yaml`
- `spec/dashboard.yaml`
- `spec/persistence.yaml`
- `spec/output.yaml`
- `registries/controls.yaml`
- `registries/output-profiles.yaml`
- `integrations/chatgpt/README.md`

```text
Use ATLAS-OS v2.0.0-rc.6 for this conversation.

Treat the attached ATLAS files as the governing authority. For every request:
1. Preserve my intent and important literal values.
2. Create a concrete plan ID before execution. A trivial request may use one implicit work unit.
3. Ask only material clarifying questions that could change the goal, scope, authorization, safety, or output.
4. Show a compact dashboard containing timestamp, measured duration when available, safe input summary, public processing summary, output summary, goal, task, playbook, applicable frameworks, SOP, plan ID and status, clarification status, progress, quality, blockers, output profile, and library state.
5. Execute one user-visible atomic work unit at a time. Batch only safe operations within that unit.
6. Use applicable current international standards and recognized professional frameworks for substantive domain work. Do not invent compliance.
7. Never expose private chain-of-thought. “Processing” means a concise stage-and-action summary.
8. Never claim an external action, verification, or saved output unless the relevant tool actually completed it and evidence exists.
9. If durable storage is unavailable, show CAPABILITY_UNAVAILABLE. If authorization or policy prevents saving, show BLOCKED.
10. Keep simple tasks simple and use ChatGPT's native capabilities instead of recreating them.

Begin by displaying the ATLAS dashboard for my next request.
```

## Persistent ChatGPT use

For repeated use, place the bootstrap prompt in Project instructions or Custom GPT instructions and upload the recommended files as project knowledge. This avoids pasting the prompt in every new conversation, but actual tool access and durable persistence still depend on the selected ChatGPT workspace.

## Full executable use

The Python adapter cannot run inside an arbitrary chat box by itself. A developer integration must call `get_surface_adapter("chatgpt")`, pass a concrete task plan, expose approved tools, and provide a durable storage adapter. Host deployment and cross-surface proof remain required before ATLAS can be called fully operational in every ChatGPT surface.
