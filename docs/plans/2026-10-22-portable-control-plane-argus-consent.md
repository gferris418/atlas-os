# Portable Control Plane and ARGUS Consent Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ATLAS-OS a host-agnostic operating layer that initializes Mission Control and the Control Plane for every substantive request, preserves the three-step preprocessing flow, and requires explicit user authorization before ARGUS activation.

**Architecture:** Keep Mission Control, Control Plane, Observability, and Dashboard cross-cutting around the existing three-step preprocessing flow: Understand + Normalize -> Minimal Domain Framing -> Route. Separate ARGUS need (`collection_mode`) from ARGUS authorization (`argus_approval_status`) and activation state, while allowing one explicit user approval event to authorize the exact digest-bound routing preview and ARGUS handoff without forcing two prompts. Treat host/model/tool implementations as adapters and replaceable capability providers, never as ATLAS authority.

**Tech Stack:** Python 3.12 reference runtime, YAML normative contracts, JSON Schema, unittest, GitHub Actions.

## Global Constraints

- Pre-execution remains exactly three visible steps: UNDERSTAND_AND_NORMALIZE, MINIMAL_DOMAIN_FRAMING, ROUTE.
- Mission Control and the Control Plane initialize before substantive execution and remain cross-cutting for the task lifecycle.
- `collection_mode` remains authoritative for whether ARGUS is required; it does not constitute user authorization.
- ARGUS_COLLECTION and HYBRID require explicit user authorization before any ARGUS domain-method activation or handoff.
- A current digest-bound routing approval may carry ARGUS authorization only when the host records both statuses from the same explicit user approval event; implicit, inherited, or stale authorization is invalid.
- Original input is preserved independently from normalized intent.
- Host adapters may render ATLAS differently but may not change routing, approval, evidence, or persistence semantics.
- Existing provider admission, handoff, evidence, verification, and persistence controls remain authoritative.

---

### Task 1: Model explicit ARGUS authorization in the runtime

**Files:**
- Modify: `atlas_runtime/engine.py`
- Modify: `atlas_runtime/routing.py`
- Modify: `atlas_runtime/adapters.py`
- Modify: `atlas_runtime/cli.py`
- Test: `tests/unit/test_argus_authorization.py`

**Interfaces:**
- Consumes: `ExecutionEnvelope.routing_approval_status`, `ExecutionEnvelope.routing_preview_digest`, authoritative `request_triage.collection_mode`
- Produces: `ExecutionEnvelope.argus_approval_status`, activation contract v2, ARGUS approval gate, `AWAITING_APPROVAL` lifecycle projection

- [ ] Add focused tests proving an ARGUS route remains blocked after routing approval when ARGUS authorization is pending, and proving explicit approval permits routing.
- [ ] Observe the focused failure before production changes.
- [ ] Add `argus_approval_status` with `PENDING|APPROVED|REJECTED`, propagate it through adapters/CLI, and pass it into routing-preview construction.
- [ ] Change the activation contract to v2 with separate `argus.required`, `argus.authorization`, `argus.activation`, and mission identity while preserving provider/blocker projections.
- [ ] Gate ARGUS routing before `route_domain_method`; pending/rejected authorization must produce no ARGUS routing decision.
- [ ] Keep routing-preview digest stable across approval-status changes so the explicit approval binds the proposal rather than invalidating itself.
- [ ] Run unit and integration checks.

### Task 2: Standardize lifecycle, startup dashboard, and host portability contracts

**Files:**
- Modify: `spec/mission-control.yaml`
- Modify: `spec/control-plane.yaml`
- Modify: `spec/request-triage.yaml`
- Modify: `spec/collection-routing.yaml`
- Modify: `spec/execution-spine.yaml`
- Modify: `spec/dashboard.yaml`
- Modify: `spec/approvals.yaml`
- Modify: `spec/runtime.yaml`
- Modify: `schemas/dashboard.schema.json`

**Interfaces:**
- Consumes: runtime state and activation contract v2
- Produces: normative task lifecycle, explicit ARGUS approval boundary, portable host-adapter obligations, startup-dashboard requirements

- [ ] Add/adjust conformance assertions for required states and fields.
- [ ] Observe schema/conformance failure before changing contracts.
- [ ] Define lifecycle states CREATED, NORMALIZING, FRAMING, ROUTING, AWAITING_APPROVAL, COLLECTING, ANALYZING, VERIFYING, PERSISTING, COMPLETED, PAUSED, BLOCKED, ABORTED.
- [ ] Require dashboard initialization before substantive execution with objective, task/plan identity, progress, active stage, blocker/approval, evidence health, persistence/library state, and next action.
- [ ] Define explicit approval scope semantics and state that approval is never inferred from `collection_mode` or previous tasks.
- [ ] Define host capability/provider negotiation as an adapter concern subordinate to ATLAS authority.
- [ ] Validate schemas and conformance tests.

### Task 3: Rewrite architecture and host instructions around the portable operating-layer model

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/runtime.md`
- Modify: `docs/ai-host-installation.md`
- Modify: `docs/architecture/atlas-argus-collection-boundary.md`
- Modify: `docs/architecture/capability-layer.md`
- Modify: `.agents/skills/atlas-os/SKILL.md`
- Modify: `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`

**Interfaces:**
- Consumes: normative contracts from Tasks 1-2
- Produces: one consistent human and AI-host explanation of ATLAS portability and ARGUS consent

- [ ] Rewrite diagrams to show Experience, Control, Execution, and Adapter planes without adding preprocessing steps.
- [ ] State the invariant: ATLAS governs; ARGUS collects; tools execute; the host supplies capabilities; the user retains authority over consequential actions.
- [ ] Document that one explicit approval can authorize both the exact routing preview and ARGUS handoff when the host records both statuses against the same digest.
- [ ] Document task object, original-input preservation, decision/audit ledger, bounded ARGUS mission package, and host-independent rendering.
- [ ] Run repository consistency validation.

### Task 4: Version, release note, and full verification

**Files:**
- Modify: `atlas-os.yaml`
- Modify: `atlas-ai.yaml` if authority references change
- Modify: `CHANGELOG.md`
- Create: `docs/releases/v2.1.0-rc.1.md`

**Interfaces:**
- Consumes: verified implementation and documentation
- Produces: candidate release metadata for the architecture rewrite

- [ ] Bump candidate version to `2.1.0-rc.1` because activation-contract v2 is a breaking machine-interface change.
- [ ] Preserve existing external release blockers rather than claiming stable release readiness.
- [ ] Run all unit, conformance, regression, integration, repository, machine-contract, output-contract, and deterministic-package checks.
- [ ] Publish only after all required checks pass and review findings are resolved.

## Unresolved externally observable decisions

None. The user explicitly requires portable ATLAS initialization and explicit permission before ARGUS handoff; the design above resolves the single-prompt versus double-prompt UX by allowing one explicit approval event to set both exact-preview routing approval and ARGUS authorization while keeping the machine states separate.
