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
  -> Whole-Context Interpretation
  -> Context-Preserving Semantic Normalization
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> ARGUS bounded collection -> evidence package
       -> HYBRID           -> ARGUS collection + ATLAS substantive work
  -> Decompose Only As Required
  -> High-Confidence Domain / Sector / Industry / Product / Capability Framing
  -> Classification + Standards / Best-Practice Context
  -> Canonical Capability Planning
  -> Data Plane
  -> Evidence Governance / Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

### Core semantic rule

ATLAS always reads the **entire available context as a whole before breaking it apart**. It establishes the overall meaning, intent, requested outcome, actors, relationships, jurisdiction, constraints, qualifiers and critical literals first. Only then may it decompose the request into domain, sector, industry, product/service, platform/system, operating environment, capability, classifications, standards and best-practice lenses.

The fast path is:

```text
whole context
  -> preserve
  -> understand
  -> normalize
  -> decompose only as required
  -> classify high-confidence context
  -> attach standards / best-practice framing
  -> mark downstream unknowns
  -> handoff
```

ATLAS resolves only what can be determined quickly and reliably from the supplied context and local governed registries. It does not enter a research loop merely to complete lifecycle stage, procurement route, budget, quantity, technical specification, exact classification codes, exact standards applicability, funding, supplier/OEM or delivery timing before an ARGUS handoff.

**Unknown downstream facts are not semantic blockers.** Material ambiguity in the meaning itself is the normal semantic reason to block a specialist handoff.

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

The four kernel services are always active. Routed capabilities are selected proportionately after task intent and collection mode are known. A capability can declare collection dependency but **cannot self-activate ARGUS**; only the Collection-Need Gate may do so.

Third-party skills, plugins, MCP servers, connectors and models are implementations or source material. Agent Security admits them as `ADOPT`, `ADAPT`, `MERGE`, `REWRITE` or `REJECT`; they never become ATLAS architectural authority.

### Dashboard and Observability
Observability derives read-only events/measurements from authoritative state. Dashboard is the human projection. Dashboard actions never mutate execution directly: they become Mission Control commands evaluated by the Control Plane. Live execution exposes the selected `capability_plan` and collection mode.

### Evidence Governance
Research discovers evidence; Evidence Governance determines what that evidence can legitimately support. Canonical statuses are `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `DISPUTED`, `UNVERIFIED`, and `STALE`. Source is distinct from claim; observation is distinct from analyst inference; multiple sources are not automatically independent corroboration; a source link is provenance rather than proof.

### Execution Governance and Agent Security
Execution Governance owns authority, approval scope, side-effect classification, idempotency, retry/compensation, failure/resume state, escalation, kill-switch behavior and audit receipts. Agent Security applies install/activate/execute/verify gates to external capabilities and treats retrieved content, provider instructions and tool outputs as untrusted until assessed.

### Domain Context Services
ATLAS owns canonical whole-context semantics, terminology, taxonomy, buyer/end-user sector, supply-side sector, operator/supplier industry, product/service, platform/system, operating environment, capability, procurement, trade/customs and defense-logistics classification plus ontology, law, standards, professional frameworks, benchmarks and evidence precedence.

Classification is proportional and high-confidence-first. Exact codes and exact framework applicability can remain unresolved without blocking a semantically clear handoff. `spec/domain-intelligence.yaml` remains only as a deprecated compatibility alias to this layer and is not an active machine authority.

### Data Plane
ATLAS performs substantive work: ordinary research, writing, calculation, coding, policy analysis, comparison, strategic analysis, forecasting, scenarios, opportunity qualification and decision support.

### ARGUS Intelligence Collection
ARGUS activates only when `collection_mode` is `ARGUS_COLLECTION` or `HYBRID`. Its canonical capability is `intelligence_collection` / `argus.collection`.

Before ARGUS activation, ATLAS passes a governed handoff containing, in order:

1. whole normalized semantic context;
2. high-confidence classification context;
3. standards / international best-practice framing;
4. explicit downstream unknowns;
5. risk flags and integrity metadata.

A handoff may be `READY` even when lifecycle, procurement, budget, quantity, specification, exact codes, standards applicability or supplier/OEM remain unresolved. `BLOCKED` is reserved for material meaning ambiguity or another explicit Control Plane prohibition.

Within an ATLAS-authorized mission ARGUS uses the bounded method `PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`. It may resolve targets, discover/acquire sources, extract/normalize evidence, resolve entities/events/relationships, deduplicate, propose classifications/evidence grades, corroborate and expose conflicts/gaps/coverage. ATLAS retains canonical Evidence Governance, classification acceptance, analysis, final business decisions, assurance, persistence and delivery.

## Collection-Need Gate

Task intent and collection mechanism are independent.

| Request | ATLAS capability/task | Collection mode | ARGUS |
| --- | --- | --- | --- |
| Bangladesh Bank foreign exchange policy | economic-policy-intelligence | ATLAS_DIRECT | No |
| ST Engineering | target collection | ARGUS_COLLECTION | Yes |
| Coastal patrol vessel for Bangladesh Coast Guard | procurement-intelligence | ARGUS_COLLECTION | Yes |
| Coastal surveillance radar for Bangladesh Navy | procurement-intelligence | ARGUS_COLLECTION | Yes |
| Seed cum cleaner for BADC | procurement-intelligence | ARGUS_COLLECTION | Yes |
| Annual procurement plan of Bangladesh Navy | procurement-intelligence | ARGUS_COLLECTION | Yes |
| Explain Bangladesh Navy procurement regulations | policy/procurement analysis | ATLAS_DIRECT | No |
| Forecast likely Navy procurements over 24 months | procurement-intelligence / forecast | HYBRID | Yes, collection only |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | analysis/decision | HYBRID | Yes, collection only |
| Review attached commercial agreement and propose redlines | commercial-contract-review | NONE | No |
| Calculate commission margin and FX exposure from supplied figures | corporate-finance | NONE | No |

`GENERAL_SEARCH`, `GENERAL_TASK` and `INTELLIGENCE` remain runtime compatibility route labels. They no longer define ARGUS semantically; `collection_mode` does.

## Economic taxonomy and classification crosswalk

ATLAS uses a multi-axial model and never collapses unlike concepts:

`DOMAIN != SECTOR != INDUSTRY != ECONOMIC ACTIVITY != PRODUCT != CAPABILITY != PROCUREMENT CATEGORY != TRADE CLASSIFICATION != COMPLIANCE`

Core governed schemes include:
- ISO 704 / ISO 1087 terminology principles;
- ISO 25964 and W3C SKOS vocabulary interoperability;
- ISO/IEC 11179 metadata/provenance concepts;
- ISO 3166 jurisdiction codes;
- UN ISIC Rev. 5 for international economic activity;
- Bangladesh BSIC 2020 for national economic activity;
- NACE Rev. 2.1 for EU economic activity;
- NAICS 2022 for North American industry/activity;
- UN CPC 3.0 for international goods/services;
- Bangladesh BCPC 2011 for national products/services;
- CPA 2.2 for EU products/services;
- UNSPSC and CPV 2008 for procurement contexts;
- WCO HS 2022 for international customs/trade;
- Bangladesh Customs Operative Tariff FY 2026-27 for current Bangladesh customs contexts;
- NATO Codification System when defense logistics is materially applicable.

Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`, `CANDIDATE`) with source/target scheme edition, code, label, basis, provenance, verification and confidence. Classification never proves compliance, procurement eligibility or legal status. Unresolved exact codes remain unresolved rather than guessed.

