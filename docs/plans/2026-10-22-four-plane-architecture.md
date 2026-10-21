# Four-Plane ATLAS Architecture Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Mission Control, Control Plane, Dashboard/Observability, and Domain Intelligence first-class, machine-readable ATLAS-OS architectural authorities without replacing the existing execution spine.

**Architecture:** Add a required top-level `architecture` map to `atlas-os.yaml` that binds the four recommended architectural authorities. Keep the current execution spine as the sequential workflow; Mission Control is the human command boundary, Control Plane owns machine authority and state transitions, Domain Intelligence owns governed semantic/evidentiary context, and Observability owns read-only telemetry with Dashboard as its presentation projection.

**Tech Stack:** YAML machine contracts, JSON Schema 2020-12, Python 3 repository validators/tests, GitHub Actions.

## Global Constraints

- All new authoritative controls must be machine-readable and discoverable through `atlas-ai.yaml`.
- Markdown remains non-authoritative human guidance.
- Preserve the existing execution-spine stage sequence and runtime behavior unless a test demonstrates an architectural boundary violation.
- Mission Control may request actions but cannot bypass Control Plane authorization, host permissions, safety constraints, immutable invariants, or non-waivable evidence requirements.
- Dashboard/Observability is derived/read-oriented state and must not be an authority for execution-state mutation.
- Domain Intelligence must distinguish taxonomy, classification, ontology, binding requirements, standards/practices, benchmarks, and evidence hierarchy.
- Existing `spec/classification.yaml` and `spec/domain-practices.yaml` remain specialized subordinate contracts rather than being duplicated.
- Existing external release blockers `MIG-029` and `MIG-037` remain open unless genuine independent host evidence is obtained.

---

### Task 1: Declare and validate the four architectural authorities

**Files:**
- Create: `tests/conformance/test_architecture_contracts.py`
- Create: `spec/mission-control.yaml`
- Create: `spec/control-plane.yaml`
- Create: `spec/observability.yaml`
- Create: `spec/domain-intelligence.yaml`
- Modify: `atlas-os.yaml`
- Modify: `atlas-ai.yaml`
- Modify: `schemas/atlas-os.schema.json`
- Modify: `schemas/ai-manifest.schema.json`

**Interfaces:**
- Consumes: current product authority in `atlas-os.yaml`, current AI discovery contract in `atlas-ai.yaml`.
- Produces: `atlas-os.yaml#/architecture/{mission_control,control_plane,observability,domain_intelligence}` and matching AI discovery authority pointers.

- [ ] **Step 1: Add the focused failing test**

Assert that `atlas-os.yaml` has the four exact architecture bindings, `atlas-ai.yaml` exposes the same authority paths, and each referenced spec is active, normative, and machine-discovered.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: non-zero exit because the top-level architecture bindings and four specs do not yet exist.

- [ ] **Step 3: Implement the minimum behavior**

Add the top-level architecture map, schema support, AI discovery pointers, and four normative specs with explicit ownership/non-ownership boundaries.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: zero exit.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate/validate_machine_contracts.py .`
Expected: pass with exact machine-contract discovery coverage.

- [ ] **Step 6: Commit the passing deliverable**

Commit the task as a coherent architecture-authority change.

### Task 2: Add machine contracts for commands, control state, telemetry, and domain intelligence

**Files:**
- Create: `schemas/mission-command.schema.json`
- Create: `schemas/control-plane-state.schema.json`
- Create: `schemas/control-receipt.schema.json`
- Create: `schemas/telemetry-event.schema.json`
- Create: `schemas/metric.schema.json`
- Create: `schemas/domain-intelligence-snapshot.schema.json`
- Create: `schemas/domain-ontology.schema.json`
- Create: `schemas/benchmark.schema.json`
- Create: `registries/mission-commands.yaml`
- Create: `registries/metrics.yaml`
- Create: `registries/ontologies.yaml`
- Create: `registries/benchmarks.yaml`
- Create: `registries/evidence-hierarchies.yaml`
- Modify: `tests/conformance/test_architecture_contracts.py`
- Modify: `atlas-ai.yaml`

**Interfaces:**
- Consumes: the four authority specs from Task 1.
- Produces: schema-valid command, control-state/receipt, telemetry/metric, ontology, benchmark, evidence-hierarchy, and domain-intelligence snapshot contracts.

- [ ] **Step 1: Add the focused failing test**

Assert that every new schema/registry exists, is machine-discovered, and that representative records validate against their declared schemas.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: non-zero exit for missing schemas/registries.

- [ ] **Step 3: Implement the minimum behavior**

Define the schemas and registries with explicit IDs, lifecycle/status values, provenance/evidence fields, and read-only observability semantics.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: zero exit.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate/validate_machine_contracts.py .`
Expected: pass and exact discovery coverage including all newly added structured authorities.

