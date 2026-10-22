# ATLAS-OS

ATLAS-OS is a **portable, model-agnostic operating and governance layer for AI systems**. It sits between user intent and verified delivery and is designed to run inside ChatGPT, Hermes Agent, Claude, Codex, or another compatible AI host without transferring ATLAS authority to that host.

ATLAS does not replace the host model, conversation engine, browser, tool runtime, MCP layer, or device operating system. The host supplies capabilities; ATLAS supplies the operating model, governance, routing, approvals, evidence controls, lifecycle, verification, persistence policy, and delivery semantics.

ARGUS is nested inside ATLAS as the governed intelligence-collection subsystem. It is not a peer operating system and cannot self-activate.

**Current candidate:** `v2.1.0-rc.1`  
**Control revision:** `atlas-portable-orchestration-2026-10-22-r1`  
**Target stable:** `v2.1.0`  
**Information classification:** Internal  
**License:** [MIT](LICENSE)  
**Release status:** **CANDIDATE / EXTERNAL VERIFICATION PENDING**

## Core invariant

> **ATLAS governs. ARGUS collects. Tools execute. The host supplies capabilities. The user retains authority over consequential actions.**

## Portable runtime architecture

```text
USER / EVENT / FILE
        |
        v
+---------------- EXPERIENCE PLANE ----------------+
| Mission Control                                  |
| Compact Dashboard / progress / approvals        |
+--------------------------------------------------+
        |
        v
+----------------- CONTROL PLANE ------------------+
| Task identity / lifecycle                        |
| Policy / permissions / approvals                 |
| Routing / provider admission / leases            |
| ARGUS need / authorization / activation state    |
| Evidence / persistence authority                 |
+--------------------------------------------------+
        |
        v
      Understand + Normalize
        |
      Minimal Domain Framing
        |
      Route
        |
        +--> NONE / ATLAS_DIRECT --> ATLAS execution
        |
        +--> ARGUS_COLLECTION -----> explicit approval gate
        |                               |
        |                               +--> ARGUS bounded collection
        |
        +--> HYBRID ----------------> explicit approval gate
                                        |
                                        +--> ARGUS collection + ATLAS analysis
        |
        v
+---------------- EXECUTION PLANE -----------------+
| ATLAS capabilities / ARGUS / admitted providers |
| Evidence acquisition / analysis / actions       |
+--------------------------------------------------+
        |
        v
 Assurance / Verification -> Output / Persistence
        |
        v
+----------------- ADAPTER PLANE ------------------+
| ChatGPT / Hermes / Claude / Codex / MCP / APIs  |
+--------------------------------------------------+
```

Mission Control, the Control Plane, Observability, and the Dashboard are cross-cutting. They initialize before substantive execution but **do not add preprocessing steps**.

## Canonical pre-execution flow

ATLAS preprocessing is exactly:

1. **Understand + Normalize** — read the available context as one semantic unit, preserve the original input and critical literals, and normalize only without semantic drift.
2. **Minimal Domain Framing** — add only material high-confidence jurisdiction/entity, domain, sector, industry, product/service, capability, classification, standards, and best-practice context needed for correct routing or downstream work.
3. **Route** — select `NONE`, `ATLAS_DIRECT`, `ARGUS_COLLECTION`, or `HYBRID`.

ATLAS does not create a pre-routing research loop merely to resolve lifecycle stage, procurement route, budget, quantity, technical specification, exact classification codes, exact standards applicability, funding, supplier/OEM, or delivery timing.

**Unknown downstream facts are not semantic blockers.** Material ambiguity in meaning, or another explicit Control Plane prohibition, is the normal reason to block routing.

## Bootstrap and startup dashboard

For every substantive task, the host enters the portable ATLAS orchestration seam and initializes:

- task and plan identity;
- Mission Control;
- Control Plane state;
- Observability;
- a compact Dashboard.

The Dashboard should expose, at minimum:

```text
ATLAS Mission Control
Task: <task-id>
Objective: <normalized objective>
Stage: <current stage>
Progress: <measured progress>
Blocker / Approval: <state>
Evidence: <health>
Library: <persistence state>
Next: <next action>
```

Each host may render this differently. The state semantics must remain the same.

## Mission Control

Mission Control is the human supervisory surface for:

- objective and scope;
- approve / reject;
- explicit ARGUS authorization;
- pause / resume / abort;
- priority and scope changes;
- collection expansion, reduction, redirect, or stop;
- permitted exceptions and risk acknowledgement.

Presentation surfaces never mutate execution directly. A Dashboard action becomes a Mission Control command, which the Control Plane validates.

## Control Plane

The Control Plane is the machine authority for:

- task identity and lifecycle state;
- policy and permissions;
- collection-need decisions;
- routing and provider admission;
- routing approval;
- ARGUS authorization and activation state;
- plans and work units;
- execution leases and dependencies;
- external-state reconciliation;
- persistence authorization;
- audit/control receipts.

The Control Plane remains active for the task until completion, pause, abort, or supersession.

## ARGUS need is not ARGUS consent

`collection_mode` answers:

