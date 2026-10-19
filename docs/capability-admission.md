# Capability Admission Standard

ATLAS treats skills, plugins, tools, models, frameworks, and specialist methods as **providers of semantic capabilities**, not as sources of authority over the ATLAS execution spine.

The normative contract is [`spec/capability-admission.yaml`](../spec/capability-admission.yaml).

## Admission model

A provider may be classified as:

- `APPROVED` — bounded production use is supported by the required evidence.
- `CONDITIONAL` — useful, but a named dependency, runtime surface, security condition, or missing proof must be resolved at routing time.
- `EXPERIMENTAL` — bounded evaluation only; results cannot silently become canonical or consequential.
- `QUARANTINED` — blocked pending remediation or evidence.
- `REJECTED` — not routed for the assessed capability.
- `RETIRED` — previously admitted, retained for lineage only.

ATLAS does not infer provider trust from installation, connector availability, popularity, or a clean static scan. Static quality review, security review, and measured benchmark evidence are separate evidence classes.

## Current evaluated reference providers

The following provider decisions record the October 2026 architecture review. They are **reference mappings**, not unconditional runtime dependencies.

| Provider / pattern source | ATLAS role | Current disposition | Boundary |
| --- | --- | --- | --- |
| Horizon Forge | Forecasting / foresight methodology | ADAPT | Use scan, evidence, scenarios, red-team, update, preserved-vintage, and calibration mechanics; ATLAS owns the canonical forecast record and broader geopolitical/strategic scope. |
| Adaptive Task Routing | Context/model/reasoning routing | ADAPT | Use routing mechanics under the ATLAS control plane; it does not own final execution authority. |
| Injection Checker | Untrusted-content assurance | APPROVED pattern | Apply to retrieved text, files, images, tool results, memory, and agent-tool paths when injection risk is material. |
| Memory Keeper | Durable project-state discipline | ADAPT | Use audit/repair/recovery/verification mechanics; canonical external evidence remains higher authority than memory. |
| Canonical Memory Verifier | Memory-integrity and supersession checks | APPROVED pattern | Historical authority cannot become current execution approval; conformance is not factuality proof. |
| Plugin Eval | Capability evaluation | APPROVED pattern | Use static evaluation and metric packs; measured benchmark claims require an actual benchmark harness. |
| Agent SkillGuard | Pre-admission static security review | APPROVED pattern | Clean scan is not certification; findings require file/line review and bounded remediation. |
| Data Analytics | Measurement / learning loop | ADAPT | Use for KPI design, calibration, error attribution, reliability, latency/cost, and trend diagnostics; not as a substitute for strategic reasoning. |
| Agentic Atlas | Architecture advisory | CONDITIONAL | Useful conceptually, but its provider-specific Atlas MCP surface is not universally available; never make the core dependent on it. |
| Autonomous CIO selected modules | Decision challenge / assumption testing | BORROW / ADAPT | Use assumption mining, drift detection, challenge, backtesting, risk-chain, and post-decision learning selectively; do not nest another operating system inside ATLAS. |
| Agent Skills / Superpowers / Matt skills | Engineering execution | ROUTE SELECTIVELY | Use the narrowest task-fit workflow; do not activate overlapping engineering packs by default. |

These dispositions are architecture decisions, not measured performance rankings. Provider-specific token, latency, cost, error-rate, and accuracy claims remain unverified until benchmarked in the target runtime.

## Forecasting profile

ATLAS forecasting and foresight should support the following provider-independent mechanics:

1. **Horizon scan** — define the decision boundary, causal growth/decline mechanisms, triggers, constraints, contrary signals, and second-order dependencies.
2. **Evidence assurance** — preserve source lineage, dates, definitions, units, geography, incentives, contradictions, and contrary evidence.
3. **Scenario construction** — separate assumptions, scenarios, event probabilities, sensitivities, and unsupported numerical precision.
4. **Adversarial review** — identify the weakest premise, strongest rival explanation, failure analogues, substitution, policy, financing, and observations that would reverse the conclusion.
5. **Forecast register** — freeze prediction vintage, horizon, event definition, probability, evidence state, and signposts.
6. **Update discipline** — preserve prior forecasts, distinguish new information from duplicate coverage/noise, and record old/new probabilities with reasons.
7. **Outcome scoring** — resolve only under predeclared rules and calculate calibration/error metrics such as Brier score where appropriate.
8. **Learning loop** — attribute errors to evidence, assumptions, model/provider behavior, scenario structure, or decision process before changing the framework.

A sophisticated process is not evidence of forecasting accuracy. Accuracy is established prospectively through frozen forecasts, resolved outcomes, suitable comparators, and adequate sample size.

## Assurance pipeline

```text
Candidate provider
      ↓
Provenance / identity
      ↓
Permission + blast-radius review
      ↓
Injection / secret / data-boundary review
      ↓
Dependency + runtime-surface check
      ↓
Static quality evaluation
      ↓
Task benchmark when material
      ↓
Cost / latency / reliability evidence
      ↓
Overlap + fallback review
      ↓
Admission decision
      ↓
Capability Registry / governed adapter
```

No stage converts missing evidence into a pass.

## ARGUS boundary

ARGUS remains an ATLAS-governed specialist domain method. External provider logic used by ARGUS must remain subordinate to the ARGUS activation contract and the ATLAS domain-context handoff.

Current design intent:

- **Capture Team** methodology may be adapted for discover → qualify → prioritize → brief logic, while ARGUS retains its own maturity, evidence, reconciliation, commercial scoring, and decision states.
- **Proposal Team** belongs downstream of an approved pursuit/PX decision and must not be folded into ARGUS discovery or qualification.
- Procurement search, web research, company intelligence, trade intelligence, legal/regulatory intelligence, and financial intelligence providers are replaceable source adapters; provider identity must not become ARGUS record identity.
- ARGUS may propose domain actions; ATLAS retains approval, verification, persistence, and final delivery authority.

## Promotion to hard integration

A reference provider may become a governed integration only when:

1. the provider and version are identifiable;
2. the target surface exposes the required operations;
3. permissions and data boundaries are explicit;
4. failure and fallback semantics are defined;
5. security review is complete for the intended blast radius;
6. benchmark evidence exists when performance or accuracy is material;
7. the adapter has a versioned contract and regression coverage; and
8. removal or provider substitution does not redefine ATLAS core semantics.

Until those conditions are met, the provider remains advisory, conditional, or replaceable.
