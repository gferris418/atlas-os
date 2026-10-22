# Sample workflow: coastal surveillance radar for Bangladesh Navy

This example shows how ATLAS processes the prompt `coastal surveillance radar for Bangladesh navy`. It demonstrates the fast semantic path before ARGUS collection. It is not a radar design, procurement recommendation, or claim that a Bangladesh Navy project exists. The corresponding machine-readable task state is in [`examples/workflows/coastal-surveillance-radar-bangladesh-navy.json`](../examples/workflows/coastal-surveillance-radar-bangladesh-navy.json).

## 1. Preserve and understand the whole context

ATLAS first reads the complete available context as one semantic unit. It does **not** classify `coastal`, `surveillance`, `radar`, `Bangladesh`, and `navy` independently and then attempt to reconstruct the meaning.

Whole-context interpretation:

> A coastal-surveillance radar product/capability context associated with the Bangladesh Navy in Bangladesh.

ATLAS preserves the untouched source prompt and the relationships between end user, jurisdiction, product and capability.

## 2. Normalize without changing meaning

Normalized form:

> **Coastal Surveillance Radar for the Bangladesh Navy**

Only grammar, capitalization and canonical terminology are normalized. ATLAS does not infer a project, tender, procurement, budget, quantity, technical specification, lifecycle stage, supplier, OEM, delivery date, or authority chain.

## 3. Decompose only after the whole meaning is stable

ATLAS then derives the minimum useful semantic facets:

| Facet | High-confidence context |
|---|---|
| Jurisdiction | Bangladesh (`ISO 3166-1: BD`) |
| End user | Bangladesh Navy |
| Domain | Defence / maritime surveillance / radar systems |
| Buyer/end-user sector | Public administration / defence / naval-maritime defence |
| Supply-side sector | Manufacturing / electronics / radar and sensor systems |
| Operator industry | Defence activities (`UN ISIC: 8422`) |
| Product family | Radar systems |
| Product | Coastal surveillance radar |
| Capability | Coastal / maritime surveillance |
| Operating environment | Coastal / littoral / maritime |

Every derived facet must remain consistent with the original whole context.

## 4. Attach classification context proportionally

ATLAS identifies relevant classification schemes without delaying handoff merely to force exact codes:

- ISO 3166 for jurisdiction;
- UN ISIC and jurisdiction-specific activity classifications for economic activity;
- UN CPC and relevant national/regional product classifications for product/service context;
- UNSPSC or CPV when procurement classification becomes material;
- WCO HS when customs/import/export becomes material;
- NATO Codification System when defence logistics becomes material;
- ATLAS capability vocabulary for internal capability concepts.

Known, supported mappings may be included. Conditional or unresolved mappings remain explicitly unresolved; ATLAS does not guess them.

## 5. Attach standards and best-practice context

ATLAS may quickly attach relevant framework families and best-practice lenses such as:

- radar and radio-frequency / spectrum context;
- electromagnetic compatibility;
- systems engineering;
- cybersecurity and information assurance;
- interoperability and open interfaces;
- quality and reliability;
- maintainability and supportability;
- lifecycle and total cost of ownership;
- testing, acceptance and validation;
- configuration and change management.

These are **context lenses, not Bangladesh Navy requirements**. Exact applicability can be determined later from evidence.

## 6. Preserve downstream unknowns without blocking

The prompt does not establish, and ATLAS does not try to resolve before handoff:

- whether any project or procurement exists;
- lifecycle stage;
- procurement route;
- budget or funding;
- quantity or number of sites;
- technical specifications, frequency band, range or performance;
- exact product, customs or procurement codes;
- exact standards applicability;
- selected or preferred supplier/OEM;
- delivery timeline.

These values travel downstream as unresolved context.

**Unknown downstream facts are not a semantic blocker.**

ATLAS blocks the normal semantic handoff only when the *meaning itself* is materially ambiguous—for example, an input such as `radar for bank` where the intended subject or entity cannot be reliably understood from the available context.

## 7. Fast handoff to ARGUS

For this example the semantic state is `READY` even though many real-world facts remain unknown.

The handoff contains, in order:

1. original whole context;
2. normalized whole context;
3. whole-context summary;
4. high-confidence semantic facets;
5. classification context and conditional candidates;
6. standards / international best-practice framing;
7. unresolved downstream context;
8. risk flags and integrity metadata.

ARGUS can then investigate what is actually true in the real world. ARGUS may return evidence and suggested refinements, but it cannot silently redefine ATLAS-owned meaning.

## 8. Boundary of responsibility

The operating distinction is:

> **ATLAS asks: “What does the complete request mean, and how should it be framed?”**

> **ARGUS asks: “What is actually true about it?”**

This keeps ATLAS fast, deterministic and reliable while preserving enough structured context for deeper downstream intelligence work.