> **Does this task require ARGUS?**

It does **not** answer:

> **Has the user authorized ARGUS to run?**

The states are separate.

```yaml
collection_mode: ARGUS_COLLECTION
argus:
  required: true
  authorization:
    required: true
    status: PENDING
  activation:
    status: NOT_AUTHORIZED
```

Before ARGUS handoff or activation, ATLAS must obtain explicit user permission for the current task and routing preview.

After approval:

```yaml
argus:
  required: true
  authorization:
    required: true
    status: APPROVED
    reusable: false
  activation:
    status: AUTHORIZED
```

No implicit approval is permitted. Approval cannot be inferred from:

- `collection_mode`;
- specialist selection;
- an existing collection mission;
- prior ARGUS use;
- prior task approval;
- silence;
- continued conversation.

A host may use **one explicit user interaction** to approve both the exact routing preview and the ARGUS mission, but ATLAS records `routing_approval_status` and `argus_approval_status` as separate machine states bound to the same task/digest.

## Activation contract v2

Host integrations consume a deterministic activation projection that separates route, authorization, and activation readiness.

```yaml
activation_contract:
  version: "2.0"
  activation_authority: ATLAS_OS
  collection_mode: ARGUS_COLLECTION
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
    activation:
      status: NOT_AUTHORIZED
    mission:
      id: COLLECTION-...
  blockers:
    - ARGUS_EXPLICIT_APPROVAL_REQUIRED
```

The proposal digest binds the proposed route, mission, providers, permissions, and handoff requirements. Approval state remains separate so authorizing a proposal does not mutate the proposal being authorized.

## Canonical task lifecycle

Portable host-facing states are:

`CREATED -> NORMALIZING -> FRAMING -> ROUTING -> AWAITING_APPROVAL -> COLLECTING / ANALYZING -> VERIFYING -> PERSISTING -> COMPLETED`

Control states may also be `PAUSED`, `BLOCKED`, or `ABORTED`.

`AWAITING_APPROVAL` is used when dependent work is otherwise ready but explicit human authorization is required, including ARGUS authorization.

## Host adapter plane

ATLAS should request **semantic capabilities**, not unnecessarily hard-code products.

Examples:

```text
WEB_SEARCH
FILE_READ
FILE_WRITE
CODE_EXECUTION
DATABASE_QUERY
EXTERNAL_ACTION
PERSISTENCE
SPECIALIST_METHOD
```

A host adapter resolves these to available implementations such as native tools, plugins, MCP servers, connectors, subagents, or external APIs. Those implementations remain subject to ATLAS Agent Security, permissions, provenance, scope, routing, and verification controls.

ChatGPT, Hermes Agent, Claude, Codex, and other hosts may differ in UI and tool inventory. They must not redefine ATLAS approval, routing, evidence, lifecycle, or persistence semantics.

## Canonical capability layer

ATLAS exposes ten canonical capabilities. They are capabilities, not ten independent agents.

| Capability | Class | Owner |
| --- | --- | --- |
| `atlas.deep-research` | ROUTED | ATLAS |
| `atlas.evidence-governance` | KERNEL | ATLAS |
| `argus.collection` | SPECIALIST | ARGUS under ATLAS |
| `atlas.procurement-intelligence` | HYBRID | ATLAS |
| `atlas.execution-governance` | KERNEL | ATLAS |
| `atlas.agent-security` | KERNEL | ATLAS |
| `atlas.commercial-contract-review` | ROUTED | ATLAS |
| `atlas.corporate-finance` | ROUTED | ATLAS |
| `atlas.economic-policy-intelligence` | ROUTED | ATLAS |
| `atlas.classification-crosswalk` | KERNEL | ATLAS |

The four kernel services are always active. Routed capabilities are selected proportionately after task intent and collection mode are known. A capability may declare a collection dependency but cannot self-activate ARGUS.

Third-party skills, plugins, MCP servers, connectors, models, and subagents are implementations or source material. Agent Security admits them as `ADOPT`, `ADAPT`, `MERGE`, `REWRITE`, or `REJECT`; they never become ATLAS architectural authority.

## Evidence Governance

Research discovers evidence; Evidence Governance determines what that evidence can legitimately support.

Canonical statuses are:

- `CONFIRMED`
- `PROBABLE`
- `POSSIBLE`
- `DISPUTED`
- `UNVERIFIED`
- `STALE`

Source is distinct from claim. Observation is distinct from analyst inference. Multiple sources are not automatically independent corroboration. A source link is provenance rather than proof.

## Execution Governance and Agent Security

Execution Governance owns authority, approval scope, side-effect classification, idempotency, retry/compensation, failure/resume state, escalation, kill-switch behavior, and audit receipts.

Agent Security applies install/activate/execute/verify gates to external capabilities and treats retrieved content, provider instructions, and tool outputs as untrusted until assessed.

## Domain Context Services

ATLAS owns canonical whole-context semantics, terminology, taxonomy, buyer/end-user sector, supply-side sector, operator/supplier industry, product/service, platform/system, operating environment, capability, procurement, trade/customs and defense-logistics classification, plus ontology, law, standards, professional frameworks, benchmarks, and evidence precedence.

