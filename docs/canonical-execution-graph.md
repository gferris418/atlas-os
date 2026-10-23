# 1. ATLAS Canonical Execution Graph (ACEG)

## 1.1 Purpose
ACEG is the generic ATLAS structural-integrity and workflow-governance layer for governed workflows and playbooks. It prevents an executor from silently deleting, duplicating, reordering or inventing canonical workflow elements during execution.

## 1.2 Identity model
Every substantive workflow element has three separate identifiers.

### 1.2.1 Stable ID
The permanent semantic identity of the node, such as `ATLAS-CLASSIFY-PRODUCT`.

### 1.2.2 Serial number
The human-readable execution position, such as `04.04`.

### 1.2.3 Workflow version
The version of the canonical manifest being executed.

### 1.2.4 Identity rule
Stable IDs preserve meaning across versions. Serial numbers express process position and may change only through a governed versioned manifest change.

# 2. Numbering integrity

## 2.1 Every substantive node is numbered.

## 2.2 Every substantive subitem is hierarchically numbered.

## 2.3 Sibling sequences are contiguous from one.

## 2.4 Child serials must extend the parent serial.

## 2.5 Missing, duplicate or unknown serials are structural failures.

## 2.6 A non-applicable step remains present as `NOT_APPLICABLE`; it is not silently omitted.

# 3. Node governance contract

## 3.1 Stable structural fields
Each node declares `stable_id`, `serial`, `title` and `kind`.

## 3.2 Criticality
A node may declare `CRITICAL`, `MAJOR`, `MINOR` or `INFORMATIONAL` criticality so integrity failures can be triaged without treating all omissions as equivalent.

## 3.3 Owner
A node may declare the authority responsible for the step, such as `ATLAS_OS` or `ARGUS`. Ownership metadata does not transfer authority beyond the canonical ATLAS/ARGUS boundary.

## 3.4 Condition
Conditional and optional nodes may declare the condition that governs applicability. A false condition produces an explicit runtime state rather than silent deletion.

## 3.5 Input schema reference
A node may declare the contract for inputs it is allowed to consume.

## 3.6 Output schema reference
A node may declare the contract for outputs it is allowed to return.

## 3.7 Evidence requirement
A node may declare its minimum evidence requirement. Completing the step does not require inventing a result when the evidence threshold is not met.

## 3.8 Allowed statuses
A node may narrow the runtime statuses that are valid for that step. ATLAS rejects a transition to a status outside the node contract.

# 4. Dependency integrity

## 4.1 Serial order is the default human process flow.

## 4.2 Explicit dependencies are the machine execution constraint.

## 4.3 Parallel branches are allowed only where dependencies permit them.

## 4.4 Dependency cycles are invalid.

## 4.5 A node cannot complete while a required dependency remains unresolved.

# 5. Runtime states

## 5.1 `PENDING`

## 5.2 `ACTIVE`

## 5.3 `COMPLETE`

## 5.4 `BLOCKED`

## 5.5 `FAILED`

## 5.6 `NOT_APPLICABLE`

## 5.7 `SKIPPED_WITH_AUTHORITY`

## 5.8 `SUPERSEDED`

# 6. Integrity gates

## 6.1 Preflight
ATLAS validates workflow identity, version, stable-ID uniqueness, serial uniqueness, sibling continuity, parent-child alignment, dependency resolution, acyclic dependencies and declared governance metadata.

## 6.2 Runtime
ATLAS validates that the current node exists in the manifest, required dependencies are resolved and the requested runtime status is permitted by the node contract.

## 6.3 Postflight
ATLAS reconciles the canonical graph against observed execution and reports missing, unknown, duplicate and serial-mismatched nodes.

# 7. Unknowns and evidence

## 7.1 Completing research does not require inventing an answer.

## 7.2 A domain playbook may define valid outputs such as `UNKNOWN`, `NOT_OBSERVED`, `INSUFFICIENT_EVIDENCE` or `CONFLICTING_EVIDENCE`.

## 7.3 Evidence semantics belong to the declaring playbook; structural and declared-status enforcement belong to ATLAS.

# 8. Manifest fingerprint

## 8.1 ACEG generates a deterministic SHA-256 fingerprint from the workflow identity, version, canonical node structure and declared governance metadata.

## 8.2 Fingerprinted metadata includes criticality, owner, condition, input/output schema references, evidence requirements and allowed statuses when declared.

## 8.3 The fingerprint identifies the exact graph used for an execution and supports manifest-drift detection.

# 9. ATLAS and playbook boundary

## 9.1 ATLAS owns the generic graph engine, structural validation, governance-metadata validation, allowed-status enforcement, reconciliation and fingerprinting.

## 9.2 ARGUS and other playbooks own their domain-specific node definitions, dependencies, evidence requirements and outputs.

## 9.3 Runtime executors may request a canonical extension but may not invent a new canonical step during execution.

## 9.4 Access Asia bid, project-delivery, invoice, payment and accounting state machines remain outside ATLAS core.

# 10. Integrity interpretation

## 10.1 Structural integrity
Confirms that the declared numbered process structure was followed.

## 10.2 Dependency integrity
Confirms that prerequisite relationships were satisfied.

## 10.3 Schema integrity
Confirms that declared input/output contracts were respected by the playbook or capability layer responsible for semantic execution.

## 10.4 Evidence integrity
Confirms that factual conclusions meet the declaring playbook's evidence requirements.

## 10.5 Authority integrity
Confirms that the actor or playbook making a transition is authorized under ATLAS governance.

## 10.6 Truth limitation
A structurally valid sequence does not by itself prove that its content is true. ACEG therefore complements, rather than replaces, evidence, semantic, schema and authority controls.
