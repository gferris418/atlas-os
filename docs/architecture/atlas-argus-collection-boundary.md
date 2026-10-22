# ATLAS–ARGUS collection architecture

ATLAS OS is the fixed operating architecture. ARGUS is a governed intelligence collection subsystem nested inside it.

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Whole-Context Interpretation
  -> Context-Preserving Semantic Normalization
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION -> governed semantic handoff -> ARGUS Collection Mission -> Collection Package
       -> HYBRID           -> governed semantic handoff -> ARGUS Collection Mission -> Collection Package + ATLAS analysis
  -> High-Confidence Domain Context / Classification / Standards Framing
  -> ATLAS Data Plane
  -> Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

## Whole-context boundary

ATLAS must understand the complete available context as one semantic unit **before** decomposition or classification. It establishes overall meaning, intent, requested outcome, actors, relationships, jurisdiction, constraints and critical literals first. It then normalizes the whole meaning without semantic drift, decomposes only as required, and reconciles every derived facet back to the whole.

For ARGUS-bound work ATLAS is deliberately fast. It resolves high-confidence context from the supplied input and governed local registries; it does not research merely to fill lifecycle, procurement, budget, specification, exact-code, standards-applicability, funding, supplier/OEM or timing fields.

## Handoff contract

The governed ATLAS → ARGUS handoff carries:

1. original whole context;
2. normalized whole context;
3. whole-context summary and normalization notes;
4. high-confidence domain / sector / industry / product / capability context;
5. classification context and conditional candidates;
6. standards and international best-practice framing;
7. unresolved downstream context;
8. risk flags and integrity metadata.

Handoff readiness is semantic:

- `READY` — whole-context meaning is clear enough for downstream collection; unresolved downstream facts are allowed.
- `PARTIAL` — executable compatibility state for usable legacy context; unresolved material is preserved.
- `BLOCKED` — whole-context meaning is materially ambiguous or another explicit Control Plane prohibition applies.

**Classification or framework incompleteness alone never makes a clear ARGUS handoff `BLOCKED`.**

## Separation of responsibilities

- Mission Control: human objectives, approvals/rejections, pause/resume/abort, priorities, scope, collection expansion/reduction and exceptions.
- Control Plane: authoritative governance, permissions, collection-mode decision, routing, approvals, leases, lifecycle state and persistence authorization.
- Semantic Normalization / Domain Context Services: whole-context meaning, canonical terminology, taxonomy, buyer/end-user sector, supply-side sector, industry/product/capability framing, classification context, standards/framework families and best-practice lenses.
- ARGUS: target resolution, structured collection, acquisition, extraction, evidence normalization, entity/event/relationship resolution, deduplication, corroboration, gap/conflict detection and evidence packaging.
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
| Coastal surveillance radar for Bangladesh Navy | ARGUS_COLLECTION |
| Seed cum cleaner for BADC | ARGUS_COLLECTION |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION |
| Explain Bangladesh Navy procurement regulations | ATLAS_DIRECT |
| Forecast likely Bangladesh Navy procurements over 24 months | HYBRID |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID |

## Economic and product classification

ATLAS uses multi-axial classification. Domain, buyer/end-user sector, supply-side sector, industry/activity, product/service, platform/system, procurement category, customs code, capability, lifecycle and sensitivity remain distinct. Current governed reference schemes include ISIC Rev. 5, NACE Rev. 2.1, NAICS 2022, CPC 3.0, CPA 2.2, UNSPSC, CPV 2008, HS 2022 and NATO Codification when applicable.

Crosswalks are explicit mappings, not equivalence assumptions. Exact downstream codes can remain unresolved without delaying a semantically clear handoff.

## Operating distinction

> **ATLAS asks: What does the complete request mean, and how should it be framed?**

> **ARGUS asks: What is actually true about it?**
