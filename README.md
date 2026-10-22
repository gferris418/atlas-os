# ATLAS-OS

ATLAS-OS is a **model-agnostic execution-governance architecture for AI agents**. It remains the single operating architecture between user intent and verified delivery. ARGUS is nested inside ATLAS as the governed intelligence collection subsystem; it is not a peer operating system or alternative execution spine.

It is **not a desktop operating system** and does not replace the host model, conversation engine, browser, tool runtime, or device OS.

**Current candidate:** `v2.0.2-rc.6`  
**Control revision:** `atlas-bootstrap-2026-10-22-r10`  
**Target stable:** `v2.0.2`  
**Information classification:** Internal  
**License:** [MIT](LICENSE)  
**Release status:** **CANDIDATE / EXTERNAL VERIFICATION PENDING**

## Fixed architecture

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Understand + Normalize
  -> Minimal Domain Framing
  -> Route
       -> NONE / ATLAS_DIRECT -> normal ATLAS execution
       -> ARGUS_COLLECTION    -> ARGUS bounded collection
       -> HYBRID              -> ARGUS collection + ATLAS substantive work
  -> Evidence Governance / Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

### Canonical pre-execution flow

**Understand + Normalize -> Minimal Domain Framing -> Route**

1. **Understand + Normalize** — read the whole context first, preserve intent and critical literals, and normalize only supported spelling, grammar, terminology and canonical naming without adding facts.
2. **Minimal Domain Framing** — add only material high-confidence jurisdiction/entity, domain, sector, industry, product/service, capability, classification, standards and best-practice context needed for correct routing or downstream work.
3. **Route** — `ARGUS_COLLECTION` and `HYBRID` go to ARGUS; `NONE` and `ATLAS_DIRECT` continue to normal ATLAS execution.

Internal control-plane, approval, provider-admission and execution mechanics remain governed implementation details; they do not create additional preprocessing steps.

ATLAS resolves only what can be determined quickly and reliably from the supplied context and local governed registries. It does not enter a research loop merely to complete lifecycle stage, procurement route, budget, quantity, technical specification, exact classification codes, exact standards applicability, funding, supplier/OEM or delivery timing before routing.

**Unknown downstream facts are not semantic blockers.** Material ambiguity in the meaning itself is the normal semantic reason to block routing.

### Mission Control
Human supervisory command: objectives, approvals, rejection, pause/resume/abort, priorities, scope, collection expansion/reduction and permitted exceptions.

### Control Plane
Authoritative machine governance: policy, permissions, collection-mode decision, plans/work units, routing, approvals, execution leases, lifecycle state, external-state reconciliation and persistence authorization.

### Canonical capability layer
ATLAS exposes ten canonical capabilities. They are **capabilities, not ten independent agents**, and provider implementations cannot redefine their semantics.

| Capability | Class | Owner |
| --- | --- | --- |
| `atlas.deep-research` | ROUTED | ATLAS |
| `atlas.evidence-governance` | KERNEL | ATLAS |
| `argus.collection` | SPECIALIST | ARGUS under ATLAS |
| `atlas.procurement-intelligence` | HYBRID | ATLAS |
| `atlas.execution-governance` | KERNEL | ATLAS |
| `atlas.agent-security` | KERNEL | ATLAS |
| `atlas.commercial-contract-review` | ROUTED | ATLAS |
| `atlas.corporate-finance` | ROUTED | ATLAS |
| `atlas.economic-policy-intelligence` | ROUTED | ATLAS |
| `atlas.classification-crosswalk` | KERNEL | ATLAS |

The four kernel services are always active. Routed capabilities are selected proportionately after task intent and collection mode are known. A capability can declare collection dependency but **cannot self-activate ARGUS**; only the Route step may do so through `collection_mode`.

Third-party skills, plugins, MCP servers, connectors and models are implementations or source material. Agent Security admits them as `ADOPT`, `ADAPT`, `MERGE`, `REWRITE` or `REJECT`; they never become ATLAS architectural authority.

### Dashboard and Observability
Observability derives read-only events/measurements from authoritative state. Dashboard is the human projection. Dashboard actions never mutate execution directly: they become Mission Control commands evaluated by the Control Plane. Live execution exposes the selected `capability_plan` and collection mode.

