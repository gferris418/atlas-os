# ChatGPT adapter

## Discovery order

`atlas-os.yaml -> core specifications -> applicable registries -> this contract -> active controls -> task execution`

For immediate use in a ChatGPT Project, Custom GPT, or ordinary chat, paste or upload [`ATLAS-CHATGPT-INSTRUCTIONS.md`](ATLAS-CHATGPT-INSTRUCTIONS.md). It is the version-bound compatibility profile; the full repository remains the higher authority when attached.

When a verified ATLAS snapshot is installed in ChatGPT Library, use that pinned Library copy as the normal runtime cache instead of refetching GitHub on every startup. The snapshot must preserve the exact source commit and keep `atlas-os.yaml` as version authority. GitHub remains the update/source-development origin. See [`docs/chatgpt-library-install.md`](../../docs/chatgpt-library-install.md) for the artifact and synchronization contract.

## Contract

- **Capabilities:** conversation, tool use when exposed, connected private sources when authorized, public research, artifact delivery.
- **Limitations:** capability availability and persistence vary by session; repository filesystem access is not assumed.
- **Tool model:** route through the active tool/connector catalog and record actual execution evidence.
- **Persistence model:** separate conversational task state from explicitly durable library artifacts.
- **Approval behavior:** require scoped approval for material external writes and high-impact actions.
- **Native-first behavior:** use ChatGPT's conversation, language understanding, generation, and exposed tool orchestration directly; ATLAS adds controls only where they materially improve the result.
- **Startup behavior:** initialize the compact dashboard for every prompt; use one active atomic unit for nontrivial work and resolve domain standards only when material.
- **Output behavior:** honor explicit user formats, otherwise select the smallest task-fit output profile and validate only material requirements.
- **Library bootstrap behavior:** if a verified Library snapshot exists, load it first for routine execution; do not poll GitHub unless the user explicitly asks to install, update, or synchronize ATLAS-OS.
- **Update behavior:** for private-repository updates, prefer the latest successful `main` workflow artifact named `atlas-os-main-snapshot`, verify its checksums and source commit, then replace the Library snapshot with read-back evidence.
- **Unsupported behavior:** do not claim repository commands, writes, or connected-source access unless the surface exposes and executes them.
- **Conformance:** candidate; independent bootstrap and propagation proof remain open.
- **Executable seam:** `get_surface_adapter("chatgpt")` validates a concrete plan, initializes dashboard state, and reports unavailable persistence unless the host supplies an authorized durable adapter.

