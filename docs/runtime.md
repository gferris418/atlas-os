# Runtime

The portable ATLAS runtime initializes governance first, preserves the untouched user input, executes exactly three preprocessing steps, and then continues through governed execution.

## Runtime entry

Compatible hosts should enter through the package-level portable orchestration seam:

```python
from atlas_runtime import ExecutionEnvelope, execute
```

The lower-level engine/routing modules remain implementation and compatibility seams.

For every substantive task the host initializes or supplies task/plan identity and ATLAS establishes Mission Control, Control Plane state, Observability and the compact Dashboard before substantive execution.

## Three preprocessing steps

Exactly:

1. `UNDERSTAND_AND_NORMALIZE`
2. `MINIMAL_DOMAIN_FRAMING`
3. `ROUTE`

Bootstrap, approval evaluation, provider admission and execution governance do not become additional preprocessing steps.

## Collection modes

- `NONE` — no external collection required.
- `ATLAS_DIRECT` — ordinary retrieval/research stays in ATLAS.
- `ARGUS_COLLECTION` — ARGUS collection is required, subject to explicit user authorization.
- `HYBRID` — ARGUS collection is required, subject to explicit user authorization, while ATLAS retains substantive analysis/decision work.

The legacy `request_route` field remains a compatibility projection. `collection_mode` is authoritative for **ARGUS need**, not activation permission.

## Explicit ARGUS authorization

The public execution envelope exposes:

```text
routing_approval_status = PENDING | APPROVED | REJECTED
argus_approval_status   = PENDING | APPROVED | REJECTED
routing_preview_digest  = <current digest or null>
```

For `ARGUS_COLLECTION` or `HYBRID`:

- `PENDING` ARGUS authorization stops execution at `AWAITING_APPROVAL` / `ARGUS_APPROVAL` when the route is otherwise ready;
- `REJECTED` fails closed and produces no ARGUS routing decision;
- `APPROVED` permits the Control Plane to continue only if routing approval, digest, provider, mission, handoff and other gates also pass.

One explicit user action may set both routing and ARGUS approval to `APPROVED` for the same current digest. The machine states remain separate.

## Activation contract v2

The portable routing result exposes `activation_contract.version = "2.0"`.

It retains provider/blocker compatibility fields and adds:

```yaml
route:
  collection_mode: ARGUS_COLLECTION
  routing_preview_digest: sha256:...

argus:
  required: true
  authorization:
    required: true
    status: PENDING
    scope_task_id: TASK-...
    bound_preview_digest: sha256:...
    reusable: false
    decision_source: null
  activation:
    status: NOT_AUTHORIZED
  mission:
    id: COLLECTION-...
```

Authorization state is deliberately projected outside the proposal digest. The digest binds the route, mission, providers, permissions, prerequisites, data scope and handoff proposal; approving it does not mutate the object being approved.

## Provider routing

Before provider invocation ATLAS presents the digest-bound routing preview. Changed providers, permissions, task classes, prerequisites, data scope, mission or execution sequence invalidate stale routing approval.

ARGUS has an additional non-waivable human gate. `collection_mode`, specialist availability and collection-mission existence do not constitute authorization.

ARGUS canonical specialist requirement is `intelligence_collection`. After authorization, a governed `READY` or executable `PARTIAL` domain-context handoff plus collection mission may proceed under the pinned provider contract. `BLOCKED` never authorizes dependent collection.

## Host adapters

Host adapters pass available provider inventory and ATLAS control state through the same execution envelope. They may map semantic capabilities to native tools, plugins, connectors, MCP servers, APIs or subagents.

Hosts may differ in rendering, but must not infer consent or redefine ATLAS routing/evidence semantics.

## Lifecycle

Canonical host-facing lifecycle states:

```text
CREATED
NORMALIZING
FRAMING
ROUTING
AWAITING_APPROVAL
COLLECTING
ANALYZING
VERIFYING
PERSISTING
COMPLETED
PAUSED
BLOCKED
ABORTED
```

`AWAITING_APPROVAL` means dependent work is otherwise ready but requires a human authorization decision.

Lower-level implementation states may exist for compatibility, but portable adapters should project the canonical lifecycle.

## Dashboard

Dashboard is read-only and event-driven. At startup and meaningful state changes it should expose:

- objective and task/plan identity;
- progress;
- active stage/unit;
- blocker or approval;
- evidence health;
- persistence/library state;
- next action;
- collection/ARGUS state when material.

A Dashboard request to approve/reject ARGUS, expand/redirect/stop collection, change a provider, persist, publish or execute becomes a Mission Control command evaluated by the Control Plane.

## ARGUS return path

ARGUS returns a bounded evidence/collection package to ATLAS. ATLAS retains canonical Evidence Governance, classification acceptance, substantive analysis, strategic analysis, forecasting, scenario work, opportunity qualification, business decisions, assurance, persistence and final delivery.

## Domain context

Use only material context. Keep sector, industry/activity, product/service, procurement category, customs code and capability distinct. Verify official scheme editions when currency matters. Never infer certification, compliance, procurement eligibility or legal status merely from classification.

## Failure and resumption

Failures remain explicit (`BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, `VALIDATION_FAILED`).

Resumption restores structured state, reconciles it with actual external state and revalidates stale approvals, routing digests, permissions and execution leases before dependent work continues.
