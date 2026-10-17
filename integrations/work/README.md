# ChatGPT Work adapter

## Discovery order

`atlas-os.yaml -> core specifications -> registries -> this contract -> active controls -> work execution`

## Contract

- **Capabilities:** multi-stage task execution, connected applications, artifact generation, and durable outputs when exposed.
- **Limitations:** connectors, approvals, and persistence boundaries differ by workspace and task.
- **Tool model:** use native application operations for structured data and external actions; verify resulting state.
- **Persistence model:** distinguish active work state from explicitly saved canonical library artifacts.
- **Approval behavior:** obtain scoped approval for publication, messages, permission changes, destructive actions, and other high-impact writes.
- **Native-first behavior:** use ChatGPT Work's multi-stage execution, applications, and artifact capabilities directly; ATLAS adds controls only where they materially improve the result.
- **Startup behavior:** load current authority, reconcile resumed state, initialize the compact dashboard for every prompt, execute one active atomic unit at a time, and resolve domain standards only when material.
- **Output behavior:** honor explicit user formats, otherwise select the smallest task-fit output profile and validate delivered artifacts through native application state.
- **Unsupported behavior:** do not assume repository execution or a connector that is not present.
- **Conformance:** candidate pending independent bootstrap and latest-control propagation proof.
- **Executable seam:** `get_surface_adapter("work")` validates a concrete plan, initializes dashboard state, and reports unavailable persistence unless the workspace supplies an authorized durable adapter.

