# ATLAS Master Classification Catalogue Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a governed six-dimension ATLAS master classification catalogue with stable IDs, authoritative-source descriptors, crosswalks, indicator definitions, validation, and complete ATLAS-owned reference lists while preserving external redistribution constraints.

**Architecture:** Extend the existing classification registry rather than adding a second taxonomy subsystem. ATLAS-owned Sector, Domain, Capability, and Technology catalogues are version-controlled reference data; external standards such as ISIC Rev.5 and CPC 3.0 are represented by authoritative descriptors and source-integrity metadata, with full external data stored only when redistribution is explicitly permitted. ARGUS remains a consumer/proposer, never the classification authority.

**Tech Stack:** YAML/JSON registries and schemas, Python 3.12 repository validator, `unittest` conformance tests, GitHub Actions validation.

## Global Constraints

- ATLAS remains the classification authority.
- ARGUS may propose classifications/crosswalks but may not promote them to canonical state.
- Use six primary catalogue dimensions: ECONOMIC_ACTIVITY, SECTOR, INDUSTRY, PRODUCT, DOMAIN/CAPABILITY, TECHNOLOGY.
- Keep PRODUCT, CAPABILITY and TECHNOLOGY semantically separate.
- Add TECHNOLOGY as a first-class family.
- Preserve historical standard versions and stable ATLAS IDs.
- Crosswalks remain directional and explicitly graded as EXACT, CLOSE, BROADER, NARROWER, RELATED or CANDIDATE.
- Dynamic indicator observations do not belong in GitHub reference-data registries.
- Restricted or unclear external datasets remain metadata/remote-source references unless redistribution is explicitly permitted.
- ISIC Rev.5 and CPC 3.0 official-source status must distinguish classification operational status from publication status.
- No runtime invention of canonical classification items.

---

### Task 1: Extend classification contracts for master catalogues

**Files:**
- Modify: `registries/classification/families.yaml`
- Modify: `registries/classification/standards.yaml`
- Modify: `schemas/classification-entry.schema.json`
- Create: `schemas/classification-catalogue.schema.json`
- Create: `schemas/classification-indicator.schema.json`
- Modify: `atlas-ai.yaml`
- Modify: `tools/validate.py`
- Test: `tests/conformance/test_classification_registry.py`

**Interfaces:**
- Consumes: existing family, standard/version, authority and lifecycle vocabularies.
- Produces: `TECHNOLOGY` family; catalogue-manifest schema; indicator-definition schema; source-version fields for operational/publication state.

- [ ] **Step 1: Add the focused failing tests**

Add assertions that:
1. `TECHNOLOGY` is in the exact approved family set.
2. `classification-catalogue.schema.json` and `classification-indicator.schema.json` are declared machine contracts.
3. classification entries require stable `atlas_classification_id`, `family_id`, provenance, lifecycle and source-standard/version linkage.
4. standards may separately declare `classification_status` and `publication_status`.
5. CPC 3.0 and ISIC Rev.5 remain operational while publication status may be `FORTHCOMING`.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: failures for missing TECHNOLOGY family, missing schemas/machine contracts and missing status separation.

- [ ] **Step 3: Implement the minimum behavior**

Update schemas and validator constants without changing unrelated families. Extend standard-version metadata with optional `classification_status` and `publication_status`; set verified current UN versions accordingly.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_registry -v`
Expected: all classification-registry conformance tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: `ATLAS repository contracts valid`.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: extend classification catalogue contracts`

---

### Task 2: Add catalogue descriptors and hierarchy validation

**Files:**
- Create: `registries/classification/catalogues/economic-activity.yaml`
- Create: `registries/classification/catalogues/industry.yaml`
- Create: `registries/classification/catalogues/product.yaml`
- Create: `registries/classification/catalogues/sector.yaml`
- Create: `registries/classification/catalogues/domain.yaml`
- Create: `registries/classification/catalogues/capability.yaml`
- Create: `registries/classification/catalogues/technology.yaml`
- Modify: `tools/validate.py`
- Test: `tests/conformance/test_classification_catalogues.py`

