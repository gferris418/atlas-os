# ATLAS artifact model

ATLAS uses four lightweight layers. An artifact is created only when it has a distinct operational purpose; a simple request does not require every artifact type.

| Layer | Artifact | Purpose |
|---|---|---|
| Governance | Framework | Principles, concepts, roles, stages, and decision logic for approaching a domain. |
| Governance | Policy | Mandatory rules describing what is required or prohibited. |
| Governance | Standard | Testable requirements for quality, technical behavior, or interoperability. |
| Governance | Protocol | Interaction sequence, required messages, validation, and failure behavior between systems. |
| Governance | Schema | Machine-readable representation and validation constraints. |
| Governance | Taxonomy | Controlled categories, codes, labels, and relationships. |
| Execution guidance | Methodology | Disciplined analytical method operating inside a framework. |
| Execution guidance | Playbook | Reusable, branching guidance for a recurring situation. |
| Execution guidance | SOP | Exact ordered procedure for a stable, repeatable operation. |
| Execution guidance | Checklist | Compact confirmation that required items or gates were completed. |
| Live execution | Plan | Dependency-ordered intended work for one objective. |
| Live execution | Workflow | The actual task instance, states, owners, dependencies, and evidence. |
| Live execution | Approval | Authorization bound to a governed action scope. |
| Live execution | Receipt | Verifiable evidence that a handoff, action, or persistence operation occurred. |
| Implementation | Runtime | Executable enforcement of ATLAS contracts. |
| Implementation | Adapter | Translation between ATLAS contracts and a host surface, tool, or store. |
| Implementation | Skill | Packaged instructions and capabilities for a defined task. |
| Implementation | Runbook | Operational startup, monitoring, incident, and recovery instructions. |
| Implementation | Template | Reusable output or record shape. |

## Selection rule

Use the smallest sufficient set:

- direct work may need only a result and a lightweight check;
- recurring judgment-heavy work benefits from a playbook;
- stable repeatable operations use an SOP;
- cross-system exchange uses a protocol and schema;
- a live nontrivial task uses one ATLAS plan and workflow;
- a specialist domain method may supply methodology and domain decisions, but it does not create a second execution spine, planner, or approval authority.

## Specialist activation

ATLAS never activates a specialist from raw keyword matching alone. Classification and planning first produce an explicit structured capability requirement. `route_domain_method` consumes the complete active domain-method registry, validates governance ownership, and always requires an acceptable Domain Context Handoff. A registration cannot opt out of handoff validation, and `BLOCKED` handoffs cannot activate dependent execution.

When a handoff or approval crosses into a specialist runtime, ATLAS emits a detached Ed25519 attestation over the complete record. The specialist verifies that signature with an operator-pinned public key; the payload SHA-256 remains an integrity and correlation value, not an authenticity claim.
