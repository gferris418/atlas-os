# Global Classification Standards Registry Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first-class, versioned ATLAS classification standards registry with explicit taxonomy families, authoritative provenance, historical editions, crosswalks, validation, persistence routing, and seed international/Bangladesh catalogue metadata.

**Architecture:** Keep the existing 11-spec core unchanged. Add classification reference data as a nested registry under `registries/classification/`, three public interchange schemas, deterministic repository validation, and a small human documentation page. GitHub holds versioned reference knowledge; Access Asia operational classifications remain in SharePoint SQLite. Provider discoveries are proposals only until ATLAS validates/adopts them.

**Tech Stack:** YAML, JSON Schema draft 2020-12, Python 3.12 standard library + PyYAML 6.0.3, unittest, GitHub Actions.

## Global Constraints

- Preserve exactly three preprocessing steps and ATLAS sole next-step authority.
- `DOMAIN != SECTOR != INDUSTRY != ECONOMIC_ACTIVITY != PRODUCT != CAPABILITY != PROCUREMENT_CATEGORY != TRADE_CLASSIFICATION != OCCUPATION != GEOGRAPHY != COMPLIANCE_REGULATORY`.
- Classification does not prove customs, legal, regulatory, procurement, licensing, sanctions, or eligibility conclusions.
- Standard editions are versioned; successors never overwrite historical identities.
- Crosswalk grades are directional and limited to EXACT, CLOSE, BROADER, NARROWER, RELATED, CANDIDATE.
- Evidence statuses reuse CONFIRMED, PROBABLE, POSSIBLE, DISPUTED, UNVERIFIED, STALE.
- Full datasets are stored in GitHub only when redistribution/licensing metadata permits and repository size is suitable.
- GitHub is a versioned reference-data store, not the universal transactional database.
- No secrets, personal contact data, restricted source payloads, or private-system IDs enter the registry.
- The existing ban on `docs/plans` remains; this active implementation plan is stored under `docs/specs/` and should be removed after the implementation is merged, leaving history in Git.

---

### Task 1: Establish classification contracts and registry identity

**Files:**
- Create: `tests/conformance/test_classification_registry.py`
- Create: `schemas/classification-standard.schema.json`
- Create: `schemas/classification-entry.schema.json`
- Create: `schemas/classification-crosswalk.schema.json`
- Create: `registries/classification/families.yaml`
- Create: `registries/classification/authorities.yaml`
- Modify: `atlas-ai.yaml`
- Modify: `atlas-os.yaml`
- Modify: `tools/validate.py`

**Interfaces:**
- Consumes: existing ATLAS evidence vocabulary from `spec/evidence.yaml`; repository machine-contract discovery in `atlas-ai.yaml`; registry list in `atlas-os.yaml`.
- Produces: permanent classification family IDs, authority IDs, and three machine-readable schemas referenced by later registry files.

- [ ] **Step 1: Add the focused failing test**

Add conformance assertions that the eleven approved families exist and are unique; classification schemas are listed in `atlas-ai.yaml`; the classification registry root is listed in `atlas-os.yaml`; authorities have unique IDs and non-empty official names/source URLs; and the repository validator recognizes the nested classification surface.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: non-zero exit because classification schemas/registries and machine-contract references do not exist.

- [ ] **Step 3: Implement the minimum behavior**

Create the three schemas with strict object shapes and enums matching the approved design. Create `families.yaml` and `authorities.yaml`. Extend `atlas-ai.yaml`/`atlas-os.yaml` without adding a new core spec. Update `tools/validate.py` so nested classification registries and the new schemas are part of the canonical authority surface while the top-level registry set remains deliberately small.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: Task 1 tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: `ATLAS validation PASSED`.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: add classification registry contracts`.

---

### Task 2: Add versioned standards catalogue, update sources, and crosswalk graph

**Files:**
- Modify: `tests/conformance/test_classification_registry.py`
- Create: `registries/classification/standards.yaml`
- Create: `registries/classification/update-sources.yaml`
- Create: `registries/classification/crosswalks.yaml`
- Modify: `tools/validate.py`

**Interfaces:**
- Consumes: family IDs and authority IDs from Task 1; evidence statuses from `spec/evidence.yaml`; schemas from Task 1.
- Produces: standard/version records, authoritative update-source records, and directional crosswalk records.

- [ ] **Step 1: Add the focused failing test**

Add assertions for unique permanent standard IDs and version IDs; valid authority/family references; allowed lifecycle/evidence values; ACTIVE records requiring authoritative provenance; successor records preserving the superseded version; allowed directional crosswalk grades; CANDIDATE not being equivalent to EXACT; and dataset-storage mode requiring explicit redistribution status.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: non-zero exit because catalogue/update-source/crosswalk files and validation rules are absent.

- [ ] **Step 3: Implement the minimum behavior**

Seed metadata for the approved major standards where authoritative metadata is verified: ISIC, CPC, HS, SITC, UNSPSC, NACE, CPA, CPV, NAICS, World Bank frameworks, ADB frameworks, and relevant Bangladesh classifications. Records whose edition/licensing details are not yet verified remain CANDIDATE/UNVERIFIED rather than being promoted. Add update-source records pointing to authoritative publishers. Start `crosswalks.yaml` with no fabricated equivalences; only evidence-backed mappings may be added. Extend deterministic validation for identities, references, lifecycle, provenance, historical preservation, crosswalk grades, and licensing/storage rules.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: all classification registry tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: `ATLAS validation PASSED`.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: seed versioned classification standards catalogue`.

