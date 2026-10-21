# Sample workflow: coastal surveillance radar for Bangladesh Navy

This example shows how ATLAS processes the prompt `coastal surveillance radar for Bangladesh navy`. It is a governance example, not a radar design or procurement recommendation. The corresponding machine-readable task state is in [`examples/workflows/coastal-surveillance-radar-bangladesh-navy.json`](../examples/workflows/coastal-surveillance-radar-bangladesh-navy.json).

## 1. Taxonomy layer and input boundary

ATLAS preserves the untouched prompt, then uses its internal hierarchy to route the task before interpreting an outcome:

- Domain: government and public sector
- Sub-domain: defense and national security
- Vertical: maritime defense
- Artifact class: surveillance-sensor capability

These are internal routing concepts, not external industry, product, customs, procurement, or legal codes. The layer identifies candidate schemes such as ISO 3166-1, UN ISIC, UN CPC, HS, UNSPSC, or the NATO Codification System; it does not assign a code until later context establishes applicability.

## 2. Intent normalization and material context

ATLAS preserves the literal entities and capability terms:

- `Bangladesh`
- `navy`
- `coastal surveillance radar`

The request does not state the intended outcome. ATLAS does not silently reinterpret it as acquisition, technical design, market research, or operational planning.

The domain-neutral intent profile is therefore `GENERAL_RESEARCH` or `GENERAL_TASK`, depending on the surrounding request, with no authority to route a provider. If the user instead asks to “find public procurement opportunities,” the profile becomes `OPPORTUNITY_IDENTIFICATION` and recommends government/public-sector opportunity intelligence plus public research as semantic needs. ARGUS remains only a candidate provider until the later routing preview is approved.

The Who/What/Where/When/Why/Which/How/How Much matrix is applied proportionally. Only missing answers that could change scope, authorization, safety, classification, or the deliverable become clarification questions.

## 3. Task classification and depth

Initial task classes are `RESEARCH`, `ANALYSIS`, `PLANNING`, and `MULTI_STAGE`. Because the subject is defense-related and materially ambiguous, the initial execution depth is `L3`.

## 4. Industry, product, capability, and other domain classification

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

## 5. Material clarification gate

ATLAS pauses detailed work and asks:

> What outcome and lifecycle stage are intended—public market research, requirements definition, procurement planning, system design, integration, operation, or sustainment—and what information is authorized for use?

This single question controls the downstream workflow. Until it is answered, task status is `BLOCKED` and domain-framework alignment is `RESEARCH_REQUIRED`.

## 6. Conditional branch activation

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

## 7. Binding-requirement and framework alignment

ATLAS next identifies applicable Bangladesh law, policy, procurement authority, spectrum authority, security classification, contractual requirements, and supplier/export jurisdictions. Only then does it select current international standards and professional frameworks. A candidate standard is recorded as applicable, not applicable, conditional, or research-required; alignment never becomes a compliance claim without evidence.

Classification systems and governing requirements remain separate. ISO 3166-1, UN ISIC, UN CPC, HS, UNSPSC, and the NATO Codification System classify particular facets when applicable. Engineering standards, military standards, and Bangladesh procurement law or rules govern requirements and execution; their current official status and applicability must be verified rather than inferred from the prompt.

## 8. Capability audit, plan, evidence, and approvals

The execution plan is built from the selected branch. It names required sources, unresolved dependencies, approval boundaries, verification methods, and deliverables. The required semantic capabilities are then mapped to the smallest admitted set of native host features, skills, plugins, tools, or specialist methods after provenance, permissions, security, dependencies, evidence, overlap, and fallback behavior are checked.

Before any selected provider is routed, ATLAS shows a digest-bound preview stating what it proposes to do and how. For a public opportunity-intelligence request this can identify ARGUS as the specialist method, Evidence Research as the research method, and Public Research as the read-only retrieval tool, with each provider's exact purpose, prerequisites, data scope, fallback, and unresolved gates. Rejection, omission, a stale digest, or a changed proposal blocks routing. Even an approved ARGUS proposal remains blocked until its Domain Context Handoff is acceptable.

Public-source analysis may proceed within the agreed scope only after the applicable preview and gates pass. Access to restricted sources, external communications, procurement actions, publication, or other high-impact actions requires the relevant authorization.

## 9. Data plane, assurance, and delivery

The data plane executes one authorized atomic unit at a time. Generated work is not considered verified: ATLAS checks requirements and evidence independently before it persists or delivers the result.

The deliverable reports:

- the interpreted objective and authorized scope;
- resolved and unresolved classification facets;
- applicable requirements and frameworks with editions and sources;
- evidence, assumptions, conflicts, and gaps;
- recommendations appropriate to the selected lifecycle stage;
- verification performed and any decisions or approvals still required.

If the user answers, for example, “public market research for an early capability assessment; public information only,” ATLAS can safely continue into public-source capability criteria, market structure, standards research, and an evidence-backed options framework. It still does not infer permission for procurement, supplier contact, sensitive performance analysis, or operational planning.