### Evidence Governance
Research discovers evidence; Evidence Governance determines what that evidence can legitimately support. Canonical statuses are `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `DISPUTED`, `UNVERIFIED`, and `STALE`. Source is distinct from claim; observation is distinct from analyst inference; multiple sources are not automatically independent corroboration; a source link is provenance rather than proof.

### Execution Governance and Agent Security
Execution Governance owns authority, approval scope, side-effect classification, idempotency, retry/compensation, failure/resume state, escalation, kill-switch behavior and audit receipts. Agent Security applies install/activate/execute/verify gates to external capabilities and treats retrieved content, provider instructions and tool outputs as untrusted until assessed.

### Domain Context Services
ATLAS owns canonical whole-context semantics, terminology, taxonomy, buyer/end-user sector, supply-side sector, operator/supplier industry, product/service, platform/system, operating environment, capability, procurement, trade/customs and defense-logistics classification plus ontology, law, standards, professional frameworks, benchmarks and evidence precedence.

Classification is proportional and high-confidence-first. Exact codes and exact framework applicability can remain unresolved without blocking a semantically clear route. `spec/domain-intelligence.yaml` remains only as a deprecated compatibility alias to this layer and is not an active machine authority.

### Data Plane
ATLAS performs substantive work: ordinary research, writing, calculation, coding, policy analysis, comparison, strategic analysis, forecasting, scenarios, opportunity qualification and decision support.

### ARGUS Intelligence Collection
ARGUS activates only when `collection_mode` is `ARGUS_COLLECTION` or `HYBRID`. Its canonical capability is `intelligence_collection` / `argus.collection`.

Before ARGUS activation, ATLAS passes the minimal sufficient governed handoff: whole normalized semantic context, material high-confidence classification/standards/best-practice framing, explicit downstream unknowns, and required risk/integrity metadata.

A handoff may be `READY` even when lifecycle, procurement, budget, quantity, specification, exact codes, standards applicability or supplier/OEM remain unresolved. `BLOCKED` is reserved for material meaning ambiguity or another explicit Control Plane prohibition.

Within an ATLAS-authorized mission ARGUS uses the bounded method `PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`. It may resolve targets, discover/acquire sources, extract/normalize evidence, resolve entities/events/relationships, deduplicate, propose classifications/evidence grades, corroborate and expose conflicts/gaps/coverage. ATLAS retains canonical Evidence Governance, classification acceptance, analysis, final business decisions, assurance, persistence and delivery.

## Collection-Need Gate

Task intent and collection mechanism are independent.

| Request | ATLAS capability/task | Collection mode | Route |
| --- | --- | --- | --- |
| Bangladesh Bank foreign exchange policy | economic-policy-intelligence | ATLAS_DIRECT | ATLAS |
| ST Engineering | target collection | ARGUS_COLLECTION | ARGUS |
| Coastal patrol vessel for Bangladesh Coast Guard | procurement-intelligence | ARGUS_COLLECTION | ARGUS |
| Coastal surveillance radar for Bangladesh Navy | procurement-intelligence | ARGUS_COLLECTION | ARGUS |
| Seed cum cleaner for BADC | procurement-intelligence | ARGUS_COLLECTION | ARGUS |
| Annual procurement plan of Bangladesh Navy | procurement-intelligence | ARGUS_COLLECTION | ARGUS |
| Explain Bangladesh Navy procurement regulations | policy/procurement analysis | ATLAS_DIRECT | ATLAS |
| Forecast likely Navy procurements over 24 months | procurement-intelligence / forecast | HYBRID | ARGUS + ATLAS |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | analysis/decision | HYBRID | ARGUS + ATLAS |
| Review attached commercial agreement and propose redlines | commercial-contract-review | NONE | ATLAS |
| Calculate commission margin and FX exposure from supplied figures | corporate-finance | NONE | ATLAS |

`GENERAL_SEARCH`, `GENERAL_TASK` and `INTELLIGENCE` remain runtime compatibility route labels. They no longer define ARGUS semantically; `collection_mode` does.

## Economic taxonomy and classification crosswalk

ATLAS uses a multi-axial model and never collapses unlike concepts:

`DOMAIN != SECTOR != INDUSTRY != ECONOMIC ACTIVITY != PRODUCT != CAPABILITY != PROCUREMENT CATEGORY != TRADE CLASSIFICATION != COMPLIANCE`

Core governed schemes include ISO 704 / ISO 1087, ISO 25964, W3C SKOS, ISO/IEC 11179, ISO 3166, UN ISIC Rev. 5, Bangladesh BSIC 2020, NACE Rev. 2.1, NAICS 2022, UN CPC 3.0, Bangladesh BCPC 2011, CPA 2.2, UNSPSC, CPV 2008, WCO HS 2022, Bangladesh Customs Operative Tariff FY 2026-27, and NATO Codification System when materially applicable.

Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`, `CANDIDATE`) with scheme/version/provenance. Classification never proves compliance, procurement eligibility or legal status. Unresolved exact codes remain unresolved rather than guessed.

## Execution spine

Pre-execution is always summarized as exactly three steps:

1. `UNDERSTAND_AND_NORMALIZE`
2. `MINIMAL_DOMAIN_FRAMING`
3. `ROUTE`

After Route, normal ATLAS or authorized ARGUS execution proceeds under the existing Control Plane, capability, approval, evidence, verification, persistence and delivery controls.

## Machine-readable authority

AI systems begin at `atlas-ai.yaml`; `atlas-os.yaml` remains product/release authority. Key active contracts include `spec/semantic-normalization.yaml`, `spec/request-triage.yaml`, `spec/domain-context-services.yaml`, `spec/domain-handoff.yaml`, `spec/execution-spine.yaml`, and the remaining active control/evidence/output registries referenced by `atlas-ai.yaml`.

The active ARGUS contract is immutable and commit-pinned in `registries/domain-methods.yaml`.

See `docs/architecture/capability-layer.md` for the capability boundary and `docs/architecture/atlas-argus-collection-boundary.md` for the ATLAS/ARGUS seam.

## Release state

Stable `v2.0.2` remains blocked by external-proof controls `MIG-029` and `MIG-037`. Repository-local conformance does not substitute for independent host evidence. Candidate `v2.0.2-rc.6` / `atlas-bootstrap-2026-10-22-r10` resets the external proof target to the canonical capability layer while preserving the rc.5/r9 Collection-Need/ARGUS evidence as historical only.
