# Codex adapter

## Discovery order

1. Read `atlas-os.yaml`.
2. Read the core specifications relevant to the task, including domain-practice alignment.
3. Load applicable capability, tool, skill, control, and migration registries.
4. Apply this surface contract.
5. Reconcile active migration/control state.
6. Execute, verify, persist deliberately, and report evidence.

## Contract

- **Capabilities:** repository inspection and editing, command execution, tests, version control, connected capabilities exposed to the session.
- **Limitations:** network, credentials, sandbox, and external-system access remain environment-specific.
- **Tool model:** prefer repository-native commands and structured tools; preserve exit status and distinguish generated from executed and verified.
- **Persistence model:** repository files are canonical only when committed through the governed change process; task notes are not automatically canonical.
- **Approval behavior:** respect platform and repository approval boundaries; external publication requires user authority.
- **Native-first behavior:** use Codex repository understanding, coding, command execution, and exposed tools directly; ATLAS adds controls only where they materially improve the result.
- **Startup behavior:** locate repository instructions, inspect status, select proportional depth, initialize the compact dashboard for every prompt, execute one active atomic unit at a time, and resolve classification or standards only when material.
- **Output behavior:** honor explicit user formats, otherwise select the smallest task-fit output profile; verify files, commands, and artifacts before delivery.
- **Unsupported behavior:** Codex cannot manufacture proof from ChatGPT or Work surfaces.
- **Conformance:** candidate; repository-local behaviors are testable, while MIG-029 and MIG-037 require independent evidence.
- **Executable seam:** `get_surface_adapter("codex")` validates a concrete plan, initializes dashboard state, and can deliver through the verified filesystem library adapter.

Codex-specific instructions remain subordinate to the ATLAS core and must not fork its meaning.

