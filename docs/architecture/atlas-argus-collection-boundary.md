# ATLAS–ARGUS collection architecture

ATLAS OS is the fixed operating architecture. ARGUS is a governed government commercial opportunity intelligence subsystem nested inside it.

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Intent + Target Interpretation
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> ARGUS Collection Mission -> Commercial Opportunity Intelligence Package
       -> HYBRID           -> ARGUS Package + ATLAS substantive analysis/decision
  -> Canonical Capability Planning
  -> Domain Context Services
  -> ATLAS Data Plane
  -> Evidence Governance / Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

## Separation of responsibilities

- Mission Control: human objectives, approvals/rejections, pause/resume/abort, priorities, scope, collection expansion/reduction and exceptions.
- Control Plane: authoritative governance, permissions, collection-mode decision, routing, approvals, leases, lifecycle state and persistence authorization.
- Domain Context Services: canonical terminology, taxonomy, economic/industry/product/procurement/trade classifications, law, international standards, frameworks, benchmarks and evidence precedence.
- ARGUS: target resolution, structured collection, evidence reconciliation, pre-PX opportunity identity/lifecycle, demand intelligence, supply intelligence, supplier/OEM partnerability, supplier matching, advisory opportunity qualification, early-warning events, Rapid Tender collection, gaps/conflicts/coverage and evidence packaging.
- Data Plane: substantive ATLAS execution including analysis, comparison, forecasting/scenarios, authoritative opportunity priority and decision work.
- Evidence Governance / Assurance / Verification: determines what evidence can legitimately support and independently checks specialist returns, claims, tests and unresolved gaps.
- Observability: read-oriented events and measurements.
- Dashboard: read-only projection. A state-changing dashboard action becomes a Mission Control command.

## Core activation rule

Do not ask `Is this intelligence?` Ask `Does this ATLAS task require structured intelligence collection?`

| Example | Collection mode | Procurement Intelligence? |
| --- | --- | --- |
| Bangladesh Bank foreign exchange policy | ATLAS_DIRECT | No |
| ST Engineering | ARGUS_COLLECTION | No |
| What capability gaps could Bangladesh Coast Guard address with foreign technology? | ARGUS_COLLECTION | No |
| Where could ST Engineering coastal surveillance technology fit in Bangladesh government? | ARGUS_COLLECTION | No |
| Coastal patrol vessel for Bangladesh Coast Guard | ARGUS_COLLECTION | Not unless procurement semantics are requested |
| Seed cum cleaner for BADC | ARGUS_COLLECTION | Not unless procurement semantics are requested |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION | Yes |
| Live tender closes in 7 days; find eligible OEMs | ARGUS_COLLECTION / RAPID_TENDER | Yes |
| Explain Bangladesh Navy procurement regulations | ATLAS_DIRECT | Yes, ATLAS analysis only |
| Forecast likely Bangladesh Navy procurements over 24 months | HYBRID | Yes |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID | Not automatically |

## Commercial opportunity boundary

ARGUS v3 treats a persistent commercial opportunity as an intelligence object before a PX identity exists. ARGUS may assign `ARGUS-OPP-YYYY-NNNNNN` when a credible commercial possibility requires persistent tracking. ATLAS assigns `YYYY_PXNNNNN_SHORTNAME` only through governed `PROMOTE_TO_PX` or explicit commercial-pipeline registration.

ARGUS tracks the S0–S9 lifecycle and the separate `SHAPE`, `POSITION`, `REACT`, `EXPAND` mode. One tender does not automatically create one opportunity, and one opportunity may legitimately link to multiple packages, tenders, amendments, rebids or follow-ons.

ARGUS may calculate supplier matches, partnerability and advisory qualification. ATLAS owns canonical evidence acceptance, authoritative priority, PX promotion, pursuit/bid decisions, external-action authorization, persistence and final delivery.

> **ARGUS may calculate and recommend; ATLAS authorizes and decides.**

## Evidence and probability separation

Keep these distinct:

- evidence confidence;
- procurement realization probability;
- Access Asia success probability;
- supplier-match confidence.

None is interchangeable with another, and none automatically establishes an ATLAS business decision.

## Economic and product classification

ATLAS uses multi-axial classification. Domain, sector, industry/activity, product/service, procurement category, customs code, capability, lifecycle and sensitivity remain distinct. Current governed reference schemes include ISIC Rev. 5, NACE Rev. 2.1, NAICS 2022, CPC 3.0, CPA 2.2, UNSPSC, CPV 2008, HS 2022 and NATO Codification when applicable. Crosswalks are explicit mappings, not equivalence assumptions.
