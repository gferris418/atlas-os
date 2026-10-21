# Generic AI-host adapter

Any AI assistant or agent can host ATLAS-OS when it can receive the governing instructions and preserve the required execution state. The host does not need to run a particular model, device operating system, programming language, or deployment topology.

Use a stable lowercase surface identifier of 1–64 characters, for example `my-ai-tool`. The identifier may contain lowercase letters, numbers, `.`, `_`, and `-`, but must start with a letter and end with a letter or number.

An adapter must:

1. Resolve `atlas-os.yaml` and the active specifications without redefining them.
2. Map native conversation, reasoning, tools, approvals, and storage to ATLAS contracts.
3. Create a concrete plan identifier and pass the clarification gate before execution.
4. Before routing any native function, skill, plugin, tool, model, subagent, or specialist method, display the exact digest-bound routing preview with what will be done, how, permission, data scope, prerequisites, fallback, and unresolved gates. Route only the exact approved proposal.
5. Expose capability gaps and failures explicitly.
6. Verify results and durable writes before reporting completion or `SAVED`.
7. Keep provider-specific behavior outside the normative core.

The shared executable seam is `get_surface_adapter("my-ai-tool")`. Registration documents known hosts and their capabilities, but an unregistered host slug remains valid so provider support does not require a core release.
