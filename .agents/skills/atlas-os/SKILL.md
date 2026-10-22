---
name: atlas-os
description: Apply the portable ATLAS-OS operating and governance contract inside the current AI host while preserving explicit ARGUS authorization.
version: 2.1.0-rc.1
metadata:
  atlas:
    control_revision: atlas-portable-orchestration-2026-10-22-r1
    ai_entrypoint: atlas-ai.yaml
  hermes:
    tags: [governance, mission-control, planning, capability-routing, collection, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply or govern work with ATLAS-OS, or when a task explicitly requires the ATLAS execution spine.

## Bootstrap first

For every substantive ATLAS task, establish or bind:

- task and plan identity;
- Mission Control;
- Control Plane state;
- Observability;
- compact Dashboard state.

Bootstrap is cross-cutting governance and is **not** a preprocessing step.

## Canonical preprocessing

Exactly:

**Understand + Normalize -> Minimal Domain Framing -> Route**

1. **UNDERSTAND_AND_NORMALIZE** — preserve the complete untouched input plus relevant conversation/upstream context; understand the whole meaning first; normalize only supported spelling/grammar/terminology/canonical naming without inventing facts.
2. **MINIMAL_DOMAIN_FRAMING** — decompose only as required and resolve only material high-confidence jurisdiction/entity, domain, sector, industry, product/service, platform/system, capability, classification, standards/framework and international best-practice context needed for correct routing or downstream work.
3. **ROUTE** — choose `NONE`, `ATLAS_DIRECT`, `ARGUS_COLLECTION`, or `HYBRID`.

Do not create a fourth preprocessing step.

## ARGUS authorization rule

`collection_mode` establishes whether ARGUS is **needed**. It never establishes user consent.

If Route selects `ARGUS_COLLECTION` or `HYBRID`:

1. prepare the bounded routing preview / collection mission;
2. stop before ARGUS handoff or activation;
3. surface `AWAITING_APPROVAL` / `ARGUS_APPROVAL` when no earlier blocker applies;
4. ask the user explicitly whether to authorize ARGUS for the current task/scope;
5. proceed only after explicit approval is bound to the current task and routing-preview digest.

No implicit authorization. Never infer approval from prior ARGUS use, previous tasks, silence, continued conversation, specialist availability or the collection mode itself.

A host may use one explicit user action to approve both the exact routing preview and ARGUS mission, but it must keep `routing_approval_status` and `argus_approval_status` separate in machine state.

## Operating rules

- Preserve original input separately from normalized intent.
- Preserve whole-context relationships and critical literals; never let isolated classification override whole meaning.
- Downstream unknowns are non-blocking when semantic meaning is clear. Lifecycle, project/procurement existence, route, budget/funding, quantity, specification, exact codes, exact standards applicability, supplier/OEM and timing may be resolved later.
- Meaning ambiguity is the normal semantic blocker.
- Keep domain, sector, industry/activity, product/service, capability, procurement category, customs/trade classification and compliance distinct.
- Apply classifications, standards and best-practice framing proportionately; do not research them merely because they are available.
- Keep ordinary factual/policy/rules research and ordinary task execution in ATLAS. Policy subject matter alone is not an ARGUS trigger.
- Route `intelligence_collection` / `argus.collection` only when collection mode is `ARGUS_COLLECTION` or `HYBRID`, and never activate it before explicit approval.
- In `HYBRID`, ARGUS collects/packages evidence after authorization while ATLAS retains strategic analysis, forecasting/scenarios, opportunity qualification and decisions.
- For authorized ARGUS work, hand off the whole normalized semantic context plus materially useful high-confidence framing, explicit unresolved downstream context, risk/integrity metadata and the bounded mission.
- Mission Control is human command/intervention. Control Plane is authoritative governance. Observability is read-oriented measurement. Dashboard is read-only projection.
- Establish routing preview, relevant approvals and the minimum admitted provider set before provider invocation. Execute one authorized atomic work unit at a time.
- Treat concrete tools/plugins/MCPs/connectors/models/subagents as replaceable providers of semantic capabilities, never architectural authority.
- Use the current host's native capabilities where appropriate while preserving ATLAS semantics.
- Before completion, verify the requested outcome with fresh evidence. Report unavailable or blocked capabilities explicitly.
- Governing identity is `2.1.0-rc.1` / `atlas-portable-orchestration-2026-10-22-r1`.

## Portable lifecycle

Project host-facing task state as:

`CREATED -> NORMALIZING -> FRAMING -> ROUTING -> AWAITING_APPROVAL -> COLLECTING / ANALYZING -> VERIFYING -> PERSISTING -> COMPLETED`

Also support `PAUSED`, `BLOCKED`, and `ABORTED`.

## Boundaries

- Never split context first and reconstruct meaning afterward.
- Never overwrite original input with normalized text.
- Never block ARGUS merely because downstream research is incomplete.
- Never weaken host permissions or ATLAS approvals.
- Never treat model output as verified evidence by itself.
- Never report durable state as saved without an authorized write and verified receipt.
- Never create provider-specific core semantics.
- Never treat `collection_mode` as ARGUS authorization.
- Never activate or hand off to ARGUS without explicit task-scoped user approval.
- Never let a routed capability override `collection_mode` or create a competing execution spine.
- Never let ARGUS make the final ATLAS business decision or own ATLAS governance.
- Never close an external-proof migration from repository-local or self-generated evidence.