- [ ] **Step 6: Commit the passing deliverable**

Commit the machine-contract layer independently.

### Task 3: Enforce architectural boundaries and remap the existing dashboard/domain contracts

**Files:**
- Modify: `spec/dashboard.yaml`
- Modify: `spec/classification.yaml`
- Modify: `spec/domain-practices.yaml`
- Modify: `spec/core.yaml`
- Modify: `spec/execution-spine.yaml`
- Modify: `tools/validate/validate_machine_contracts.py`
- Modify: `tests/conformance/test_architecture_contracts.py`

**Interfaces:**
- Consumes: four-plane architecture contracts plus existing execution/classification/domain-practice specs.
- Produces: validator-enforced boundaries: Dashboard derives state only; Mission Control commands flow through Control Plane; Domain Intelligence composes classification/domain-practice authorities without silently replacing them.

- [ ] **Step 1: Add the focused failing test**

Assert that Dashboard declares read-only/derived semantics, execution-spine routing references Control Plane authority, and classification/domain-practices declare Domain Intelligence as their parent composition layer.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: non-zero exit because current specs do not expose the new boundaries.

- [ ] **Step 3: Implement the minimum behavior**

Update specs and extend `validate_machine_contracts.py` to fail when any architecture pointer is absent, points to a non-normative spec, is omitted from AI discovery, or Dashboard is declared as an execution-state authority.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_architecture_contracts`
Expected: zero exit.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate/validate_machine_contracts.py . && python tools/validate/validate_repository.py . && python tools/validate/validate_output_contracts.py .`
Expected: all validators pass.

- [ ] **Step 6: Commit the passing deliverable**

Commit the boundary-enforcement and compatibility mapping.

### Task 4: Publish the candidate revision and verify the full repository

**Files:**
- Modify: `atlas-os.yaml`
- Modify: `atlas-ai.yaml`
- Modify: release-verification YAMLs and migration target metadata that bind to candidate identity where required by existing validators.
- Modify: `README.md` and `docs/architecture.md` as human renderings of the machine authority.

**Interfaces:**
- Consumes: passing architecture contracts from Tasks 1-3.
- Produces: a single coherent candidate identity and documented architecture with no fabricated external verification evidence.

- [ ] **Step 1: Add/extend the identity regression assertion**

Assert that product version/control revision remain consistent across product manifest, AI manifest, release-verification contracts, and any migration proof targets governed by the current candidate.

- [ ] **Step 2: Verify any relevant failure before identity update**

Run the focused conformance test and machine validator after changing the candidate identity; expect drift failures until all governed identity references are updated.

- [ ] **Step 3: Implement the minimum behavior**

Advance the candidate revision, update all machine-bound identity references consistently, and update human architecture documentation without changing the status of `MIG-029` or `MIG-037`.

- [ ] **Step 4: Verify focused pass**

Run: `python -m unittest discover -s tests -p 'test_*.py'`
Expected: all tests pass.

- [ ] **Step 5: Run the full validation/release-readiness checks**

Run: `python tools/validate/validate_repository.py . && python tools/validate/validate_machine_contracts.py . && python tools/validate/validate_output_contracts.py . && python tools/package/build_release.py . dist`
Expected: all checks pass; release remains candidate if external blockers remain open.

- [ ] **Step 6: Commit the passing deliverable**

Commit the candidate identity/documentation update and merge only after CI is green.

## Unresolved Product Decisions

None. The approved architecture and existing ATLAS fail-closed governance settle the externally observable behavior for this migration.