---

### Task 3: Route reference state and operational classifications correctly

**Files:**
- Modify: `tests/conformance/test_classification_registry.py`
- Modify: `tests/conformance/test_access_asia_data_ownership.py`
- Modify: `spec/persistence.yaml`
- Modify: `integrations/access-asia.yaml`
- Modify: `integrations/argus.yaml`

**Interfaces:**
- Consumes: classification registry identities from Tasks 1-2 and existing ATLAS persistence/provider authority contracts.
- Produces: explicit persistence classes for ATLAS GitHub reference data versus Access Asia operational entity classifications; explicit ARGUS proposal-only classification boundary.

- [ ] **Step 1: Add the focused failing test**

Assert that classification standards/authorities/versions/crosswalks/update sources route to `ATLAS_GITHUB`; operational entity classifications route to `SHAREPOINT_SQLITE` in the Access Asia profile; large/restricted classification source documents route to SharePoint; and ARGUS cannot promote discovered standards/crosswalks or persist canonical classification state without ATLAS authorization.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_registry tests.conformance.test_access_asia_data_ownership -v`
Expected: non-zero exit because these routing and provider-boundary contracts are not yet expressed.

- [ ] **Step 3: Implement the minimum behavior**

Extend the provider-neutral persistence spec with reference-data semantics without hard-coding Access Asia storage. Add the concrete Access Asia persistence routes. Add explicit ARGUS `may`/`may_not` classification proposal/adoption boundaries while preserving activation and next-step authority.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_registry tests.conformance.test_access_asia_data_ownership -v`
Expected: all focused routing tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python -m unittest discover -s tests/conformance -v`
Expected: all conformance tests pass.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: route classification reference and operational state`.

---

### Task 4: Publish user/integrator documentation and run full verification

**Files:**
- Modify: `tests/conformance/test_clean_architecture.py`
- Create: `docs/classification-standards.md`
- Modify: `docs/README.md`
- Modify: `docs/SUMMARY.md`
- Modify: `docs/framework.md`
- Modify: `docs/implementation-guide.md`
- Modify: `README.md`
- Delete after implementation is otherwise green: `docs/specs/2026-10-23-global-classification-standards-registry-implementation.md`

**Interfaces:**
- Consumes: implemented registry and persistence contracts.
- Produces: GitBook-ready explanation and navigation for classification standards, crosswalk semantics, update lifecycle, eligibility warning, and contributor workflow.

- [ ] **Step 1: Add the focused failing test**

Update clean-architecture documentation expectations to require `classification-standards.md` and require `docs/SUMMARY.md` to link it.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_clean_architecture -v`
Expected: non-zero exit because the new documentation page/navigation are absent.

- [ ] **Step 3: Implement the minimum behavior**

Document classification family separation, versioning, crosswalk grades, candidate/adoption workflow, licensing rule, provider boundary, and classification-not-eligibility warning. Update root repository map and implementation guidance. Remove this completed implementation plan from the active tree before final merge; retain the approved design spec as current architectural documentation unless repository review determines it should also move to Git history.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_clean_architecture -v`
Expected: documentation conformance passes.

- [ ] **Step 5: Run full verification**

Run in order:
- `python -m compileall -q atlas_runtime`
- `python -m atlas_runtime --help`
- `python -m unittest discover -s tests/unit -v`
- `python -m unittest discover -s tests/conformance -v`
- `python -m unittest discover -s tests/integration -v`
- `python tools/validate.py .`

Expected: every command exits 0; repository validator prints `ATLAS validation PASSED`.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `docs: publish classification standards registry`.

## Externally observable decisions

Resolved by the approved design:
- GitHub is the canonical versioned reference-data store for classification standards and crosswalks.
- Access Asia operational classifications remain in SharePoint SQLite.
- Full datasets are stored only when licensing/redistribution permits; otherwise metadata/checksum/retrieval information is stored.
- Candidate discoveries never become canonical automatically.
- Historical editions are retained.

No unresolved product decision blocks implementation. Exact seed editions and redistribution modes are evidence-dependent facts: when authoritative verification is unavailable, the record remains CANDIDATE/UNVERIFIED rather than guessing.