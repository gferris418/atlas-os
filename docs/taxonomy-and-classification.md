# Taxonomy and industry classification

When classification can materially improve a result, ATLAS classifies the relevant context before it chooses standards, frameworks, sources, or execution controls. It uses capable host-language understanding to identify candidates and the governed registry to validate and record them. Classification is multi-axial: a country, operator, supplier, product, capability, lifecycle stage, and information sensitivity answer different questions and must not be collapsed into one code. Facets that cannot change the task create no recordkeeping obligation.

## Mandatory classification sequence

ATLAS starts with taxonomy selection. It first determines which governed classification standards are applicable and verifies their scope, authority, version policy, and official source. Only then does it assign codes or concepts to material domain facets in this order:

1. jurisdiction;
2. operator industry;
3. supplier industry;
4. product or service;
5. capability;
6. lifecycle stage;
7. stakeholder; and
8. information sensitivity.

Conditional schemes are activated only when their context applies. For example, HS is not selected merely because a physical product is mentioned; customs or cross-border trade must be in scope. Domain-law, standards, framework, evidence, planning, and execution work begins only after this taxonomy-first classification is complete or its unresolved facets are explicitly preserved.

## Governed baseline

The taxonomy registry includes ISO 704 and ISO 1087 for terminology, ISO 25964 for thesauri and mappings, W3C SKOS for machine-readable concept schemes, ISO/IEC 11179-3 for metadata governance, ISO 3166-1 for countries, UN ISIC for economic activities, UN CPC for products and services, the WCO Harmonized System for customs, UNSPSC for procurement, and the NATO Codification System for defense logistics.

An external classification applies only within its intended scope. HS is conditional on customs or cross-border trade; UNSPSC is conditional on procurement; NATO codification is conditional on defense supply identification. An ATLAS internal SKOS concept can recognize a capability, but it must never be presented as an external industry or product code.

## Required classification record

For each material facet, record the taxonomy identifier, version policy, code, label, source, applicability, and evidence. Preserve unresolved facets and conditional candidates. Crosswalks must be explicit and versioned; similarity does not establish equivalence.

## Example: coastal surveillance radar for Bangladesh Navy

The prompt first selects the applicable taxonomy standards, then produces a partial classification:

| Facet | Initial result | Basis |
|---|---|---|
| Jurisdiction | Bangladesh (`BD`) | ISO 3166-1 |
| Operator industry | Defence activities (`8422`) | UN ISIC |
| Capability | Coastal surveillance radar | ATLAS capability scheme modeled in SKOS |
| Supplier industry | Conditional candidate | Apply only for supplier/manufacturer analysis |
| Customs product | HS heading `8526`, conditional candidate | Apply only for customs/import/export scope |
| Lifecycle stage | Unresolved | The prompt does not say research, requirements, acquisition, design, integration, operation, or sustainment |
| Sensitivity/risk | Defense, national security, dual use, operational security | Governed risk flags |

The next step is not to design or recommend a radar. ATLAS asks only the material scope question: what outcome and lifecycle stage are intended, and what information is authorized and safe to use? It then determines whether supplier, procurement, trade/export, defense-logistics, cybersecurity, safety, spectrum, maritime, systems-engineering, and Bangladesh-specific requirements are in scope. Detailed framework selection follows that classification and must use current official sources.

Classification does not establish legal status, export-control classification, procurement eligibility, compliance, or authorization. Those claims require the competent jurisdiction, current rules, and scope-specific evidence.
