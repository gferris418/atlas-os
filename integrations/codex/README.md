# Codex adapter

## Discovery order

1. Read `atlas-os.yaml`.
2. Read the core specifications relevant to the task.
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
- **Startup behavior:** locate repository instructions, inspect status, classify the task, select proportional depth, and expose compact dashboard state for substantive work.
- **Unsupported behavior:** Codex cannot manufacture proof from ChatGPT or Work surfaces.
- **Conformance:** candidate; repository-local behaviors are testable, while MIG-029 and MIG-037 require independent evidence.

Codex-specific instructions remain subordinate to the ATLAS core and must not fork its meaning.

