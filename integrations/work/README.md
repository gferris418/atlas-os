# ChatGPT Work adapter

## Discovery order

`atlas-os.yaml -> core specifications -> registries -> this contract -> active controls -> work execution`

## Contract

- **Capabilities:** multi-stage task execution, connected applications, artifact generation, and durable outputs when exposed.
- **Limitations:** connectors, approvals, and persistence boundaries differ by workspace and task.
- **Tool model:** use native application operations for structured data and external actions; verify resulting state.
- **Persistence model:** distinguish active work state from explicitly saved canonical library artifacts.
- **Approval behavior:** obtain scoped approval for publication, messages, permission changes, destructive actions, and other high-impact writes.
- **Startup behavior:** load current authority, reconcile resumed state, and expose a compact dashboard for substantive work.
- **Unsupported behavior:** do not assume repository execution or a connector that is not present.
- **Conformance:** candidate pending independent bootstrap and latest-control propagation proof.

