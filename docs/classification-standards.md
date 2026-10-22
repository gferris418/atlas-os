# Classification Standards Registry

ATLAS maintains a governed, versioned registry of external classification systems used to interpret, route, compare, match, and persist structured business and intelligence context. The registry is reference infrastructure; it is not a substitute for legal, customs, regulatory, sanctions, licensing, or procurement determinations.

## Classification families

The canonical families are deliberately distinct:

| Family | Meaning |
| --- | --- |
| `DOMAIN` | Broad knowledge or operating domain |
| `SECTOR` | High-level sector grouping used for analysis or policy |
| `INDUSTRY` | Industry grouping describing producers or establishments |
| `ECONOMIC_ACTIVITY` | Productive activities carried out by economic units |
| `PRODUCT` | Goods or services as outputs or transaction objects |
| `CAPABILITY` | Functional or solution capability used for matching |
| `PROCUREMENT_CATEGORY` | Procurement-oriented goods, works, services, or category grouping |
| `TRADE_CLASSIFICATION` | Customs or trade-statistics classification of traded goods |
| `OCCUPATION` | Jobs or occupations |
| `GEOGRAPHY` | Geographic or administrative areas |
| `COMPLIANCE_REGULATORY` | Regulatory or compliance classification context |

A code in one family must not be treated as interchangeable with a code in another family merely because the labels look similar.

## Registry structure

The machine authority is under `registries/classification/`:

- `families.yaml` — approved family vocabulary and meanings.
- `authorities.yaml` — issuing authorities and authoritative source locations.
- `standards.yaml` — stable standard IDs, versioned editions, provenance, lifecycle, evidence and storage/licensing metadata.
- `update-sources.yaml` — authoritative places ATLAS may check for revisions.
- `crosswalks.yaml` — directional mappings between identified editions and codes.

Public contracts are defined by:

- `schemas/classification-standard.schema.json`
- `schemas/classification-entry.schema.json`
- `schemas/classification-crosswalk.schema.json`

## Version and lifecycle model

Standards have stable IDs and editions have stable version IDs. New editions do not overwrite older editions. Historical versions remain available so ATLAS can interpret old tenders, contracts, trade records, policies, and evidence using the classification actually in force or cited at that time.

Lifecycle states are:

`DISCOVERED -> CANDIDATE -> VERIFIED -> ACTIVE -> SUPERSEDED -> ARCHIVED`

The lifecycle is not purely automatic. A newly observed standard or edition is a candidate until evidence and provenance are checked. An `ACTIVE` edition must be `CONFIRMED`.

## Evidence and provenance

Classification metadata uses the normal ATLAS evidence vocabulary: `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `DISPUTED`, `UNVERIFIED`, and `STALE`.

Each edition carries an authoritative source URL. ATLAS should prefer the issuing authority or another primary official source when establishing an edition, revision, effective date, or official code meaning. Secondary sources may help discovery but do not promote a candidate by themselves.

## Crosswalks

Crosswalks are directional. Allowed relationships are:

- `EXACT`
- `CLOSE`
- `BROADER`
- `NARROWER`
- `RELATED`
- `CANDIDATE`

A relationship in one direction does not imply the inverse relationship unless the inverse is separately recorded and valid. `CANDIDATE` means a proposed mapping that still requires ATLAS validation; it is never canonical equivalence.

## Licensing and dataset storage

The registry distinguishes metadata about a standard from the underlying classification dataset. Dataset storage modes are `NONE`, `METADATA_ONLY`, `PERMITTED_EXTRACT`, and `FULL_DATASET`. Redistribution status is recorded separately.

`FULL_DATASET` is allowed only where redistribution is explicitly `PERMITTED`. Otherwise ATLAS keeps metadata, provenance, and permitted extracts instead of copying restricted material into GitHub.

No credentials, private platform IDs, personal contact information, or restricted source payloads belong in the classification registry.

## Update workflow

1. Detect a possible new standard, edition, revision, or mapping from an authoritative update source or an authorized intelligence task.
2. Register it as `DISCOVERED` or `CANDIDATE` with provenance rather than silently replacing the current canonical record.
3. Verify issuing authority, official name/version, jurisdiction, effective/publication dates where available, evidence status, and licensing/storage constraints.
4. Link predecessor/successor editions without deleting history.
5. Validate any crosswalk direction and relationship strength independently.
6. Run ATLAS conformance and repository validation.
7. Promote only after ATLAS accepts the evidence and persistence change.

ARGUS may discover and propose standards or crosswalks while performing an ATLAS-authorized intelligence mission. It may not promote a candidate to canonical classification state or persist that canonical state without ATLAS authorization.

## Persistence model

ATLAS separates reference knowledge from operating data:

| Workload | Core class | Access Asia deployment target |
| --- | --- | --- |
| Standard, authority, edition, update-source and crosswalk reference metadata | `VERSIONED_REFERENCE_DATA` | ATLAS GitHub |
| Classification attached to a live organization, product, opportunity, tender or project | `OPERATIONAL_RELATIONAL_STATE` | SharePoint SQLite canonical graph |
| Classification source documents and large/restricted supporting files | `DOCUMENT_CONTENT` | SharePoint |
| Relationship and engagement state | `CRM_STATE` | HubSpot |

The product names above are Access Asia deployment choices, not core ATLAS architecture. The core persistence contract remains provider-neutral.

## Interpretation limits

A classification can organize evidence, support search, suggest supplier/product similarity, assist procurement research, or provide analytical context. It cannot by itself establish:

- customs duty or tariff treatment;
- legal or regulatory compliance;
- import/export authorization;
- sanctions or restricted-party status;
- procurement eligibility or qualification;
- licensing or certification; or
- technical compliance with a tender requirement.

Those conclusions require the applicable authoritative evidence and the relevant ATLAS verification workflow.
