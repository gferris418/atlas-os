# ATLAS Master Classification Catalogue — Design

## 1. Objective

1.1 Create a governed, machine-readable master classification catalogue beneath the existing ATLAS standards registry.

1.2 Preserve ATLAS as the classification authority while allowing ARGUS and other playbooks to assign real-world entities to canonical classifications.

1.3 Provide complete browseable catalogues for six dimensions:

1.3.1 Economic Activity

1.3.2 Sector / Subsector

1.3.3 Industry

1.3.4 Product / Service / Solution

1.3.5 Domain / Capability

1.3.6 Technology

1.4 Keep dynamic indicators separate from static taxonomy definitions.

## 2. Design principles

2.1 Multi-dimensional catalogue, not one forced hierarchy.

2.2 Stable ATLAS classification IDs remain independent of external standard codes.

2.3 Every entry records provenance, source standard/version, hierarchy, lifecycle and crosswalks.

2.4 Historical versions are preserved.

2.5 Restricted external datasets are not redistributed when licensing or source policy does not permit it.

2.6 Unknown or candidate mappings remain explicit and never become canonical equivalence by implication.

2.7 ARGUS may propose assignments and mappings but ATLAS governs promotion to canonical state.

## 3. Canonical dimensions

3.1 ECONOMIC_ACTIVITY

3.1.1 Primary global backbone: UN ISIC Rev. 5.

3.1.2 ISIC Rev. 5 is operational, adopted in 2024, and exposes Section, Division, Group and Class levels.

3.1.3 Crosswalk targets include NACE Rev. 2.1, NAICS 2022 and verified national classifications.

3.2 SECTOR

3.2.1 ATLAS-owned analytical sector and subsector vocabulary.

3.2.2 External mappings include World Bank, ADB and verified government-sector structures.

3.3 INDUSTRY

3.3.1 ATLAS-owned canonical producer/supplier ecosystem vocabulary.

3.3.2 Crosswalks reference ISIC, NACE and NAICS where semantically valid.

3.4 PRODUCT

3.4.1 Primary global backbone: UN CPC Version 3.0.

3.4.2 Additional mappings may reference CPV, UNSPSC, HS, NATO supply classifications and national product/procurement catalogues.

3.4.3 A solution is a governed composite of products/services, capabilities and technologies rather than a duplicate external taxonomy.

3.5 DOMAIN and CAPABILITY

3.5.1 ATLAS-owned functional controlled vocabularies.

3.5.2 Examples include maritime surveillance, C4ISR, port automation, renewable power, bridge engineering and their constituent capabilities.

3.6 TECHNOLOGY

3.6.1 Add TECHNOLOGY as a first-class ATLAS classification family.

3.6.2 ATLAS owns the canonical technology vocabulary and may cross-reference authoritative technical standards and vocabularies.

## 4. Universal classification-entry contract

4.1 atlas_classification_id — stable ATLAS identifier.

4.2 family_id — governed classification family.

4.3 preferred_label — canonical human-readable label.

4.4 short_label — optional concise label.

4.5 definition — canonical definition.

4.6 source_standard_id — external or ATLAS-owned source standard.

4.7 source_version_id — explicit source version.

4.8 source_code — source-native code where one exists.

4.9 source_label — source-native label.

4.10 level — hierarchy level.

4.11 parent_id — canonical parent within the same catalogue when applicable.

4.12 hierarchy_path — ordered ancestor path.

4.13 jurisdiction — Global, regional, national or ATLAS-owned scope.

4.14 authority_id — source authority.

4.15 source_url — authoritative provenance URL.

4.16 effective_from / effective_to — temporal applicability.

4.17 lifecycle — DISCOVERED, CANDIDATE, VERIFIED, ACTIVE, SUPERSEDED or ARCHIVED.

4.18 evidence_status — CONFIRMED, PROBABLE, POSSIBLE, DISPUTED, UNVERIFIED or STALE.

4.19 aliases — alternative terminology.

4.20 keywords — search and normalization terms.

4.21 redistribution_status — PERMITTED, RESTRICTED, UNKNOWN or NOT_APPLICABLE.