**Interfaces:**
- Consumes: Task 1 catalogue schema, standards registry, authorities and families.
- Produces: one discoverable catalogue descriptor for each governed dimension and deterministic hierarchy validation.

- [ ] **Step 1: Add the focused failing tests**

Assert that every catalogue descriptor has:
1. unique `catalogue_id`;
2. governed `family_id`;
3. explicit owner/authority;
4. version and lifecycle;
5. source mode (`ATLAS_OWNED`, `REMOTE_AUTHORITATIVE`, or `METADATA_ONLY`);
6. source standard/version when externally sourced;
7. hierarchy-level declarations;
8. redistribution mode consistent with storage mode.

Also test rejection of duplicate item IDs, unknown parents, parent cycles and family mismatches for embedded ATLAS-owned items.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_catalogues -v`
Expected: missing-module/files failure.

- [ ] **Step 3: Implement the minimum behavior**

Create descriptors:
- ECONOMIC_ACTIVITY → ISIC Rev.5 authoritative remote structure.
- INDUSTRY → ATLAS canonical industry catalogue crosswalkable to ISIC/NACE/NAICS.
- PRODUCT → CPC 3.0 authoritative remote structure plus procurement/trade crosswalk targets.
- SECTOR, DOMAIN, CAPABILITY, TECHNOLOGY → ATLAS-owned embedded catalogues.

The validator must fail closed on broken hierarchy and external source-version mismatch.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_catalogues -v`
Expected: all catalogue conformance tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: repository contract passes with nested catalogue directories admitted explicitly.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: add governed classification catalogues`

---

### Task 3: Populate ATLAS-owned Sector, Domain, Capability and Technology lists

**Files:**
- Modify: `registries/classification/catalogues/sector.yaml`
- Modify: `registries/classification/catalogues/domain.yaml`
- Modify: `registries/classification/catalogues/capability.yaml`
- Modify: `registries/classification/catalogues/technology.yaml`
- Test: `tests/conformance/test_classification_catalogues.py`

**Interfaces:**
- Consumes: common catalogue-entry contract.
- Produces: complete initial ATLAS-owned browseable controlled vocabularies with stable IDs and hierarchy paths.

- [ ] **Step 1: Add the focused failing tests**

Require the seed catalogues to include, at minimum, governed roots and representative descendants for:
- sectors: Defence & Security, Maritime, Transport, Energy, Infrastructure, ICT/Telecommunications, Healthcare, Water/Environment, Agriculture, Education, Financial Services, Public Administration;
- domains: Maritime, C4ISR, Ports, Energy, Civil Infrastructure, ICT/Digital, Security, Healthcare;
- capabilities: maritime surveillance, vessel detection/identification/tracking, command-and-control, communications, port automation, vessel-traffic management, renewable power, grid stability, energy storage, bridge engineering and structural monitoring;
- technologies: AI/ML/computer vision, radar, EO/IR, LiDAR, sonar, GNSS/PNT/INS, RF/satellite/5G/data links, diesel/gas-turbine/electric/hybrid propulsion, simulation/digital twin, cybersecurity, IoT, robotics, cloud/edge, batteries/energy storage, hydrogen, DLT and quantum.

Tests must require stable IDs, unique sibling serial/order values, definitions and valid parent chains.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_catalogues -v`
Expected: assertions fail for missing required roots/descendants.

- [ ] **Step 3: Implement the minimum behavior**

