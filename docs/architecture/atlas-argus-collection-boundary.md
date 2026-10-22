# ATLAS–ARGUS collection boundary

ATLAS-OS is the operating and governance architecture. ARGUS is a governed intelligence-collection subsystem nested inside it.

## Boundary rule

> **A route may establish that ARGUS is needed. Only explicit user authorization may establish that ARGUS is permitted to run.**

```text
User / Event
  -> ATLAS bootstrap: Mission Control + Control Plane + Dashboard
  -> Understand + Normalize
  -> Minimal Domain Framing
  -> Route
       -> NONE / ATLAS_DIRECT -> ATLAS execution
       -> ARGUS_COLLECTION ----+
       -> HYBRID ---------------+-> ARGUS REQUIRED
                                      |
                                      v
                              EXPLICIT USER APPROVAL
                                      |
                              approved? yes / no
                                 |          |
                                 v          v
                        governed handoff   stop / revise
                                 |
                                 v
                         ARGUS collection mission
                                 |
                                 v
                         Collection package
                                 |
                                 v
                       ATLAS analysis / verification /
                       persistence / final delivery
```

Bootstrap is cross-cutting and the preprocessing flow remains exactly three steps.

## Three independent states

### 1. Collection need

Authoritative field:

```text
collection_mode
```

ARGUS is needed only when the mode is `ARGUS_COLLECTION` or `HYBRID`.

### 2. User authorization

Authoritative portable field:

```text
argus_approval_status = PENDING | APPROVED | REJECTED
```

Authorization is explicit, task-scoped, digest-bound and non-reusable by default.

It must not be inferred from:

- collection mode;
- specialist/provider selection;
- an existing mission object;
- prior task approval;
- prior ARGUS execution;
- silence;
- continued conversation.

### 3. Activation state

The Control Plane may activate ARGUS only when:

- ARGUS is required;
- explicit authorization is `APPROVED`;
- the routing approval/digest is current;
- the provider is admitted;
- prerequisites/permissions pass;
- the collection mission is valid;
- the domain-context handoff is executable;
- no other Control Plane blocker applies.

## Combined approval UX

Hosts should avoid unnecessary double prompts. One explicit user interaction may approve both:

- the exact digest-bound routing preview; and
- ARGUS collection for that exact task/mission.

The adapter then records the two separate machine states against the same digest. A single UI action therefore does not collapse the underlying authorization model.

## Whole-context handoff

The governed ATLAS → ARGUS handoff carries the minimum sufficient context:

1. source task / plan / work-unit identity;
2. original whole context or authoritative source reference;
3. normalized semantic context;
4. whole-context summary and normalization notes;
5. high-confidence domain / sector / industry / product / capability framing;
6. classification context and conditional candidates;
7. standards / best-practice context when material;
8. unresolved downstream facts;
9. risk flags and integrity metadata;
10. bounded collection mission and return expectations.

Handoff readiness remains semantic:

- `READY` — meaning is clear enough for downstream collection;
- `PARTIAL` — usable context with explicit unresolved material;
- `BLOCKED` — meaning is materially ambiguous or another Control Plane prohibition applies.

Classification/framework incompleteness alone does not make a clear handoff `BLOCKED`.

## Activation contract v2

The portable routing result exposes one deterministic integration projection:

```yaml
activation_contract:
  version: "2.0"
  activation_authority: ATLAS_OS
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
  blockers:
    - ARGUS_EXPLICIT_APPROVAL_REQUIRED
```

The activation contract is a projection, not an independent authority.

The proposal digest binds the proposed route, mission, provider order, permissions, data scope, prerequisites and handoff requirements. Authorization state is outside the proposal digest so the act of approving does not change the proposal being approved.

## Separation of responsibilities

### Mission Control

Owns human objective, scope, explicit approval/rejection, ARGUS authorization, pause/resume/abort, priorities, collection expansion/reduction/redirect/stop and permitted exceptions.

### Control Plane

Owns authoritative policy, permissions, task/lifecycle state, collection need, routing, routing approval, ARGUS authorization state, ARGUS activation state, execution leases, provider admission and persistence authorization.

### ARGUS

After authorization, owns bounded collection work only:

- target resolution;
- collection planning within authorized scope;
- source discovery/acquisition;
- extraction/normalization;
- entity/event/relationship resolution;
- deduplication;
- corroboration/reconciliation;
- gap/conflict/coverage assessment;
- collection packaging.

### ATLAS Data/Execution Plane

Retains:

- substantive and strategic analysis;
- forecasting/scenarios;
- comparison;
- opportunity qualification;
- business/pursuit decisions;
- canonical classification acceptance;
- evidence governance;
- verification;
- persistence;
- final delivery.

ARGUS never owns the ATLAS execution spine, approval model, Dashboard, or final business conclusion.

## Representative routing

| Example | Collection mode | Explicit ARGUS approval required? |
| --- | --- | --- |
| Bangladesh Bank foreign exchange policy | ATLAS_DIRECT | No |
| ST Engineering | ARGUS_COLLECTION | Yes |
| Coastal patrol vessel for Bangladesh Coast Guard | ARGUS_COLLECTION | Yes |
| Coastal surveillance radar for Bangladesh Navy | ARGUS_COLLECTION | Yes |
| Seed cum cleaner for BADC | ARGUS_COLLECTION | Yes |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION | Yes |
| Explain Bangladesh Navy procurement regulations | ATLAS_DIRECT | No |
| Forecast likely Bangladesh Navy procurements over 24 months | HYBRID | Yes |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID | Yes |

## Classification boundary

ATLAS uses multi-axial classification. Domain, buyer/end-user sector, supply-side sector, industry/activity, product/service, platform/system, procurement category, customs code, capability, lifecycle and sensitivity remain distinct.

Exact downstream codes can remain unresolved without delaying a semantically clear route or handoff.

## Operating distinction

> **ATLAS asks: What does the complete request mean, how should it be governed, and what is authorized?**

> **ARGUS asks: Within the authorized collection mission, what evidence can we establish?**