## Execution spine

1. preserve the whole raw input/context;
2. understand the complete context and relationships;
3. normalize the whole context without semantic drift;
4. interpret intent and targets;
5. decide collection mode;
6. decompose only as required;
7. resolve high-confidence Domain Context Services, classification and standards/best-practice framing;
8. mark downstream unknowns without blocking a clear handoff;
9. select the canonical capability plan and establish providers/approvals;
10. execute ATLAS work and any authorized ARGUS collection work unit;
11. apply Evidence Governance and independent assurance/verification;
12. output and persist through authorized receipts;
13. project operational state through Observability/Dashboard.

## Machine-readable authority

AI systems begin at `atlas-ai.yaml`; `atlas-os.yaml` remains product/release authority. Key active contracts include:
- `spec/semantic-normalization.yaml`
- `spec/mission-control.yaml`
- `spec/control-plane.yaml`
- `spec/request-triage.yaml`
- `spec/collection-routing.yaml`
- `spec/capability-layer.yaml`
- `spec/evidence-governance.yaml`
- `spec/execution-governance.yaml`
- `spec/agent-security.yaml`
- `spec/classification-crosswalk.yaml`
- `spec/domain-capabilities.yaml`
- `spec/domain-context-services.yaml`
- `spec/domain-handoff.yaml`
- `spec/execution-spine.yaml`
- `spec/observability.yaml`
- `spec/dashboard.yaml`
- `registries/canonical-capabilities.yaml`
- `registries/domain-methods.yaml`
- `registries/taxonomies.yaml`

The active ARGUS contract is immutable and commit-pinned in `registries/domain-methods.yaml`.

See `docs/architecture/capability-layer.md` for the capability boundary and `docs/architecture/atlas-argus-collection-boundary.md` for the ATLAS/ARGUS seam.

## Release state

Stable `v2.0.2` remains blocked by external-proof controls `MIG-029` and `MIG-037`. Repository-local conformance does not substitute for independent host evidence. Candidate `v2.0.2-rc.6` / `atlas-bootstrap-2026-10-22-r10` resets the external proof target to the canonical capability layer while preserving the rc.5/r9 Collection-Need/ARGUS evidence as historical only.