Populate the four catalogues. Use ATLAS-owned identifiers rather than pretending these terms are official ISIC/CPC entries. Record aliases only where unambiguous.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_catalogues -v`
Expected: all catalogue tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: repository contract passes.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `data: populate ATLAS classification catalogues`

---

### Task 4: Add authoritative external catalogue source integrity

**Files:**
- Create: `registries/classification/catalogues/sources/isic-rev5.yaml`
- Create: `registries/classification/catalogues/sources/cpc-3.0.yaml`
- Create: `registries/classification/catalogues/sources/nace-rev2.1.yaml`
- Create: `registries/classification/catalogues/sources/naics-2022.yaml`
- Create: `registries/classification/catalogues/sources/cpv-2008.yaml`
- Modify: `registries/classification/update-sources.yaml`
- Test: `tests/conformance/test_classification_sources.py`

**Interfaces:**
- Consumes: official source URLs/version metadata and catalogue descriptors.
- Produces: pinned source descriptors with expected counts/digests where independently verified, retrieval/update policy and redistribution decision.

- [ ] **Step 1: Add the focused failing tests**

Require source descriptors to record:
1. official authoritative URL;
2. standard/version IDs;
3. expected hierarchy/count metadata when official source publishes it;
4. source digest when independently verified;
5. retrieval mode;
6. redistribution status and allowed storage mode;
7. last verification date.

For ISIC Rev.5 require official hierarchy counts: 22 sections, 87 divisions, 258 groups, 463 classes, 830 total nodes. For CPC 3.0 record its verified source digest and 4,586-code structure only when the descriptor cites the official structure file and marks the source as independently verified; do not copy the entire dataset into GitHub unless redistribution is explicitly PERMITTED by ATLAS governance.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_sources -v`
Expected: missing-source-descriptor failure.

- [ ] **Step 3: Implement the minimum behavior**

Create descriptors using official URLs and independently verified structural metadata. Keep restricted/unclear datasets remote-authoritative or metadata-only. Do not treat a third-party mirror's license assertion as ATLAS redistribution authority.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_sources -v`
Expected: all source-integrity tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python tools/validate.py .`
Expected: repository contract passes.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `data: register authoritative classification sources`

---

### Task 5: Add indicator-definition registry and documentation

**Files:**
- Create: `registries/classification/indicators.yaml`
- Modify: `docs/classification-standards.md`
- Modify: `docs/SUMMARY.md` only if a new top-level document is introduced; otherwise keep the existing documentation surface.
- Modify: `atlas-ai.yaml`
- Modify: `tools/validate.py`
- Test: `tests/conformance/test_classification_indicators.py`

**Interfaces:**
- Consumes: classification family IDs and indicator schema.
- Produces: governed indicator definitions without dynamic observations.

- [ ] **Step 1: Add the focused failing tests**

Require each indicator to have unique ID, family applicability, definition, value type, unit/measure semantics, direction where meaningful, periodicity class, source expectation and explicit `stores_observations: false`.

Reject records containing current values, observation dates, entity-specific values or time-series arrays.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.conformance.test_classification_indicators -v`
Expected: missing indicator registry/schema failures.

- [ ] **Step 3: Implement the minimum behavior**

Add definitions for the agreed indicator groups: GVA/GDP contribution/growth/employment/enterprise count/investment; public budget/development allocation/project pipeline/procurement spend/donor funding; supplier count/concentration/capacity/domestic capability/import dependence; tender frequency/import/export/price trend/supplier availability; demand intensity/capability gap/installed base/supplier coverage; technology maturity/adoption/TRL/growth/obsolescence/vendor concentration/regulatory maturity.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.conformance.test_classification_indicators -v`
Expected: all indicator tests pass.

- [ ] **Step 5: Run the full verification**

Run:
- `python -m ruff check atlas_runtime tests tools`
- `python -m mypy atlas_runtime`
- `python -m unittest discover -s tests/unit -v`
- `python -m unittest discover -s tests/conformance -v`
- `python -m unittest discover -s tests/integration -v`
- `python tools/validate.py .`

Expected: zero failures and `ATLAS repository contracts valid`.

- [ ] **Step 6: Commit the passing deliverable**

Commit message: `feat: add classification indicator definitions`

---

## Unresolved externally observable decisions

1. Full copies of external standards must not enter GitHub until ATLAS records explicit redistribution permission. Until then, the general catalogue exposes their full authoritative source through remote descriptors rather than republishing it.
2. Bangladesh-specific BBS/BPPA code lists remain candidate sources until their exact current editions and redistribution terms are authoritatively verified.
3. Sector/Domain/Capability/Technology vocabularies are ATLAS-owned controlled vocabularies and therefore require version increments for structural changes after release.
