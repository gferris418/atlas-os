# Runtime

The canonical runtime preserves the untouched prompt at the input boundary and then performs `REQUEST_TRIAGE` before deep domain or provider work.

The three first-stage routes are:

- `GENERAL_SEARCH` — direct factual/current-information retrieval or research through ATLAS.
- `GENERAL_TASK` — direct ordinary task execution through ATLAS.
- `INTELLIGENCE` — governed specialist intelligence through ARGUS.

A topic alone does not select `INTELLIGENCE`. Government, public-sector, tender, company, market, person, or political mentions remain on a direct path unless the objective requires intelligence methodology such as opportunity qualification, competitive/stakeholder assessment, strategic or political-economic intelligence, monitoring, forecasting, scenarios, probability estimation, or decision intelligence.

The preferred executable entry point is `execute(ExecutionEnvelope)`. It preserves and normalizes intent, emits the request-triage result, builds the minimum sufficient plan, audits and previews capabilities, applies approval gates, selects one current atomic work unit, measures runtime preparation, and derives the Dashboard through one interface. Existing low-level runtime functions remain available for compatible integrations and focused testing.

## Fast path

`GENERAL_SEARCH` and `GENERAL_TASK` do not automatically pay taxonomy, classification, standards/framework, ontology, or specialist-intelligence cost. Domain controls run only when they can materially change correctness, authorization, safety, or the requested outcome.

Examples:

```text
Find the current Bangladesh Railway tenders.
  -> GENERAL_SEARCH
  -> ATLAS direct research

Rewrite this supplier letter in a formal tone.
  -> GENERAL_TASK
  -> ATLAS direct execution

Find and assess Bangladesh Railway opportunities we should pursue,
rank them by win probability, identify competitors and decision makers,
and monitor material developments.
  -> INTELLIGENCE
  -> governed ARGUS delegation
```

For `INTELLIGENCE`, ATLAS can prepare a governed `PARTIAL` domain-context handoff containing known context, unresolved material, evidence, and correlation identifiers. ARGUS enriches intelligence-domain context after activation. ATLAS retains authority, permissions, planning, routing, approvals, execution state, independent verification, persistence authorization, and final delivery. `BLOCKED` handoffs never authorize dependent ARGUS execution.

## Execution spine

After the lossless input boundary:

1. `REQUEST_TRIAGE`
2. `INTENT_NORMALIZATION`
3. `CONDITIONAL_DOMAIN_CONTEXT`
4. `CAPABILITY_AND_EXECUTION_PLAN`
5. `DATA_PLANE_EXECUTION`
6. `ASSURANCE_AND_VERIFICATION`
7. `PERSISTENCE_AND_DELIVERY`

A concrete plan identifier exists before execution. Material gaps pause only dependent work; safe independent work may continue. Native host understanding, generation, conversation, research, file, visual, and tool capabilities are used directly when available rather than recreated by ATLAS.

## Conditional domain context

Classification systems and requirements remain distinct. Taxonomies classify facets; ontology expresses relationships; law, regulation, contracts, mandatory technical requirements, engineering standards, military standards, procurement rules, and other binding requirements govern the work.

For direct ATLAS requests these controls are conditional. When material, current official applicability and version must be verified. No framework mapping establishes certification, conformity, or legal compliance by itself.

## Planning and execution

Execution depth ranges from L0 direct to L4 high-impact. The runtime uses the lowest depth that preserves correctness and required controls.

Nontrivial work is decomposed into atomic units with one objective and observable completion criteria. One user-visible work unit is active at a time. Safe reads and checks may run concurrently inside a unit when this improves performance without weakening evidence or authorization.

Before routing an external or specialist provider, ATLAS presents the digest-bound routing preview required by the current contract. Approval binds to that exact proposal. Changed providers, permissions, task classes, prerequisites, data scope, or execution sequence invalidate stale approval.

Downstream intent or provider logic cannot silently override a `GENERAL_SEARCH` or `GENERAL_TASK` decision into ARGUS activation. The canonical specialist requirement for ARGUS is `intelligence_analysis`.

## Control Plane, Mission Control, and Dashboard

The **Control Plane** owns machine authority: permissions, policy, routing, approvals, plan/work-unit state, leases, lifecycle transitions, persistence authorization, and control receipts.

**Mission Control** is the human command/intervention surface. Human requests to approve, reject, pause, resume, abort, reprioritize, change scope, or request exceptions are evaluated by the Control Plane before state changes.

The **Dashboard** is the visible read-only observability projection. It is event-driven—startup, route decision, unit completion, blocker, approval, verification, persistence, and delivery—not timer-driven or token-by-token.

Default rendering remains compact:

```text
ATLAS/core [####------] 40% | 2026-10-22T02:00:00+06:00 | 420 ms | Goal update repository | Task 1/3 · EXECUTION: implement current work unit
Input requested repository update | Processing Route GENERAL_TASK; domain context ON_DEMAND; plan validated | Output implementation pending
Playbook test-first change | Framework Not applicable | SOP plan → execute → verify → persist → deliver
Plan plan-change:READY | Profile output.technical-spec | Library READY | Quality PENDING | Blocker None
```

Timestamp and duration are measured, not invented. Processing is a public stage/action summary, never private chain-of-thought.

## Failure and resumption

Failures remain explicit: `BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, and `VALIDATION_FAILED`. A localized failure does not stop independent work, but no failure is relabeled as success.

Resumption restores structured state and reconciles it with actual external state before dependent work continues.

`atlas_runtime.adapters` provides one executable startup/delivery seam for validated AI-host identifiers. ChatGPT, Codex, Work, and Hermes Agent have documented configurations; unlisted tools use the generic AI-host contract. Local adapter conformance does not substitute for independent external-surface evidence required by release-blocking migrations.