4.22 last_verified_at — latest governance verification timestamp.

## 5. Crosswalk contract

5.1 Every crosswalk is directional.

5.2 Relationship values: EXACT, CLOSE, BROADER, NARROWER, RELATED or CANDIDATE.

5.3 A CANDIDATE relationship can never be treated as confirmed equivalence.

5.4 Crosswalks record source and target classification IDs plus provenance and evidence status.

## 6. Catalogue storage model

6.1 `registries/classification/catalogues/` stores ATLAS-governed catalogue manifests.

6.2 One catalogue manifest per family or externally sourced standard keeps files bounded and independently versionable.

6.3 `registries/classification/crosswalks/` stores explicit crosswalk datasets when redistribution is permitted.

6.4 Restricted standards remain metadata-only unless the source permits redistribution.

6.5 Generated or imported catalogue data is validated against a common JSON schema before becoming canonical.

## 7. Indicator-definition layer

7.1 Indicators are separate from classification entries.

7.2 ATLAS governs indicator definitions, units, formulas, dimensions, periodicity and source expectations.

7.3 Dynamic values are operational observations and do not belong in the static ATLAS taxonomy repository.

7.4 Initial indicator groups:

7.4.1 Economic Activity — GVA, GDP contribution, growth, employment, enterprise count, investment.

7.4.2 Sector — government budget, development allocation, project pipeline, procurement spend, donor funding.

7.4.3 Industry — supplier count, concentration, capacity, domestic capability, import dependence.

7.4.4 Product / Service — procurement spend, tender frequency, import/export value, price trend, supplier availability.

7.4.5 Domain / Capability — demand intensity, capability gap, installed base, procurement pipeline, supplier coverage.

7.4.6 Technology — maturity, adoption, TRL, growth, obsolescence risk, vendor concentration, regulatory maturity.

## 8. Source and version policy

8.1 Official authoritative sources are preferred.

8.2 The standards registry remains the source of truth for standard metadata and version lifecycle.

8.3 The catalogue layer must not silently infer or overwrite source versions.

8.4 `classification_status` and `publication_status` are separate concepts where an operational classification is available before final publication.

8.5 As of 2026-10-23, official UNSD sources identify ISIC Rev. 5 and CPC Version 3.0 as operational while their final UN publications may still be forthcoming.

## 9. Runtime and anti-drift rules

9.1 Catalogue entries are immutable by stable ID within a released version except through governed correction.

9.2 New external versions create new source-version records and preserve historical mappings.

9.3 Missing source codes do not authorize invented codes.

9.4 Restricted standards cannot be copied into the repository solely for convenience.

9.5 Classification assignments remain separate operational facts and may reference one or more catalogue entries.

## 10. Initial implementation scope

10.1 Add TECHNOLOGY to the approved classification-family set.

10.2 Add schemas for catalogue entries, catalogue manifests and indicator definitions.

10.3 Add validation for stable IDs, hierarchy integrity, source-version ownership, lifecycle/evidence status and redistribution rules.

10.4 Add ATLAS-owned seed catalogues for SECTOR, DOMAIN, CAPABILITY and TECHNOLOGY.

10.5 Add machine-readable external catalogue descriptors for ISIC Rev. 5, CPC 3.0, NACE Rev. 2.1, NAICS 2022 and CPV 2008.

10.6 Where official source data is freely available and suitable for redistribution, ingest canonical structure into ATLAS catalogue files through a governed import path.

10.7 Where redistribution is restricted or uncertain, retain metadata-only descriptors and authoritative source links.

10.8 Add indicator-definition registry for the six dimensions.

10.9 Add conformance tests that prevent duplicate IDs, broken parent chains, wrong source-version ownership, ungoverned technology terms, and dynamic indicator values from entering static registry files.

## 11. Non-goals

11.1 ATLAS will not become a market-data warehouse.

11.2 ATLAS will not store changing indicator observations.

11.3 ARGUS will not become the taxonomy authority.

11.4 External classification licensing terms will not be bypassed.

11.5 Product, capability and technology dimensions will not be collapsed into a single tree.
