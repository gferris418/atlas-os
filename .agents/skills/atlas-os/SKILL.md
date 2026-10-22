---
name: atlas-os
description: Apply the ATLAS-OS execution-governance contract to AI-agent work using the current host's native capabilities.
version: 2.0.2-rc.6
metadata:
  atlas:
    control_revision: atlas-bootstrap-2026-10-22-r10
    ai_entrypoint: atlas-ai.yaml
  hermes:
    tags: [governance, planning, capability-routing, collection, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply, or govern work with ATLAS-OS, or when a task explicitly requires the ATLAS execution spine.

## Canonical preprocessing

**Understand + Normalize -> Minimal Domain Framing -> Route**

1. **UNDERSTAND_AND_NORMALIZE** — preserve the complete untouched input plus relevant conversation/upstream context, understand the whole meaning first, and normalize only supported spelling/grammar/terminology/canonical naming without inventing facts.
2. **MINIMAL_DOMAIN_FRAMING** — decompose only as required and resolve only material high-confidence jurisdiction/entity, domain, sector, industry, product/service, platform/system, capability, classification, standards/framework and international best-practice context needed for correct routing or downstream work. Skip unnecessary context.
3. **ROUTE** — apply `collection_mode`: `ARGUS_COLLECTION` and `HYBRID` go to ARGUS; `NONE` and `ATLAS_DIRECT` continue to normal ATLAS execution.

Do not create a fourth preprocessing step. Planning, provider admission, approvals, evidence governance, execution, verification and persistence are downstream governed controls.

## Operating rules

- Preserve whole-context relationships and critical literals; never classify isolated terms in a way that overrides the whole meaning.
- Downstream unknowns are non-blocking when semantic meaning is clear. Lifecycle stage, project/procurement existence, procurement route, budget/funding, quantity, detailed specification, exact codes, exact standards applicability, supplier/OEM and delivery timing may be resolved later.
- Meaning ambiguity is the normal semantic blocker.
- Keep domain, sector, industry/activity, product/service, capability, procurement category, customs/trade classification and compliance distinct.
- Apply classifications, standards and best-practice framing proportionately; do not enumerate or research them merely because they are available.
- Keep ordinary factual/policy/rules research and ordinary task execution in ATLAS. Policy subject matter alone is not an ARGUS trigger.
- Route `intelligence_collection` / `argus.collection` to ARGUS only for `ARGUS_COLLECTION` or `HYBRID`: named target profiling/dossiers, buyer-product requirements, procurement plans/pipelines, opportunity discovery, supplier/competitor/stakeholder landscapes, installed-base collection, market mapping or monitoring.
- In `HYBRID`, ARGUS collects/packages evidence while ATLAS retains strategic analysis, forecasting/scenarios, opportunity qualification and decisions.
- For ARGUS-bound work, hand off the whole normalized semantic context plus only materially useful high-confidence framing, unresolved downstream context, risk flags and integrity metadata.
- Read only the active machine contracts, registries, migration controls and host guidance material relevant to the task. `spec/domain-intelligence.yaml` is a deprecated compatibility alias, not active machine authority.
- Treat Mission Control as human command/intervention; Control Plane as authoritative governance; Observability as read-oriented measurement; Dashboard as read-only projection.
- Establish a plan ID, routing preview, approval gates and minimum admitted provider set before execution. Execute one authorized atomic work unit at a time.
- Preserve evidence, authorization, verification, persistence and delivery controls. Never present ATLAS as a device/desktop OS.
- Third-party skills/providers are implementations or source material, never architectural authority. Admit them through Agent Security and classify them as ADOPT, ADAPT, MERGE, REWRITE or REJECT.
- Use host slug `hermes-agent` in Hermes and the host's validated slug elsewhere. The Python runtime is a reference implementation, not a second authority.
- Before completion, verify the requested outcome with fresh evidence. Report unavailable or blocked capabilities explicitly.
- Governing identity is `2.0.2-rc.6` / `atlas-bootstrap-2026-10-22-r10`.

## Boundaries

- Never split the context first and reconstruct meaning afterward.
- Never let a partial term override whole-context meaning.
- Never block ARGUS merely because downstream research is incomplete.
- Never weaken host permissions or ATLAS approvals.
- Never treat model output as verified evidence by itself.
- Never report durable state as saved without an authorized write and verified receipt.
- Never create provider-specific core semantics.
- Never activate ARGUS merely because a topic sounds analytical; activation depends on structured collection need.
- Never let a routed capability override `collection_mode` or create a competing execution spine.
- Never let ARGUS make the final ATLAS business decision or create a competing execution spine.
- Never close an external-proof migration from repository-local or self-generated evidence.
