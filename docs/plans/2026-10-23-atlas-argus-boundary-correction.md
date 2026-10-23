# ATLAS–ARGUS Boundary Correction Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the canonical boundary: ATLAS-OS is the generic governance/orchestration framework; ARGUS is the ATLAS-governed 360° Business Intelligence playbook; Access Asia operational execution remains outside ATLAS core.

**Architecture:** Remove Access Asia bid/project/finance state machines from `atlas_runtime` because ATLAS already owns generic approvals, routing, evidence governance, verification, and action authorization. Strengthen ARGUS's manifest and Access Asia profiles so ARGUS owns intelligence methods and evidence-backed commercial facts across the lifecycle without becoming the authoritative bid-submission, project-management, accounting, invoice, or payment execution engine.

**Tech Stack:** Python `unittest`, YAML/Markdown contracts, GitHub Actions validation.

## Global Constraints

- ATLAS-OS remains framework-level and provider/tool neutral.
- ARGUS remains subordinate to ATLAS governance and is the 360° Business Intelligence playbook, not a peer operating system.
- Search engines, MCP servers, plugins, databases, connected apps, and other execution surfaces are capability providers/tools.
- ARGUS may maintain provenance-backed intelligence/commercial facts and derived views; it must not claim transactional execution authority for bid submission, project acceptance, invoicing, payments, or accounting.
- Preserve the Access Asia PX lineage across opportunity, bid, award, contract, and project.
- Preserve the pre-award `REV/OPP Opportunities` record after award; create a linked `OPS/PRJ Projects` workspace using the same PX identity rather than moving/deleting pre-award evidence.
- Do not invent a finance/accounting system of record that has not been designated.

---

### Task 1: Remove Access Asia domain execution from ATLAS core

**Files:**
- Create: `tests/conformance/test_framework_domain_boundary.py`
- Delete: `atlas_runtime/bid_workflow.py`
- Delete: `atlas_runtime/project_handover.py`
- Delete: `atlas_runtime/project_execution.py`
- Delete: `atlas_runtime/commercial_payment.py`
- Delete: their four unit-test files
- Modify: `README.md`
- Modify: `docs/argus-interface.md`
- Modify: `integrations/access-asia.yaml`

**Interfaces:**
- Consumes: existing ATLAS approval, routing, verification, persistence and external-action controls.
- Produces: framework-level boundary invariant with no Access Asia business state machines in `atlas_runtime`.

- [ ] Add a failing conformance test asserting the four domain modules are absent from ATLAS core and the Access Asia integration is explicitly a deployment profile.
- [ ] Verify the test fails while the merged PR #68–#71 modules exist.
- [ ] Remove the domain modules and their dedicated unit tests; do not replace them with duplicate generic state machines.
- [ ] Clarify that the `argus` registry handle is an ATLAS compatibility/execution handle for the ARGUS playbook, while underlying tools/providers are selected under ATLAS policy.
- [ ] Run conformance, unit, integration and repository validation workflows.

### Task 2: Define ARGUS as 360° BI without operational-execution authority

**Files:**
- Create: `spec/business-intelligence-boundary.yaml`
- Create: `tests/test_business_intelligence_boundary.py`
- Modify: `README.md`
- Modify: `argus-intelligence.yaml`
- Modify: `profiles/access-asia-system-registry.yaml`
- Modify: `profiles/access-asia-commercial-data-standard-v1.0.yaml`

**Interfaces:**
- Consumes: ATLAS governance contract and existing ARGUS collection/opportunity/supplier/learning methods.
- Produces: a machine-readable boundary defining ARGUS BI scope, operational exclusions, fact-store semantics and lifecycle workspace rules.

- [ ] Add focused tests for the 360° BI boundary, operational exclusions, fact-vs-ledger semantics, and SharePoint lifecycle preservation.
- [ ] Add the boundary specification and expose it from the ARGUS manifest.
- [ ] Reword ARGUS product/scope language from a narrow provider description to an ATLAS-governed 360° Business Intelligence playbook with government-commercial opportunity intelligence as a primary domain.
- [ ] Clarify that project, contract, invoice, payment and cost records in the ARGUS canonical graph are provenance-backed BI/commercial facts, not transactional execution authority.
- [ ] Correct lifecycle routing so `REV/OPP Opportunities` remains the pre-award record and award/contract activation creates a linked `OPS/PRJ Projects` workspace with the same PX lineage.
- [ ] Run ARGUS contract tests and repository validation.

### Task 3: Cross-repository consistency verification

**Files:**
- Modify only if validation exposes a concrete mismatch.

**Interfaces:**
- Consumes: corrected ATLAS and ARGUS branches.
- Produces: aligned terminology and authority boundaries across both repositories.

- [ ] Confirm ATLAS contains no bid/project/finance domain execution modules.
- [ ] Confirm ARGUS declares 360° BI scope but excludes transactional execution authority.
- [ ] Confirm ATLAS still owns approvals, routing, provider selection, evidence acceptance and persistence authorization.
- [ ] Confirm ARGUS still declares capability requirements while ATLAS selects and authorizes the actual providers/tools.
- [ ] Confirm no existing canonical schema or PX lineage is broken.

## Unresolved externally observable decisions

- The authoritative accounting/finance transaction system is intentionally left deployment-specific until Access Asia designates one; ARGUS stores BI facts and evidence references only.
