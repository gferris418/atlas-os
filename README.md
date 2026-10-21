# ATLAS-OS

ATLAS-OS is a **model-agnostic execution-governance specification for AI agents**. It sits between user intent and verified delivery, giving different AI hosts one machine-readable contract for routing, planning, permissions, approvals, evidence, verification, persistence, observability, and specialist delegation.

It is **not a desktop operating system** and does not replace the host model, conversation engine, browser, tool runtime, or device OS.

**Current candidate:** `v2.0.2-rc.4`  
**Control revision:** `atlas-bootstrap-2026-10-22-r8`  
**Target stable:** `v2.0.2`  
**Information classification:** Internal  
**License:** [MIT](LICENSE)  
**Release status:** **CANDIDATE / EXTERNAL VERIFICATION PENDING**

Stable `v2.0.2` remains blocked by external-proof controls `MIG-029` and `MIG-037`. Repository-local tests and machine-readiness do not substitute for independent host evidence.

## Machine-readable authority

AI systems begin at [`atlas-ai.yaml`](atlas-ai.yaml), the deterministic discovery entrypoint. [`atlas-os.yaml`](atlas-os.yaml) remains the sole product/release authority. Active machine authority is YAML/JSON and schema-validated; Markdown is human guidance or compatibility material.

Current first-class architecture contracts:

- [`spec/mission-control.yaml`](spec/mission-control.yaml) — human command and intervention.
- [`spec/control-plane.yaml`](spec/control-plane.yaml) — authority, governance, routing, permissions, approvals, and state.
- [`spec/observability.yaml`](spec/observability.yaml) — measurement and read-only operational projection.
- [`spec/domain-intelligence.yaml`](spec/domain-intelligence.yaml) — conditional domain semantics, standards, benchmarks, evidence hierarchy, signals, forecasting, and scenarios.
- [`spec/request-triage.yaml`](spec/request-triage.yaml) — first semantic route decision.
- [`spec/execution-spine.yaml`](spec/execution-spine.yaml) — canonical execution lifecycle after triage.

## Fast request triage

ATLAS makes one lightweight decision before deep domain processing:

```text
USER REQUEST
   |
   v
ATLAS REQUEST TRIAGE
   |
   +--> GENERAL_SEARCH --> ATLAS direct research/search
   |
   +--> GENERAL_TASK ----> ATLAS direct execution
   |
   +--> INTELLIGENCE ----> governed ARGUS delegation
```

### `GENERAL_SEARCH`

Use for ordinary factual/current-information retrieval or research.

```text
Find the current Bangladesh Railway tenders.
```

ATLAS searches directly. ARGUS is not activated merely because the subject is government, public sector, a tender, a company, a market, a person, or politics.

### `GENERAL_TASK`

Use for ordinary production, transformation, calculation, analysis, coding, document, workflow, or external-action preparation.

```text
Rewrite this supplier letter in a formal tone.
```

ATLAS plans only as much as needed and executes through the smallest admitted host capability set.

### `INTELLIGENCE`

Use when the objective requires intelligence methodology: strategic assessment, market intelligence, opportunity qualification, competitor/stakeholder analysis, political-economic assessment, monitoring, forecasting, probability estimation, scenarios, or decision intelligence.

```text
Find and assess Bangladesh Railway opportunities we should pursue,
rank them by win probability, identify competitors and decision makers,
and monitor material developments.
```

ATLAS routes the canonical `intelligence_analysis` capability to ARGUS after governed routing and approval gates.

## ATLAS / ARGUS boundary

ARGUS is the governed specialist for intelligence-grade work. It supports strategic, market, opportunity, competitive, stakeholder, political-economic, monitoring, forecasting, scenario, and decision intelligence. Government/public-sector opportunity intelligence remains an ARGUS specialization rather than its only purpose.

ATLAS retains user and Mission Control authority, permissions and policy, plan/work-unit state, routing and approvals, execution leases and lifecycle state, independent verification, persistence authorization, and final delivery.

For an `INTELLIGENCE` route, ATLAS may send ARGUS a governed `READY` or `PARTIAL` domain-context handoff. ARGUS preserves known upstream context and enriches unresolved intelligence-domain context. A `BLOCKED` handoff cannot authorize dependent ARGUS execution.

The active ARGUS contract is immutably pinned in [`registries/domain-methods.yaml`](registries/domain-methods.yaml).

## Four architectural responsibilities

```text
                         HUMAN
                           |
                           v
                    MISSION CONTROL
               command / approval / intervention
                           |
                           v
                     CONTROL PLANE
        authority / policy / permissions / routing / state
                           |
            +--------------+---------------+
            |                              |
            v                              v
       DATA PLANE                  DOMAIN INTELLIGENCE
     substantive work              conditional context
            |                              |
            +--------------+---------------+
                           |
                           v
                ASSURANCE / VERIFICATION
                           |
                           v
                      OBSERVABILITY
                           |
                           v
                       DASHBOARD
```

### Mission Control

Mission Control is the human supervisory boundary for mission objectives, approvals/rejections, pause/resume/abort, scope changes, priorities, escalation, risk acknowledgement, and permitted exception requests.

Mission Control does not directly mutate machine state. The Control Plane evaluates every state-changing request against permissions, policy, current state, approvals, and non-waivable restrictions.

### Control Plane

The Control Plane is authoritative machine governance. It owns policy evaluation, permissions, plan/work-unit state, routing, provider admission, approval state, execution leases, lifecycle transitions, external-state reconciliation, persistence authorization, and control receipts.

It authorizes substantive execution but is not itself the data plane.

### Dashboard / Observability

