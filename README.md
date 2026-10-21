# ATLAS-OS

ATLAS-OS is a **model-agnostic execution-governance architecture for AI agents**. It remains the single operating architecture between user intent and verified delivery. ARGUS is nested inside ATLAS as the governed intelligence collection subsystem; it is not a peer operating system or alternative execution spine.

**Current candidate:** `v2.0.2-rc.4`  
**Control revision:** `atlas-bootstrap-2026-10-22-r8`  
**Target stable:** `v2.0.2`  
**Release status:** **CANDIDATE / EXTERNAL VERIFICATION PENDING**

## Fixed architecture

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Intent + Target Interpretation
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> ARGUS bounded collection -> evidence package
       -> HYBRID           -> ARGUS collection + ATLAS substantive work
  -> Domain Context Services
  -> Data Plane
  -> Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

### Mission Control
Human supervisory command: objectives, approvals, rejection, pause/resume/abort, priorities, scope, collection expansion/reduction and permitted exceptions.

### Control Plane
Authoritative machine governance: policy, permissions, collection-mode decision, plans/work units, routing, approvals, execution leases, lifecycle state, external-state reconciliation and persistence authorization.

### Dashboard and Observability
Observability derives read-only events/measurements from authoritative state. Dashboard is the human projection. Dashboard actions never mutate execution directly: they become Mission Control commands evaluated by the Control Plane.

### Domain Context Services
ATLAS owns canonical terminology, taxonomy, economic sector context, operator/supplier industry, product/service, procurement, trade/customs and defense-logistics classification plus ontology, law, standards, professional frameworks, benchmarks and evidence precedence. `spec/domain-intelligence.yaml` remains only as a compatibility alias to this layer.

### Data Plane
ATLAS performs substantive work: ordinary research, writing, calculation, coding, policy analysis, comparison, strategic analysis, forecasting, scenarios, opportunity qualification and decision support.

### ARGUS Intelligence Collection
ARGUS activates only when `collection_mode` is `ARGUS_COLLECTION` or `HYBRID`. Its canonical capability is `intelligence_collection`.

ARGUS resolves targets, plans bounded collection, discovers/acquires sources, extracts/normalizes evidence, resolves entities, deduplicates, corroborates, exposes conflicts/gaps/coverage and returns a collection package. ATLAS retains canonical classification, analysis, final business decisions, assurance, persistence and delivery.

## Collection-Need Gate

Task intent and collection mechanism are independent.

| Request | ATLAS task | Collection mode | ARGUS |
| --- | --- | --- | --- |
| Bangladesh Bank foreign exchange policy | research/analysis | ATLAS_DIRECT | No |
| ST Engineering | research | ARGUS_COLLECTION | Yes |
| Coastal patrol vessel for Bangladesh Coast Guard | research/opportunity context | ARGUS_COLLECTION | Yes |
| Seed cum cleaner for BADC | research/opportunity context | ARGUS_COLLECTION | Yes |
| Annual procurement plan of Bangladesh Navy | research | ARGUS_COLLECTION | Yes |
| Explain Bangladesh Navy procurement regulations | analysis | ATLAS_DIRECT | No |
| Forecast likely Navy procurements over 24 months | analysis/forecast | HYBRID | Yes, collection only |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | analysis/decision | HYBRID | Yes, collection only |

`GENERAL_SEARCH`, `GENERAL_TASK` and `INTELLIGENCE` remain runtime compatibility route labels. They no longer define ARGUS semantically; `collection_mode` does.

## Economic taxonomy and international classification

ATLAS uses a multi-axial model and never collapses unlike concepts:

`DOMAIN != SECTOR != INDUSTRY != PRODUCT != CAPABILITY != PROCUREMENT CATEGORY != HS CODE`

Core governed schemes include:
- ISO 704 / ISO 1087 terminology principles;
- ISO 25964 and W3C SKOS vocabulary interoperability;
- ISO/IEC 11179 metadata/provenance concepts;
- ISO 3166 jurisdiction codes;
- UN ISIC Rev. 5 for economic activity;
- NACE Rev. 2.1 for EU economic activity;
- NAICS 2022 for North American industry/activity;
- UN CPC 3.0 for goods/services;
- CPA 2.2 for EU products/services;
- UNSPSC and CPV 2008 for procurement contexts;
- WCO HS 2022 for customs/trade;
- NATO Codification System when defense logistics is materially applicable.

Crosswalks must be explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`) with scheme, edition, provenance and confidence. Classification never proves compliance, procurement eligibility or legal status.

## Execution spine

1. preserve raw input/context;
2. interpret intent and targets;
3. decide collection mode;
4. resolve material Domain Context Services;
5. plan capabilities/providers/approvals;
6. execute ATLAS work and any authorized ARGUS collection work unit;
7. assure/verify;
8. output and persist through authorized receipts;
9. project operational state through Observability/Dashboard.

## Machine-readable authority

AI systems begin at `atlas-ai.yaml`; `atlas-os.yaml` remains product/release authority. Key contracts:
- `spec/mission-control.yaml`
- `spec/control-plane.yaml`
- `spec/request-triage.yaml`
- `spec/collection-routing.yaml`
- `spec/domain-context-services.yaml`
- `spec/execution-spine.yaml`
- `spec/observability.yaml`
- `spec/dashboard.yaml`
- `registries/domain-methods.yaml`
- `registries/taxonomies.yaml`

The active ARGUS contract is immutable and commit-pinned in `registries/domain-methods.yaml`.

## Release state

Stable `v2.0.2` remains blocked by external-proof controls `MIG-029` and `MIG-037`. Repository-local conformance does not substitute for independent host evidence.
