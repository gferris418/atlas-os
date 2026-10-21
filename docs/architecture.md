# Architecture

ATLAS-OS is a normative AI-agent execution-governance layer. It is not a desktop or device operating system. The architecture separates human command, machine authority, specialist intelligence, substantive execution, assurance, and observability so no surface can silently become the source of truth for another.

```text
USER
  |
  v
MISSION CONTROL
human command / approval / intervention
  |
  v
REQUEST TRIAGE
GENERAL_SEARCH | GENERAL_TASK | INTELLIGENCE
  |
  +----------------------+----------------------+
  |                                             |
  v                                             v
ATLAS DIRECT PATH                           ARGUS INTELLIGENCE
search / task execution                    specialist intelligence
  |                                             |
  +----------------------+----------------------+
                         |
                         v
                   CONTROL PLANE
           authority / policy / permissions
           plan / routing / approvals / state
                         |
              +----------+----------+
              |                     |
              v                     v
      DATA-PLANE EXECUTION   ASSURANCE / VERIFICATION
              |                     |
              +----------+----------+
                         |
                         v
                 OBSERVABILITY EVENTS
                         |
                         v
                      DASHBOARD
              progress / metrics / risks
```

The core architectural authorities are machine-readable:

- `spec/mission-control.yaml` — human command and intervention boundary.
- `spec/control-plane.yaml` — authoritative machine governance, routing, permissions, approvals, and state.
- `spec/observability.yaml` — measurement and read-only state projection.
- `spec/domain-intelligence.yaml` — conditional domain semantics, evidence hierarchy, standards, benchmarks, signals, forecasting, scenarios, and calibration.
- `spec/request-triage.yaml` — first semantic routing gate.

## Request triage and fast paths

ATLAS performs the smallest useful decision first:

- `GENERAL_SEARCH` — direct factual/current-information retrieval or research in ATLAS.
- `GENERAL_TASK` — direct production, transformation, calculation, analysis, coding, document, workflow, or other ordinary task execution in ATLAS.
- `INTELLIGENCE` — governed delegation to ARGUS when the objective requires strategic, market, opportunity, competitive, stakeholder, political-economic, monitoring, forecasting, scenario, probability, or decision intelligence.

A government agency, tender, company, market, person, or political topic does not by itself activate ARGUS. A plain tender lookup remains `GENERAL_SEARCH`; qualifying, ranking, forecasting, monitoring, or deciding which opportunities to pursue is `INTELLIGENCE`.

This gate occurs before deep taxonomy, classification, framework, or provider work. Direct requests resolve those controls only when they can materially change correctness, authorization, safety, or the requested outcome.

## Mission Control

Mission Control is the human supervisory command surface. It expresses mission objectives, approvals, rejection, pause/resume/abort requests, scope changes, priorities, escalation, and exception requests.

Mission Control does not mutate execution state directly. Every state-changing request is evaluated by the Control Plane against permissions, policy, current state, approvals, and non-waivable constraints.

## Control Plane

The Control Plane is the authoritative machine-governance and orchestration layer. It owns policy evaluation, permissions, plan/work-unit state, routing, approval state, execution leases, lifecycle transitions, external-state reconciliation, persistence authorization, and control receipts.

The Control Plane authorizes substantive work but does not become the substantive data plane. It is also distinct from the Dashboard: displayed state is a projection, not authority.

## Dashboard and observability

The Dashboard is a read-oriented projection over event-driven observability state. It reports progress, active work, blockers, approvals, evidence health, verification state, performance, reliability, and persistence status.

A user action initiated from a dashboard is converted into a Mission Control command and evaluated by the Control Plane. Dashboard state never silently mutates a plan, permission, routing decision, or approval.

## Conditional Domain Intelligence

Domain Intelligence is not universal preflight. For direct ATLAS work it resolves only the domain context that can materially affect the result.

For `INTELLIGENCE`, ATLAS may transfer a governed `READY` or `PARTIAL` domain-context handoff to ARGUS. ARGUS preserves known upstream context and enriches unresolved intelligence-domain context. A `BLOCKED` handoff cannot authorize dependent execution.

The layer distinguishes:

- taxonomy — controlled categories;
- classification — contextual assignment into those categories;
- ontology — material relationships among entities and concepts;
- binding requirements — law, regulation, contract, mandatory technical requirements;
- standards and recognized professional frameworks;
- best practices and authoritative guidance;
- benchmarks and comparison baselines;
- domain-sensitive evidence hierarchies;
- signals, trends, forecasting, scenarios, and calibration where the intelligence objective requires them.

## ARGUS specialist boundary

ARGUS is the governed specialist for `intelligence_analysis`. It supports strategic, market, opportunity, competitive, stakeholder, political-economic, monitoring, forecasting, scenario, and decision intelligence. Government/public-sector opportunity intelligence remains an ARGUS specialization rather than its only purpose.

ARGUS never owns the ATLAS execution spine, user authority, permissions, plan, approval state, provider routing authority, independent verification decision, persistence authorization, or final delivery. ATLAS pins ARGUS through an immutable activation contract in `registries/domain-methods.yaml`.

## Provider-independent capabilities

ATLAS registers semantic capabilities rather than embedding provider brands into core semantics. Skills, plugins, models, connectors, specialist methods, and host functions remain providers of capabilities and are subordinate to `spec/capability-admission.yaml`.

Availability is not admission. Installation is not trust. A static security scan is not certification. Provider-specific accuracy, cost, latency, and reliability claims remain unverified until measured in the target runtime.

The executable `atlas_runtime` package is a conformance reference, not a second source of truth. Declarative specifications remain authoritative. Surface adapters may use native host capabilities but cannot redefine core semantics.