The Dashboard is not the Control Plane. It is a derived, read-only observability projection showing route, plan, progress, current work, blockers/approvals, evidence/verification state, performance, and persistence status without exposing private chain-of-thought.

A user action initiated from a Dashboard becomes a Mission Control command and must be admitted by the Control Plane before state changes.

### Conditional Domain Intelligence

ATLAS no longer requires full taxonomy/classification/framework processing before every request.

`GENERAL_SEARCH` and `GENERAL_TASK` resolve taxonomy, classification, ontology, law, standards, frameworks, evidence hierarchy, or benchmarks only when those controls can materially change correctness, authorization, safety, or the requested outcome.

For `INTELLIGENCE`, deep intelligence-domain enrichment is normally deferred until ARGUS activation. This keeps ordinary requests fast without weakening governed specialist analysis.

## Canonical execution spine

After the lossless raw-input boundary:

1. `REQUEST_TRIAGE`
2. `INTENT_NORMALIZATION`
3. `CONDITIONAL_DOMAIN_CONTEXT`
4. `CAPABILITY_AND_EXECUTION_PLAN`
5. `DATA_PLANE_EXECUTION`
6. `ASSURANCE_AND_VERIFICATION`
7. `PERSISTENCE_AND_DELIVERY`

Implementations may use native host capabilities internally when these responsibilities remain satisfied.

## Provider-independent capabilities

ATLAS registers semantic capabilities, not provider brands. Skills, plugins, tools, models, connectors, host functions, subagents, and specialist methods remain replaceable providers governed by [`spec/capability-admission.yaml`](spec/capability-admission.yaml).

Availability is not admission. Installation is not trust. Provider-specific accuracy, latency, cost, or reliability claims require evidence from the target runtime.

Downstream intent/provider logic cannot silently override a `GENERAL_SEARCH` or `GENERAL_TASK` triage decision into ARGUS activation.

## Output contract

Every completed ATLAS output has a canonical schema-valid structured envelope. Markdown, HTML, PDF, CSV, or other user-facing forms are renderings or payload artifacts rather than competing sources of state.

Output profiles are defined in [`registries/output-profiles.yaml`](registries/output-profiles.yaml) and governed by [`spec/output.yaml`](spec/output.yaml).

## Runtime

The executable Python package is a conformance/reference implementation, not a second normative authority.

```bash
python -m pip install --require-hashes -r requirements.lock
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/conformance -v
python -m unittest discover -s tests/regression -v
python -m unittest discover -s tests/integration -v
python tools/validate/validate_repository.py .
python tools/validate/validate_machine_contracts.py .
python tools/validate/validate_output_contracts.py .
```

Run the local executable seam:

```bash
python -m atlas_runtime --input examples/execution-request.json
```

For machine streaming:

```bash
python -m atlas_runtime --format ndjson < examples/execution-request.json
```

See [`docs/runtime.md`](docs/runtime.md) and [`docs/live-testing.md`](docs/live-testing.md).

## AI-host integrations

Documented surfaces include:

- ChatGPT — [`integrations/chatgpt/`](integrations/chatgpt/)
- ChatGPT Work — [`integrations/work/`](integrations/work/)
- Codex — [`integrations/codex/`](integrations/codex/)
- Hermes Agent — [`integrations/hermes-agent/`](integrations/hermes-agent/)
- Generic AI hosts — [`integrations/generic-ai-host/`](integrations/generic-ai-host/)

External conformance is governed by machine-readable `integrations/<surface>/release-verification.yaml` contracts.

## Persistence

Task execution state and durable canonical-library state remain separate namespaces. A `SAVED` claim requires an authorized write and verified receipt. If durable storage is unavailable, ATLAS reports `CAPABILITY_UNAVAILABLE`; if authorization or policy blocks it, ATLAS reports `BLOCKED`.

## Repository map

- `atlas-ai.yaml` — machine discovery entrypoint.
- `atlas-os.yaml` — sole product/release authority.
- `.agents/skills/atlas-os/` — project-local AI-host skill entrypoint.
- `atlas_runtime/` — optional reference runtime and adapter seam.
- `spec/` — normative machine specifications.
- `schemas/` — JSON Schemas for governed state.
- `registries/` — capabilities, providers, surfaces, outputs, taxonomies, frameworks, and controls.
- `migration/` — schema-validated migration/release-control evidence.
- `integrations/` — host adapters and external verification contracts.
- `tests/` — unit, conformance, regression, and integration evidence.
- `tools/validate/` — repository/machine/output validation.
- `tools/package/` — deterministic candidate/release packaging.
- `library/` — durable reusable outputs and storage guidance.

## Release state

The last stable release remains `v2.0.1`.

`v2.0.2-rc.4` is a candidate. It introduces the triage-first fast path, four-responsibility architecture, conditional Domain Intelligence, generalized ARGUS intelligence routing, and provider-neutral control revision `atlas-bootstrap-2026-10-22-r8`.

Candidate verification items:

- `MIG-029` — independent New Chat and ChatGPT Work bootstrap proof for rc.4/r8 remains pending.
- `MIG-037` — repository publication is proven for rc.4/r8, but independent propagation across ChatGPT, Codex, Work, and Hermes Agent remains blocked on `MIG-029`.
- `DTIF-RECONCILIATION` — closed and archive-only; retained historical evidence is not current ARGUS truth.

Stable `v2.0.2` must not be promoted until genuine independent evidence satisfies the current external-proof criteria.

See [`GOVERNANCE.md`](GOVERNANCE.md), [`docs/architecture.md`](docs/architecture.md), and [`docs/release-process.md`](docs/release-process.md).
