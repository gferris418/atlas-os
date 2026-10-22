---
name: atlas-os
description: Apply the ATLAS-OS execution-governance contract to AI-agent work using the current host's native capabilities.
version: 2.0.2-rc.7
metadata:
  atlas:
    control_revision: atlas-bootstrap-2026-10-22-r11
    ai_entrypoint: atlas-ai.yaml
  hermes:
    tags: [governance, planning, capability-routing, collection, evidence, verification]
    category: agent-governance
---

# ATLAS-OS

Use this skill when the user asks to run, install, apply, or govern work with ATLAS-OS, or when a task explicitly requires the ATLAS execution spine.

1. Locate the repository root, read `atlas-ai.yaml`, then `atlas-os.yaml` as product/release authority.
2. Preserve untouched input and interpret task intent plus target objects.
3. Apply the Collection-Need Gate independently of task intent: `NONE`, `ATLAS_DIRECT`, `ARGUS_COLLECTION`, `HYBRID`.
4. Select the canonical capability plan after collection need is known. Always keep the four kernel services active: Evidence Governance, Execution Governance, Agent Security, and Classification Crosswalk.
5. Use routed ATLAS capabilities proportionately: Deep Research, Procurement Intelligence, Commercial Contract Review, Corporate Finance, and Economic Policy Intelligence. Capabilities do not self-activate ARGUS.
6. Keep ordinary factual/policy/rules research and ordinary task execution in ATLAS. Policy subject matter alone is not an ARGUS trigger.
7. Route `intelligence_collection` / `argus.collection` to ARGUS only for `ARGUS_COLLECTION` or `HYBRID`. ARGUS v3 government commercial opportunity intelligence includes named targets; need/capability-gap discovery; programme/project/funding/approval intelligence; buyer-product requirements; pre-procurement opportunity development; supplier/OEM landscapes and partnerability; demand-supply matching; procurement plans/pipelines; Rapid Tender recovery; installed-base expansion; competitor/stakeholder landscapes; and monitoring.
8. Keep early opportunity intelligence distinct from procurement intelligence. Need/gap discovery, solution shaping, supply-first matching and early opportunity development do not automatically activate `atlas.procurement-intelligence`; procurement plans, tenders, acquisitions, eligibility/evaluation, bid/no-bid and `RAPID_TENDER` do.
9. In `HYBRID`, ARGUS may derive bounded PIR/EEI, collect/package evidence, maintain pre-PX opportunity identity/lifecycle, build supplier universes, assess partnerability and compute advisory supplier-match/opportunity-qualification outputs. ATLAS Evidence Governance owns canonical claim status and ATLAS retains authoritative opportunity priority, `PROMOTE_TO_PX`, pursuit/bid decisions, strategic analysis, forecasting/scenarios, approvals and final delivery.
10. Resolve material Domain Context Services through ATLAS: terminology, taxonomy, economic sector, industry/activity, product/service, procurement, customs/trade, capability, ontology, laws, international standards, professional frameworks and benchmarks. ARGUS may suggest mappings but cannot silently replace ATLAS canonical classification.
11. Read only the active machine contracts, registries, migration controls and host guidance material relevant to the task. `spec/domain-intelligence.yaml` is a deprecated compatibility alias, not active machine authority.
12. Treat Mission Control as human command/intervention; Control Plane as authoritative governance; Observability as read-oriented measurement; Dashboard as read-only projection. Dashboard state changes become Mission Control commands.
13. Establish a plan ID, routing preview, approval gates and minimum admitted provider set before execution. Execute one authorized atomic work unit at a time.
14. Preserve evidence, authorization, verification, persistence and delivery controls. Never present ATLAS as a device/desktop OS.
15. Third-party skills/providers are implementations or source material, never architectural authority. Admit them through Agent Security and classify them as ADOPT, ADAPT, MERGE, REWRITE or REJECT.
16. For legitimate opportunity development, support only lawful market education, demonstrations, concept notes, transparent pre-procurement engagement, industry consultation and solution discovery. Never support bribery, collusion, improper procurement influence, unlawful specification manipulation, confidential bid-information acquisition or evaluation interference.
17. Use host slug `hermes-agent` in Hermes and the host's validated slug elsewhere. The Python runtime is a reference implementation, not a second authority.
18. Before completion, verify the requested outcome with fresh evidence. Report unavailable or blocked capabilities explicitly.
19. Governing identity is `2.0.2-rc.7` / `atlas-bootstrap-2026-10-22-r11`.

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
