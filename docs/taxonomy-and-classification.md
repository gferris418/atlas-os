# Taxonomy and industry classification

ATLAS understands the **whole available context first**, then decomposes and classifies only the facets needed to frame the request reliably. Classification must never precede or override whole-context meaning.

Classification is multi-axial: jurisdiction, buyer/end-user sector, supply-side sector, operator industry, supplier industry, product/service, platform/system, capability, procurement category, customs classification, lifecycle and information sensitivity answer different questions and must not be collapsed into one code.

ATLAS is optimized for speed and reliability. It resolves high-confidence context from the supplied input and local governed registries. It does not enter a research loop merely to complete every possible facet before handoff.

## Whole-context-first sequence

1. preserve the complete original context and critical literals;
2. understand the overall meaning, intent, actors, relationships, constraints and requested outcome;
3. normalize the whole context without changing meaning;
4. decompose only as required;
5. classify high-confidence material facets;
6. reconcile every derived facet back to the whole context;
7. preserve unresolved downstream context and hand off.

A term is not classified in isolation when its meaning depends on surrounding context. For example, `surveillance` in `coastal surveillance radar for Bangladesh navy` is interpreted in the full maritime-radar context rather than as a generic surveillance concept.

## High-confidence semantic facets

ATLAS may resolve, when supported by the input:

1. jurisdiction;
2. buyer or end-user sector;
3. supply-side sector;
4. operator industry;
5. supplier industry;
6. product or service;
7. platform or system family;
8. operating environment;
9. capability.

Lifecycle stage, procurement route, budget, quantity, exact specifications, exact product/customs/procurement codes, specific standards applicability, supplier/OEM, funding source and delivery timeline may remain unresolved. They are downstream facts, not normal semantic handoff blockers.

## Governed baseline

The taxonomy registry includes ISO 704 and ISO 1087 for terminology, ISO 25964 for thesauri and mappings, W3C SKOS for machine-readable concept schemes, ISO/IEC 11179-3 for metadata governance, ISO 3166-1 for countries, UN ISIC for economic activities, UN CPC for products and services, the WCO Harmonized System for customs, UNSPSC for procurement, and the NATO Codification System for defense logistics.

Jurisdiction-specific and regional schemes may be attached when material, including national economic/product classifications, NACE, NAICS, CPA and CPV.

An external classification applies only within its intended scope. HS is conditional on customs or cross-border trade; UNSPSC/CPV are conditional on procurement classification; NATO codification is conditional on defense supply identification. An ATLAS internal SKOS concept can recognize a capability, but it must never be presented as an external industry or product code.

## Required classification record

For each material classification that ATLAS actually resolves, record where available:

- scheme;
- version;
- code and label;
- source/issuer;
- relationship (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`, or `CANDIDATE`);
- confidence;
- applicability;
- resolution status.

Unavailable or uncertain exact codes remain unresolved. Similarity never establishes cross-scheme equivalence.

## Example: coastal surveillance radar for Bangladesh Navy

Whole-context interpretation:

> A coastal-surveillance radar product/capability context associated with the Bangladesh Navy in Bangladesh.

ATLAS can immediately resolve or frame:

| Facet | Initial context | Basis |
|---|---|---|
| Jurisdiction | Bangladesh (`BD`) | ISO 3166-1 |
| End user | Bangladesh Navy | User context |
| Domain | Defence / maritime surveillance / radar systems | Whole-context interpretation |
| Buyer/end-user sector | Public administration / defence | Contextual sector framing |
| Supply-side sector | Manufacturing / electronics / radar systems | Contextual sector framing |
| Operator industry | Defence activities (`8422`) | UN ISIC |
| Product family | Radar systems | Product context |
| Product | Coastal surveillance radar | Normalized context |
| Capability | Coastal / maritime surveillance | ATLAS capability scheme |
| Supplier industry | Candidate only | Resolve when supplier/manufacturer analysis is material |
| Customs product | Candidate only | Resolve when customs/import/export becomes material |

ATLAS does **not** stop to determine lifecycle stage, procurement route, budget, number of sites, radar band/range, supplier or exact standards applicability. Those remain explicit downstream unknowns.

The semantic status is `READY` when the whole meaning is clear. ARGUS can then investigate what is actually true in the real world.

Classification does not establish project existence, legal status, export-control classification, procurement eligibility, compliance, authority, supplier selection or any Bangladesh Navy requirement. Those claims require downstream evidence.
