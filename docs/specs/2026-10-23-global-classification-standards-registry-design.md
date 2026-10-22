# Global Classification Standards Registry — Design

## Status
Approved design, 2026-10-23.

## Objective
Make international and national classification standards first-class, versioned ATLAS reference knowledge so ATLAS and bounded providers such as ARGUS can classify commercial concepts reproducibly without treating unlike taxonomies as interchangeable.

## Core invariant
`DOMAIN != SECTOR != INDUSTRY != ECONOMIC_ACTIVITY != PRODUCT != CAPABILITY != PROCUREMENT_CATEGORY != TRADE_CLASSIFICATION != OCCUPATION != GEOGRAPHY != COMPLIANCE`

Classification and crosswalk results do not by themselves prove customs, legal, regulatory, procurement, licensing, sanctions, or eligibility conclusions.

## Architecture
Use a GitHub-backed versioned standards registry plus an explicit crosswalk graph. Standards remain independent and preserve their issuing authority, jurisdiction, edition, effective dates, hierarchy, provenance, and lifecycle. Crosswalks relate entries without collapsing them into one universal taxonomy.

GitHub is the canonical store for ATLAS reference standards, versions, authorities, update-source definitions, and crosswalks. Operational classifications attached to Access Asia commercial objects remain in the operational relational store selected by the deployment profile.

## Proposed repository structure

```text
registries/classification/
  standards.yaml
  authorities.yaml
  families.yaml
  crosswalks.yaml
  update-sources.yaml
  datasets/
    <standard-id>/<version>/...
schemas/
  classification-standard.schema.json
  classification-entry.schema.json
  classification-crosswalk.schema.json
```

Complete machine-readable classification datasets may be stored under `datasets/` when redistribution/licensing permits and repository-size limits remain appropriate. Otherwise ATLAS stores authoritative metadata, checksums, retrieval instructions, and normalized permitted extracts without falsely claiming a full local copy.

## Identity and versioning
Every standard receives a permanent ATLAS standard ID. Every edition/version is separately addressable and immutable after canonical adoption except for provenance-preserving corrections. New editions supersede rather than overwrite prior editions.

Each standard record includes at minimum:
- ATLAS standard ID
- official name and abbreviation
- classification family
- issuing authority
- jurisdiction/scope
- official identifier/version/revision
- publication/effective/superseded dates where available
- hierarchy availability
- authoritative source metadata
- licensing/redistribution status
- lifecycle status
- evidence status
- update history

Every classification entry preserves the source code, source label, hierarchy/parent relationship where published, standard/version identity, and provenance.

## Families
Initial families are:
- DOMAIN
- SECTOR
- INDUSTRY
- ECONOMIC_ACTIVITY
- PRODUCT
- CAPABILITY
- PROCUREMENT_CATEGORY
- TRADE_CLASSIFICATION
- OCCUPATION
- GEOGRAPHY
- COMPLIANCE_REGULATORY

Families may be extended through a reviewed registry change; existing meanings must not be silently redefined.

## Initial standards catalogue
Seed authoritative metadata for major systems including, where applicable and licensing permits: UN ISIC, UN CPC, HS/WCO, SITC, UNSPSC, EU NACE, CPA, CPV, NAICS, World Bank sector/procurement frameworks, ADB sector/procurement frameworks, and relevant Bangladesh economic, customs, industrial, procurement, product, and geographic classifications. Inclusion in the catalogue does not imply a crosswalk exists.

## Crosswalk graph
Crosswalk records are first-class, directional relationships between identified entries/standards. Allowed relationship grades:
- EXACT
- CLOSE
- BROADER
- NARROWER
- RELATED
- CANDIDATE

Each crosswalk records source and target identities, relationship grade, evidence/provenance, evidence status, temporal applicability when relevant, and review metadata. `CANDIDATE` is never treated as canonical equivalence.

## Lifecycle
Standard/version lifecycle:

`DISCOVERED -> CANDIDATE -> VERIFIED -> ACTIVE -> SUPERSEDED -> ARCHIVED`

A rejected candidate is retained in audit history but is not canonical. Discovery does not automatically modify canonical truth. Promotion to VERIFIED/ACTIVE requires authoritative evidence and validation.

Evidence uses the ATLAS evidence vocabulary: CONFIRMED, PROBABLE, POSSIBLE, DISPUTED, UNVERIFIED, STALE.

## Update model
ATLAS maintains an update-source registry pointing to authoritative publishers. A periodic or user-triggered check may discover new standards, editions, amendments, or authoritative replacements. Discovery produces candidate changes. ATLAS validates source identity, version metadata, licensing constraints, and temporal applicability before canonical adoption.

Historical versions remain available so a project, tender, product, or trade event can resolve against the classification edition applicable at the relevant date.

## Persistence routing
Recommended ATLAS routing:
- CLASSIFICATION_STANDARD -> ATLAS_GITHUB
- CLASSIFICATION_AUTHORITY -> ATLAS_GITHUB
- CLASSIFICATION_VERSION -> ATLAS_GITHUB
- CLASSIFICATION_CROSSWALK -> ATLAS_GITHUB
- CLASSIFICATION_UPDATE_SOURCE -> ATLAS_GITHUB
- CLASSIFICATION_DATASET -> ATLAS_GITHUB when permitted and suitable; otherwise authoritative external source with version/checksum metadata
- OPERATIONAL_ENTITY_CLASSIFICATION -> deployment relational store (Access Asia: SHAREPOINT_SQLITE)
- LARGE_OR_RESTRICTED_SOURCE_DOCUMENT -> deployment document store (Access Asia: SHAREPOINT)

GitHub is a versioned reference-data store, not the universal transactional database.

## Provider boundary
ATLAS retains orchestration, canonical-adoption, next-step, and persistence authority. Providers may discover or propose standards and mappings within their approved scope, but provider output returns to ATLAS. ARGUS cannot independently promote candidate classifications or crosswalks into canonical ATLAS state.

## Validation and failure behavior
Validation must reject or quarantine:
- duplicate ATLAS IDs
- unknown classification families
- crosswalks to unknown standard/version/entry identities
- invalid lifecycle/evidence/relationship values
- ACTIVE versions lacking authoritative provenance
- a superseding version that destroys or overwrites historical identity
- a full-dataset claim where licensing/redistribution metadata does not permit the stored representation

Unreachable authoritative sources do not invalidate previously verified historical records; update checks record the failed observation without silently marking canonical data current.

## Testing
Conformance tests must prove:
1. classification families remain distinct;
2. IDs are unique and references resolve;
3. lifecycle and evidence vocabularies are enforced;
4. historical editions are preserved when a successor is added;
5. crosswalk grades are explicit and directional;
6. CANDIDATE mappings cannot be consumed as exact canonical equivalence;
7. GitHub reference-data routing is separate from operational entity persistence;
8. provider discoveries require ATLAS validation before canonical adoption;
9. licensing metadata gates full-dataset storage claims.

## Documentation
Public ATLAS documentation will explain the registry, classification-vs-eligibility warning, crosswalk semantics, versioning model, and how host/provider implementations consume it.

## Scope boundary
This feature establishes the registry contracts, seed catalogue metadata, validation, persistence routing, tests, and documentation. It does not assert that every listed standard has a legally redistributable full dataset or that all standards can be accurately crosswalked automatically.