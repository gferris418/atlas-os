# 1. ATLAS Canonical Execution Graph (ACEG)

## 1.1 Purpose
ACEG is the generic ATLAS structural-integrity layer for governed workflows and playbooks. It prevents an executor from silently deleting, duplicating, reordering or inventing canonical workflow elements during execution.

## 1.2 Identity model
Every substantive workflow element has three separate identifiers:

### 1.2.1 Stable ID
The permanent semantic identity of the node, such as `ATLAS-CLASSIFY-PRODUCT`.

### 1.2.2 Serial number
The human-readable execution position, such as `04.04`.

### 1.2.3 Workflow version
The version of the canonical manifest being executed.

Stable IDs preserve meaning across versions. Serial numbers express process position and may change only through a governed versioned manifest change.

# 2. Numbering integrity

## 2.1 Every substantive node is numbered.

## 2.2 Every substantive subitem is hierarchically numbered.

## 2.3 Sibling sequences are contiguous from one.

## 2.4 Child serials must extend the parent serial.

## 2.5 Missing, duplicate or unknown serials are structural failures.

## 2.6 A non-applicable step remains present as `NOT_APPLICABLE`; it is not silently omitted.

# 3. Dependency integrity

## 3.1 Serial order is the default human process flow.

## 3.2 Explicit dependencies are the machine execution constraint.

## 3.3 Parallel branches are allowed only where dependencies permit them.

## 3.4 Dependency cycles are invalid.

## 3.5 A node cannot complete while a required dependency remains unresolved.

# 4. Runtime states

## 4.1 `PENDING`
## 4.2 `ACTIVE`
## 4.3 `COMPLETE`
## 4.4 `BLOCKED`
## 4.5 `FAILED`
## 4.6 `NOT_APPLICABLE`
## 4.7 `SKIPPED_WITH_AUTHORITY`
## 4.8 `SUPERSEDED`

# 5. Integrity gates

## 5.1 Preflight
ATLAS validates workflow identity, version, stable-ID uniqueness, serial uniqueness, sibling continuity, parent-child alignment, dependency resolution and acyclic dependencies.

## 5.2 Runtime
ATLAS validates that the current node exists in the manifest and that required dependencies are resolved before terminal completion.

## 5.3 Postflight
ATLAS reconciles the canonical graph against observed execution and reports missing, unknown, duplicate and serial-mismatched nodes.

# 6. Unknowns and evidence

## 6.1 Completing research does not require inventing an answer.

## 6.2 A domain playbook may define valid outputs such as `UNKNOWN`, `NOT_OBSERVED`, `INSUFFICIENT_EVIDENCE` or `CONFLICTING_EVIDENCE`.

## 6.3 Evidence semantics belong to the declaring playbook; structural validation belongs to ATLAS.

# 7. Manifest fingerprint

## 7.1 ACEG generates a deterministic SHA-256 fingerprint from the workflow identity, version and canonical node structure.

## 7.2 The fingerprint identifies the exact graph used for an execution and supports manifest-drift detection.

# 8. ATLAS and playbook boundary

## 8.1 ATLAS owns the generic graph engine and structural validation.

## 8.2 ARGUS and other playbooks own their domain-specific node definitions, dependencies, evidence requirements and outputs.

## 8.3 Runtime executors may request a canonical extension but may not invent a new canonical step during execution.

## 8.4 Access Asia bid, project-delivery, invoice, payment and accounting state machines remain outside ATLAS core.
