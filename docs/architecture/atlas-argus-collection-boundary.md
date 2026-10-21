# ATLAS–ARGUS collection architecture

ATLAS OS is the fixed operating architecture. ARGUS is a governed intelligence collection subsystem nested inside it.

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Intent + Target Interpretation
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> ARGUS Collection Mission -> Collection Package
       -> HYBRID           -> ARGUS Collection Mission -> Collection Package + ATLAS analysis
  -> Domain Context Services
  -> ATLAS Data Plane
  -> Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

## Separation of responsibilities

- Mission Control: human objectives, approvals/rejections, pause/resume/abort, priorities, scope, collection expansion/reduction and exceptions.
- Control Plane: authoritative governance, permissions, collection-mode decision, routing, approvals, leases, lifecycle state and persistence authorization.
- Domain Context Services: canonical terminology, taxonomy, economic/industry/product/procurement/trade classifications, law, standards, frameworks, benchmarks and evidence precedence.
- ARGUS: target resolution, structured collection, acquisition, extraction, normalization, entity resolution, deduplication, corroboration, gap/conflict detection and evidence packaging.
- Data Plane: substantive ATLAS execution including analysis, forecasting, comparison, opportunity qualification and decision work.
- Assurance/Verification: checks claims, evidence, specialist returns, tests and unresolved gaps independently of collection.
- Observability: read-oriented events and measurements.
- Dashboard: read-only projection. A state-changing dashboard action becomes a Mission Control command.

## Core activation rule

Do not ask `Is this intelligence?` Ask `Does this ATLAS task require structured intelligence collection?`

| Example | Collection mode |
| --- | --- |
| Bangladesh Bank foreign exchange policy | ATLAS_DIRECT |
| ST Engineering | ARGUS_COLLECTION |
| Coastal patrol vessel for Bangladesh Coast Guard | ARGUS_COLLECTION |
| Seed cum cleaner for BADC | ARGUS_COLLECTION |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION |
| Explain Bangladesh Navy procurement regulations | ATLAS_DIRECT |
| Forecast likely Bangladesh Navy procurements over 24 months | HYBRID |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID |

## Economic and product classification

ATLAS uses multi-axial classification. Domain, sector, industry/activity, product/service, procurement category, customs code, capability, lifecycle and sensitivity remain distinct. Current governed reference schemes include ISIC Rev. 5, NACE Rev. 2.1, NAICS 2022, CPC 3.0, CPA 2.2, UNSPSC, CPV 2008, HS 2022 and NATO Codification when applicable. Crosswalks are explicit mappings, not equivalence assumptions.
