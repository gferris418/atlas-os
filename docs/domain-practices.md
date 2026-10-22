# Domain standards and best practices

ATLAS applies standards and best-practice knowledge as a **context-framing layer**, starting from the complete normalized whole context. It does not research every possible framework before downstream handoff and it does not convert a generic best-practice lens into an assumed requirement.

For each substantive semantic frame, ATLAS identifies only the standards families, regulatory context, recognized professional frameworks and international best-practice lenses that can be determined quickly and reliably from the supplied context and governed local registries.

## Whole-context rule

Standards and best-practice framing occurs only after ATLAS has:

1. preserved the complete original context;
2. understood the overall meaning, actors and relationships;
3. normalized the whole meaning without semantic drift;
4. decomposed only the facets needed for immediate framing.

A standard associated with an isolated word must never override the meaning of the whole request.

## Selection hierarchy

When exact applicability is immediately material and supported, use this precedence:

1. Applicable law and regulation.
2. Explicit binding user or contractual requirements.
3. International standards from bodies such as ISO, IEC, IEEE, W3C, IFRS Foundation, Basel Committee, or equivalent domain authorities.
4. Recognized professional frameworks.
5. Current official domain guidance.
6. Local or project practices.

The hierarchy is context-sensitive. A voluntary standard cannot override applicable law, and a global framework may require jurisdictional tailoring.

## Fast-path treatment

ATLAS may attach a standards **family** or best-practice **lens** before exact applicability is known. Examples include cybersecurity, interoperability, safety, lifecycle support, quality, testing/acceptance, maintainability, human factors and configuration management.

Exact applicability can remain unresolved for ARGUS or other downstream work. The following do **not** normally block a semantically clear handoff:

- lifecycle stage;
- procurement route;
- detailed specification;
- exact standard edition;
- exact standards applicability;
- project-specific acceptance criteria;
- supplier/OEM-specific compliance evidence.

## Record

For context that ATLAS actually resolves, record where available:

- framework identifier or family;
- issuer;
- official source;
- edition/version policy;
- relationship to the whole context;
- applicability state;
- confidence;
- unresolved conditions.

When exact applicability requires research, use `RESEARCH_REQUIRED` as an applicability state without treating the entire semantic handoff as `BLOCKED`.

## Claims

`ALIGNED` means sufficient framework context is identified for the immediate semantic frame. It does not mean certified, accredited, conformant, legally compliant, or mandatory for the downstream project.

Best practice is context, not a binding requirement. Stronger claims require scope-specific evidence from the competent authority, contract, standard, specification or verification process.

The registry is a maintained baseline and can be extended without changing the ATLAS core contract.