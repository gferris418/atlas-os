# ATLAS-OS

ATLAS-OS is a **model-agnostic execution-governance architecture for AI agents**. It remains the single operating architecture between user intent and verified delivery. ARGUS is nested inside ATLAS as the governed government commercial opportunity intelligence subsystem; it is not a peer operating system or alternative execution spine.

It is **not a desktop operating system** and does not replace the host model, conversation engine, browser, tool runtime, or device OS.

**Current candidate:** `v2.0.2-rc.7`  
**Control revision:** `atlas-bootstrap-2026-10-22-r11`  
**Target stable:** `v2.0.2`  
**Information classification:** Internal  
**License:** [MIT](LICENSE)  
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
       -> ARGUS_COLLECTION -> ARGUS bounded commercial-opportunity intelligence -> evidence package
       -> HYBRID           -> ARGUS intelligence + ATLAS substantive analysis/decision
  -> Canonical Capability Planning
  -> Domain Context Services
  -> Data Plane
  -> Evidence Governance / Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

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
ATLAS owns canonical terminology, taxonomy, economic sector context, operator/supplier industry, product/service, procurement, trade/customs and defense-logistics classification plus ontology, law, international standards, professional frameworks, benchmarks and evidence precedence. `spec/domain-intelligence.yaml` remains only as a deprecated compatibility alias to this layer and is not an active machine authority.

### Data Plane
ATLAS performs substantive work: ordinary research, writing, calculation, coding, policy analysis, comparison, strategic analysis, forecasting, scenarios, authoritative commercial prioritization and decision support. ARGUS may supply advisory opportunity qualification and supplier-match assessments; those do not become authoritative ATLAS business state automatically.

### ARGUS Government Commercial Opportunity Intelligence
ARGUS activates only when `collection_mode` is `ARGUS_COLLECTION` or `HYBRID`. Its canonical capability is `intelligence_collection` / `argus.collection`.

ARGUS `3.0.0-rc.1` is commit-pinned in `registries/domain-methods.yaml`. Within an ATLAS-authorized mission it uses bounded collection tradecraft (`PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`) and may also:

- detect government needs and capability gaps before a project or tender exists;
- track S0–S9 government-opportunity lifecycle events;
- create a persistent pre-PX intelligence identity `ARGUS-OPP-YYYY-NNNNNN` when tracking is justified;
- support `SHAPE`, `POSITION`, `REACT`, and `EXPAND` commercial modes;
- build supplier/OEM universes and assess partnerability;
- match demand to international suppliers and technologies;
- calculate advisory opportunity qualification and supplier-match scores;
- track policy, programme, funding, approval, procurement, award and expansion events;
- enter `RAPID_TENDER` collection when first material discovery occurs at live-tender stage;
- return opportunities, supplier intelligence, supplier matches, qualification recommendations, detection metrics, evidence, gaps and conflicts to ATLAS.

ATLAS retains canonical Evidence Governance and taxonomy acceptance, authoritative opportunity priority, `PROMOTE_TO_PX`, pursuit and bid/no-bid decisions, external-action authorization, assurance, persistence and final delivery.

The Access Asia commercial identity is assigned only after ATLAS-authorized promotion. The permanent ARGUS intelligence identity and the PX lineage remain linked rather than replacing one another.

## Collection-Need Gate

Task intent and collection mechanism are independent. Early commercial opportunity intelligence is also distinct from procurement intelligence.

| Request | ATLAS capability/task | Collection mode | ARGUS |
| --- | --- | --- | --- |
| Bangladesh Bank foreign exchange policy | economic-policy-intelligence | ATLAS_DIRECT | No |
| ST Engineering | target collection | ARGUS_COLLECTION | Yes |
| What capability gaps could Bangladesh Coast Guard address with foreign technology? | early opportunity / need discovery | ARGUS_COLLECTION | Yes |
| Where could ST Engineering coastal surveillance technology fit in Bangladesh government? | supply-first opportunity matching | ARGUS_COLLECTION | Yes |
| Coastal patrol vessel for Bangladesh Coast Guard | buyer/solution opportunity collection | ARGUS_COLLECTION | Yes |
| Seed cum cleaner for BADC | buyer/solution opportunity collection | ARGUS_COLLECTION | Yes |
| Annual procurement plan of Bangladesh Navy | procurement-intelligence | ARGUS_COLLECTION | Yes |
| A live tender closes in 7 days; find eligible international OEMs | procurement-intelligence + Rapid Tender | ARGUS_COLLECTION | Yes |
| Explain Bangladesh Navy procurement regulations | policy/procurement analysis | ATLAS_DIRECT | No |
| Forecast likely Navy procurements over 24 months | procurement-intelligence / forecast | HYBRID | Yes, collection only |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | analysis/decision | HYBRID | Yes, collection + advisory matching |
| Rank suitable OEMs and recommend whether Access Asia should pursue | decision | HYBRID | Yes; ATLAS makes final pursuit decision |
| Review attached commercial agreement and propose redlines | commercial-contract-review | NONE | No |
| Calculate commission margin and FX exposure from supplied figures | corporate-finance | NONE | No |

Need/gap discovery, legitimate opportunity development and supply-first technology matching do **not** automatically activate `atlas.procurement-intelligence` when procurement semantics are absent. Procurement plans, formal tenders/acquisitions, eligibility/evaluation, bid/no-bid and `RAPID_TENDER` do.

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

Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`) with source/target scheme edition, code, label, basis, provenance, verification and confidence. Classification never proves compliance, procurement eligibility or legal status.

## Execution spine

1. preserve raw input/context;
2. interpret intent and targets;
3. decide collection mode;
4. select the canonical capability plan;
5. resolve material Domain Context Services and classification crosswalks;
6. establish plan/providers/approvals;
7. execute ATLAS work and any authorized ARGUS collection work unit;
8. apply Evidence Governance and independent assurance/verification;
9. output and persist through authorized receipts;
10. project operational state through Observability/Dashboard.

## Machine-readable authority

AI systems begin at `atlas-ai.yaml`; `atlas-os.yaml` remains product/release authority. Key active contracts include:
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
- `spec/execution-spine.yaml`
- `spec/observability.yaml`
- `spec/dashboard.yaml`
- `registries/canonical-capabilities.yaml`
- `registries/domain-methods.yaml`
- `registries/taxonomies.yaml`
- `integrations/access-asia/opportunity-lifecycle.yaml`

The active ARGUS contract is immutable and commit-pinned in `registries/domain-methods.yaml`.

See `docs/architecture/capability-layer.md` for the capability boundary and `docs/architecture/atlas-argus-collection-boundary.md` for the ATLAS/ARGUS seam.

## Release state

Stable `v2.0.2` remains blocked by external-proof controls `MIG-029` and `MIG-037`. Repository-local conformance does not substitute for independent host evidence. Candidate `v2.0.2-rc.7` / `atlas-bootstrap-2026-10-22-r11` is the current external-proof target and integrates ARGUS `3.0.0-rc.1` government commercial opportunity intelligence. Earlier rc.5/r9 Collection-Need evidence and rc.6/r10 capability-layer evidence remain historical only.
