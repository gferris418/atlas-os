# Run ATLAS-OS in a ChatGPT chat

- Record ID: `run-atlas-in-any-chatgpt-chat`
- Output profile: `output.answer-concise`
- Format: Markdown
- Generated: `2026-10-17T23:57:16+06:00`
- Applies to: `v2.0.0-rc.7`

## Ordinary chat: ATLAS Lite

Paste or upload `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`, then send the task. That single file provides the version-bound ChatGPT compatibility profile; it does not claim to execute the Python runtime.

For full repository authority, also upload the core ATLAS files when file upload is available:

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

## Persistent ChatGPT use

For repeated use, paste `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md` into Project instructions or Custom GPT instructions. Upload the recommended files as project knowledge when full repository authority is required. This avoids pasting the prompt in every new conversation, but actual tool access and durable persistence still depend on the selected ChatGPT workspace.

## Full executable use

The Python adapter cannot run inside an arbitrary chat box by itself. A developer integration must call `get_surface_adapter("chatgpt")`, pass a concrete task plan, expose approved tools, and provide a durable storage adapter. Host deployment and cross-surface proof remain required before ATLAS can be called fully operational in every ChatGPT surface.
