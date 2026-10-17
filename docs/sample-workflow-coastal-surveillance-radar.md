# Sample workflow: coastal surveillance radar for Bangladesh Navy

This example shows how ATLAS processes the prompt `coastal surveillance radar for Bangladesh navy`. It is a governance example, not a radar design or procurement recommendation. The corresponding machine-readable task state is in [`examples/workflows/coastal-surveillance-radar-bangladesh-navy.json`](../examples/workflows/coastal-surveillance-radar-bangladesh-navy.json).

## 1. Intake and normalization

ATLAS preserves the literal entities and capability terms:

- `Bangladesh`
- `navy`
- `coastal surveillance radar`

The request does not state the intended outcome. ATLAS does not silently reinterpret it as acquisition, technical design, market research, or operational planning.

## 2. Task classification and depth

Initial task classes are `RESEARCH`, `ANALYSIS`, `PLANNING`, and `MULTI_STAGE`. Because the subject is defense-related and materially ambiguous, the initial execution depth is `L3`.

## 3. Domain classification

ATLAS resolves independent facets:

| Facet | Result | State |
|---|---|---|
| Jurisdiction | Bangladesh (`ISO 3166-1: BD`) | Resolved |
| Operator industry | Defence activities (`UN ISIC: 8422`) | Resolved |
| Capability | Coastal surveillance radar | Resolved internal SKOS concept |
| Supplier industry | Navigation/control equipment manufacturing (`UN ISIC: 2651`) | Conditional on supplier analysis |
| Customs product | Radar and related radio apparatus (`HS 8526`) | Conditional on import/export or customs scope |
| Lifecycle stage | Research, requirements, acquisition, design, integration, operation, or sustainment | Unresolved |
| Information sensitivity | Public, controlled, restricted, classified, or unknown | Unresolved |

Risk flags are `defense`, `dual-use`, `national-security`, and `operational-security`. Classification status is `PARTIAL`; no conditional code is treated as applicable yet.

## 4. Material clarification gate

ATLAS pauses detailed work and asks:

> What outcome and lifecycle stage are intended—public market research, requirements definition, procurement planning, system design, integration, operation, or sustainment—and what information is authorized for use?

This single question controls the downstream workflow. Until it is answered, task status is `BLOCKED` and domain-framework alignment is `RESEARCH_REQUIRED`.

## 5. Conditional branch activation

The answer determines which branches activate:

| User intent | Activated classification and research |
|---|---|
| Public market research | Public-source supplier/product taxonomy, evidence quality, current-market verification |
| Requirements definition | Capability taxonomy, systems engineering, safety, cybersecurity, human factors, spectrum and maritime requirements |
| Procurement planning | Supplier industry, UNSPSC or applicable procurement scheme, Bangladesh procurement requirements, assurance and acceptance criteria |
| Import/export analysis | WCO HS, competent export-control regimes for all relevant jurisdictions, licensing and end-use evidence |
| Defense logistics | NATO Codification System only if applicable and authoritative code access is available |
| Design or integration | Authorized technical scope, interface/security boundaries, verification strategy, and current engineering standards |
| Operations or sustainment | Authorized operational scope, maintenance, availability, training, configuration, incident, and information-security controls |

## 6. Binding-requirement and framework alignment

ATLAS next identifies applicable Bangladesh law, policy, procurement authority, spectrum authority, security classification, contractual requirements, and supplier/export jurisdictions. Only then does it select current international standards and professional frameworks. A candidate standard is recorded as applicable, not applicable, conditional, or research-required; alignment never becomes a compliance claim without evidence.

## 7. Plan, evidence, and approvals

The execution plan is built from the selected branch. It names required sources, unresolved dependencies, approval boundaries, verification methods, and deliverables. Public-source analysis may proceed within the agreed scope. Access to restricted sources, external communications, procurement actions, publication, or other high-impact actions requires the relevant authorization.

## 8. Delivery

The deliverable reports:

- the interpreted objective and authorized scope;
- resolved and unresolved classification facets;
- applicable requirements and frameworks with editions and sources;
- evidence, assumptions, conflicts, and gaps;
- recommendations appropriate to the selected lifecycle stage;
- verification performed and any decisions or approvals still required.

If the user answers, for example, “public market research for an early capability assessment; public information only,” ATLAS can safely continue into public-source capability criteria, market structure, standards research, and an evidence-backed options framework. It still does not infer permission for procurement, supplier contact, sensitive performance analysis, or operational planning.
