# Architecture

ATLAS-OS is the fixed AI-agent execution-governance architecture. ARGUS is a nested, governed intelligence collection subsystem—not a peer operating system.

```text
HUMAN / EVENT
    |
    v
MISSION CONTROL
    |
    v
CONTROL PLANE
    |
    v
INTENT + TARGET INTERPRETATION
    |
    v
COLLECTION-NEED GATE
    |---- NONE -----------------------> ATLAS
    |---- ATLAS_DIRECT ---------------> ATLAS research/retrieval
    |---- ARGUS_COLLECTION -----------> ARGUS collection package
    |---- HYBRID ---------------------> ARGUS collection + ATLAS analysis
    |
    v
DOMAIN CONTEXT SERVICES
    |
    v
ATLAS DATA PLANE
    |
    v
ASSURANCE / VERIFICATION
    |
    v
OUTPUT / PERSISTENCE
    |
    v
OBSERVABILITY -> DASHBOARD
```

## Authorities

- **Mission Control** — human objective, approvals/rejections, pause/resume/abort, scope, priority, escalation and collection expansion/reduction requests.
- **Control Plane** — authoritative policy, permissions, plan/work-unit state, Collection-Need Gate, routing, approvals, leases, lifecycle and persistence authorization.
- **Domain Context Services** — canonical terminology, taxonomy, economic/industry/product/procurement/trade context, ontology, law, standards, frameworks, benchmarks and evidence precedence.
- **Data Plane** — substantive ATLAS execution, including policy analysis, strategic analysis, forecasting, scenarios, comparison, opportunity qualification and decision support.
- **Assurance / Verification** — independent checking of claims, evidence, specialist returns, tests, conflicts and unresolved gaps.
- **Observability** — read-oriented operational events and measurements.
- **Dashboard** — human-facing read-only projection. A state-changing Dashboard action becomes a Mission Control command.

`spec/domain-intelligence.yaml` is retained only as a deprecated compatibility alias to `spec/domain-context-services.yaml` and is not active machine authority.

## Collection-Need Gate

Task intent and collection mechanism are independent. ATLAS asks: **Does this task require structured intelligence collection?**

Collection modes:
- `NONE`
- `ATLAS_DIRECT`
- `ARGUS_COLLECTION`
- `HYBRID`

Representative routing:
- Bangladesh Bank foreign exchange policy → `ATLAS_DIRECT`
- ST Engineering → `ARGUS_COLLECTION`
- coastal patrol vessel for Bangladesh Coast Guard → `ARGUS_COLLECTION`
- seed cum cleaner for BADC → `ARGUS_COLLECTION`
- annual procurement plan of Bangladesh Navy → `ARGUS_COLLECTION`
- explain Bangladesh Navy procurement regulations → `ATLAS_DIRECT`
- forecast likely Bangladesh Navy procurements over 24 months → `HYBRID`
- compare ST Engineering vs L3Harris for Bangladesh opportunities → `HYBRID`

Legacy `GENERAL_SEARCH`, `GENERAL_TASK`, and `INTELLIGENCE` remain compatibility route labels. They are not the semantic ARGUS activation authority.

## ARGUS boundary

ARGUS capability is `intelligence_collection`. Within an ATLAS-authorized mission ARGUS may resolve targets, plan collection, discover/acquire sources, extract/normalize evidence, resolve entities, deduplicate, suggest collection-side classifications, corroborate, reconcile sources, expose gaps/conflicts/coverage and return an `IntelligenceCollectionPackage`.

ATLAS retains planning, permissions, approvals, canonical classification, strategic analysis, forecasting/scenarios, opportunity qualification, pursuit decisions, assurance, persistence authorization, observability, Dashboard and final delivery. Public-sector I0–I9 maturity and `PROMOTE_TO_PX` remain specialization semantics, not universal ARGUS output.

## Multi-axial classification

ATLAS never collapses domain, sector, industry/activity, product/service, procurement category, customs/trade code and capability into one code. Current governed reference schemes include ISIC Rev. 5, NACE Rev. 2.1, NAICS 2022, CPC 3.0, CPA 2.2, UNSPSC, CPV 2008, HS 2022 and NATO Codification when materially applicable. Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`). Classification metadata does not prove compliance or eligibility.

## Provider independence

Capabilities are semantic contracts; skills, tools, plugins, models, connectors and specialist methods are providers. Availability is not admission. Installation is not trust. Provider routing remains subordinate to `spec/capability-admission.yaml`, digest-bound routing previews and Control Plane approval policy.
