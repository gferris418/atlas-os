# Capability Admission Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a governed ATLAS capability-admission standard and integrate the newly reviewed forecasting, routing, assurance, memory-integrity, evaluation, analytics, and ARGUS-specialist boundaries without making third-party skills hard runtime dependencies.

**Architecture:** ATLAS remains provider-agnostic and owns routing, approvals, verification, persistence, and delivery. The new specification governs how external capabilities are admitted, wrapped, benchmarked, quarantined, or retired; concrete third-party skills are treated as reference providers unless a surface adapter and runtime evidence promote them to an active provider.

**Tech Stack:** YAML normative specs/registries, Markdown governance documentation, existing repository validator and unittest suites.

## Global Constraints

- Preserve ATLAS as the sole execution-governance spine.
- Do not make a third-party plugin or skill an unconditional core dependency based only on session availability.
- Keep ARGUS a specialist domain method; it does not own ATLAS planning, approvals, verification, or delivery.
- Separate static admission evidence from measured benchmark evidence.
- Treat a clean security scan as risk evidence, not a safety certification.
- Preserve missing proof as missing proof.

---

### Task 1: Add the capability-admission contract

**Files:**
- Create: `spec/capability-admission.yaml`
- Create: `docs/capability-admission.md`
- Modify: `spec/core.yaml`

**Interfaces:**
- Consumes: ATLAS capability routing, evidence, approval, persistence, and domain-method boundaries.
- Produces: admission states, evaluation gates, provider-wrapper rules, and evidence requirements.

- [ ] Define admission states and gates.
- [ ] Define provider-independence and runtime-availability rules.
- [ ] Define security, benchmark, provenance, overlap, cost, and fallback evidence.
- [ ] Reference the contract from the core specification.
- [ ] Validate with `python tools/validate/validate_repository.py .`.

### Task 2: Register the new generic ATLAS capabilities

**Files:**
- Modify: `registries/capabilities.yaml`

**Interfaces:**
- Consumes: `spec/capability-admission.yaml`.
- Produces: governed capability identifiers for admission governance, forecast governance, untrusted-content assurance, memory integrity, and learning/calibration.

- [ ] Add registry entries using only fields allowed by `schemas/registry.schema.json`.
- [ ] Preserve existing capability priorities and dependency direction.
- [ ] Validate registry schema and repository invariants.

### Task 3: Document the revised architecture and release lineage

**Files:**
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `atlas-os.yaml`

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: `v2.0.0-rc.12` candidate documentation and manifest lineage.

- [ ] Document control, assurance, knowledge-integrity, foresight, learning, and specialist-domain boundaries.
- [ ] Record Horizon Forge, Adaptive Task Routing, Injection Checker, Memory Keeper, Canonical Memory Verifier, Plugin Eval, Agent SkillGuard, Data Analytics, and Capture Team as evaluated reference providers/pattern sources, not mandatory runtime dependencies.
- [ ] Record Agentic Atlas as conditional because its Atlas MCP surface is not universally available.
- [ ] Increment candidate version to `2.0.0-rc.12` without changing stable target `2.0.0` or existing release blockers.
- [ ] Run unit, conformance, regression, integration, and repository validation commands.

### Task 4: Align ARGUS capability boundaries

**Files:**
- ARGUS repository: `docs/architecture/capability-integration.md`
- ARGUS repository: `README.md`
- ARGUS repository: `argus-intelligence.yaml`
- ARGUS repository: `CHANGELOG.md` if present

**Interfaces:**
- Consumes: ATLAS capability-admission contract and existing ARGUS activation contract.
- Produces: explicit Capture Team adaptation boundary, Proposal Team downstream boundary, provider-neutral source-adapter model, and no duplicate execution spine.

- [ ] Keep ARGUS core operating loop unchanged.
- [ ] Define Capture Team as an optional methodology adapter for discover/qualify/prioritize/brief logic.
- [ ] Define Proposal Team as post-pursuit downstream execution after human decision/PX promotion.
- [ ] Define procurement, company, trade, legal, and financial providers as replaceable adapters.
- [ ] Preserve current ATLAS compatibility claim until cross-repository validation proves a newer pin.

## Unresolved product decisions

None. The user authorized repository alignment, and existing repository governance determines candidate-versioning, provider independence, approval boundaries, and validation expectations.