Classification is proportional and high-confidence-first. Exact codes and exact framework applicability can remain unresolved without blocking a semantically clear route.

`spec/domain-intelligence.yaml` remains a deprecated compatibility alias and is not an active machine authority.

## ARGUS intelligence collection

ARGUS is considered **needed** only when `collection_mode` is `ARGUS_COLLECTION` or `HYBRID`, and is considered **authorized** only after explicit user approval.

After authorization, ATLAS passes the minimum sufficient governed handoff:

- whole normalized semantic context;
- material high-confidence classification / standards / best-practice framing;
- explicit downstream unknowns;
- collection mission and risk/integrity metadata.

A handoff may be `READY` even when lifecycle, procurement, budget, quantity, specification, exact codes, standards applicability, or supplier/OEM remain unresolved. `BLOCKED` is reserved for material meaning ambiguity or another explicit Control Plane prohibition.

Within an authorized mission ARGUS uses the bounded method:

`PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`

ARGUS may resolve targets, discover/acquire sources, extract/normalize evidence, resolve entities/events/relationships, deduplicate, propose classifications/evidence grades, corroborate, and expose conflicts/gaps/coverage.

ATLAS retains canonical Evidence Governance, classification acceptance, substantive analysis, strategic analysis, forecasting, opportunity qualification, final business decisions, assurance, persistence, and delivery.

## Collection-Need Gate examples

| Request | Collection mode | ARGUS approval? | Execution |
| --- | --- | --- | --- |
| Bangladesh Bank foreign exchange policy | ATLAS_DIRECT | No | ATLAS |
| ST Engineering | ARGUS_COLLECTION | Yes | ARGUS after approval |
| Coastal patrol vessel for Bangladesh Coast Guard | ARGUS_COLLECTION | Yes | ARGUS after approval |
| Coastal surveillance radar for Bangladesh Navy | ARGUS_COLLECTION | Yes | ARGUS after approval |
| Seed cum cleaner for BADC | ARGUS_COLLECTION | Yes | ARGUS after approval |
| Annual procurement plan of Bangladesh Navy | ARGUS_COLLECTION | Yes | ARGUS after approval |
| Explain Bangladesh Navy procurement regulations | ATLAS_DIRECT | No | ATLAS |
| Forecast likely Navy procurements over 24 months | HYBRID | Yes | ARGUS + ATLAS after approval |
| Compare ST Engineering vs L3Harris for Bangladesh opportunities | HYBRID | Yes | ARGUS + ATLAS after approval |
| Review attached commercial agreement and propose redlines | NONE | No | ATLAS |
| Calculate commission margin and FX exposure from supplied figures | NONE | No | ATLAS |

`GENERAL_SEARCH`, `GENERAL_TASK`, and `INTELLIGENCE` remain compatibility route labels. `collection_mode` defines ARGUS need; explicit authorization defines ARGUS permission.

## Economic taxonomy and classification crosswalk

ATLAS uses a multi-axial model and never collapses unlike concepts:

`DOMAIN != SECTOR != INDUSTRY != ECONOMIC ACTIVITY != PRODUCT != CAPABILITY != PROCUREMENT CATEGORY != TRADE CLASSIFICATION != COMPLIANCE`

Core governed schemes include ISO 704 / ISO 1087, ISO 25964, W3C SKOS, ISO/IEC 11179, ISO 3166, UN ISIC Rev. 5, Bangladesh BSIC 2020, NACE Rev. 2.1, NAICS 2022, UN CPC 3.0, Bangladesh BCPC 2011, CPA 2.2, UNSPSC, CPV 2008, WCO HS 2022, Bangladesh Customs Operative Tariff FY 2026-27, and NATO Codification System when materially applicable.

Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`, `CANDIDATE`) with scheme/version/provenance. Classification never proves compliance, procurement eligibility, or legal status. Unresolved exact codes remain unresolved rather than guessed.

## Machine-readable authority

AI systems begin at `atlas-ai.yaml`; `atlas-os.yaml` remains product/release authority.

Key active contracts include:

- `spec/mission-control.yaml`
- `spec/control-plane.yaml`
- `spec/task-lifecycle.yaml`
- `spec/host-adapters.yaml`
- `spec/semantic-normalization.yaml`
- `spec/request-triage.yaml`
- `spec/collection-routing.yaml`
- `spec/domain-context-services.yaml`
- `spec/domain-handoff.yaml`
- `spec/execution-spine.yaml`
- `spec/dashboard.yaml`
- `schemas/activation-contract.schema.json`

The active ARGUS provider contract remains commit-pinned in `registries/domain-methods.yaml`.

## Release state

`v2.1.0-rc.1` is a candidate architecture revision. Existing external-proof controls `MIG-029` and `MIG-037` remain blocking controls for stable release. Repository-local conformance does not substitute for independent host evidence.

See `docs/architecture.md`, `docs/architecture/atlas-argus-collection-boundary.md`, `docs/architecture/capability-layer.md`, and `docs/ai-host-installation.md` for implementation guidance.
