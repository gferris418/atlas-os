# Hermes Agent adapter

Hermes Agent consumes ATLAS-OS as an AI-host skill, not as a device operating system. The portable project skill is [`.agents/skills/atlas-os/SKILL.md`](../../.agents/skills/atlas-os/SKILL.md), and the runtime surface identifier is `hermes-agent`.

- **Startup:** start Hermes inside the trusted repository checkout so it discovers the project-local skill.
- **Native-first behavior:** use Hermes' model, conversation, tools, memory, skills, subagents, terminal backends, and messaging gateway directly when they are actually available.
- **Planning and evidence:** apply the ATLAS execution spine before tool use and preserve evidence classes, plan state, and verification results.
- **Persistence:** Hermes memory or skill storage is not automatically the canonical ATLAS library. Report `CAPABILITY_UNAVAILABLE` unless an authorized durable adapter writes and verifies the required record.
- **Approvals:** Hermes tool or command approval never weakens ATLAS authorization requirements; both applicable boundaries must pass.
- **Portability:** do not add a `platforms` restriction to the ATLAS skill. The adapter semantics are identical across local, container, SSH, and remote Hermes runtimes.
- **Unsupported claims:** do not claim that tools, memory, Python, filesystem access, or external systems exist until the active Hermes session exposes them.

Repository-local tests prove only the shared adapter seam. A live Hermes session is required for independent host-conformance evidence.
