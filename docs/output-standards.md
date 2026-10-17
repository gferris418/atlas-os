# Output standards and profiles

ATLAS improves host-generated output through small, task-fit contracts. The host remains responsible for natural-language generation, reasoning, conversation, and tool use. ATLAS selects a profile, preserves explicit user format choices, and validates only requirements that can materially improve the deliverable.

## Profiles

| Profile | Use | Default shape |
|---|---|---|
| `output.answer-concise` | Simple answers | Outcome, then essential context |
| `output.analysis-standard` | Analysis | Conclusion, evidence, implications |
| `output.decision-brief` | Decisions | Recommendation, evidence, risks, next action |
| `output.research-sourced` | Research | Findings, citations, confidence, gaps |
| `output.execution-progress` | Multi-step work | Dashboard, completed, active, next |
| `output.technical-spec` | Technical work | Scope, requirements, interfaces, verification |
| `output.data-structured` | Machine consumption | Schema-valid JSON, CSV, or YAML |
| `output.artifact-delivery` | Files and documents | Outcome, artifacts, verification, limitations |

Selection order is explicit user choice, binding deliverable or tool contract, task/audience fit, then the concise-answer default. A user-requested available profile is never silently replaced by automatic selection.

Each profile also declares a logical canonical-library collection and a filename extension for every supported format. This makes outputs discoverable without forcing every adapter to use the same physical storage service. Delivery ends with a verified `SAVED` receipt or an explicit `BLOCKED` or `CAPABILITY_UNAVAILABLE` state.

## Progressive disclosure

Human-readable output starts with the outcome. Material evidence, actions, and risks follow. Technical detail, source lists, appendices, and machine-readable artifacts appear only when they are useful or requested.

The structured output envelope in `schemas/output.schema.json` is intended for workflows and integrations. Ordinary conversation does not need to be wrapped in JSON or validated against a schema.

## Visuals

Use the smallest visual that improves understanding: a table for mappings, a flow for sequence, a timeline for change, a tree for hierarchy, a progress bar for execution, or a chart for quantitative relationships. Do not add decorative diagrams, image generation, or expensive rendering when short prose is clearer.

## Validation

Validation is proportional:

- validate JSON, CSV, YAML, API contracts, and other machine-readable outputs;
- verify required citations and evidence for research outputs;
- confirm delivered artifacts exist and use the requested format;
- apply accessibility checks to user-facing web and document artifacts when applicable;
- keep ordinary conversational validation limited to correctness, relevance, clarity, and material evidence.

Format validity is not factual correctness. Evidence quality, authorization, execution, verification, acceptance, and compliance remain separate claims.
