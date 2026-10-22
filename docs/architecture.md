# Architecture

ATLAS-OS is a portable AI operating and governance layer. It runs inside a compatible AI host without becoming dependent on that host's model, UI, tool names or agent framework. ARGUS is a nested intelligence-collection subsystem under ATLAS, not a peer operating system.

## Architectural invariant

> **ATLAS governs. ARGUS collects. Tools execute. The host supplies capabilities. The user retains authority over consequential actions.**

## Four logical planes

```text
USER / EVENT / FILE
        |
        v
+---------------- EXPERIENCE PLANE ----------------+
| Mission Control                                  |
| Dashboard / progress / approvals / intervention |
+--------------------------------------------------+
        |
        v
+----------------- CONTROL PLANE ------------------+
| Task identity / lifecycle                        |
| Policy / permissions / approvals                 |
| Collection need / routing / provider admission  |
| ARGUS authorization / activation state          |
| Evidence / persistence authority                |
+--------------------------------------------------+
        |
        v
      Understand + Normalize
        |
      Minimal Domain Framing
        |
      Route
        |
        +--> NONE / ATLAS_DIRECT --> ATLAS
        |
        +--> ARGUS_COLLECTION -----> ARGUS APPROVAL GATE
        |                                  |
        |                                  +--> ARGUS collection
        |
        +--> HYBRID ----------------> ARGUS APPROVAL GATE
                                           |
                                           +--> ARGUS collection + ATLAS analysis
        |
        v
+---------------- EXECUTION PLANE -----------------+
| ATLAS capabilities / ARGUS / admitted providers |
+--------------------------------------------------+
        |
 Assurance / Verification -> Output / Persistence
        |
        v
+----------------- ADAPTER PLANE ------------------+
| ChatGPT / Hermes / Claude / Codex / MCP / APIs  |
+--------------------------------------------------+
```

The planes are responsibility boundaries, not extra preprocessing stages.

## Bootstrap invariant

Every substantive task begins by establishing:

- task and plan identity;
- Mission Control;
- authoritative Control Plane state;
- Observability;
- a compact Dashboard projection.

Bootstrap occurs before substantive execution and persists through the task lifecycle. It does **not** create a fourth preprocessing step.

## Canonical three-step preprocessing

The only user-visible preprocessing sequence is:

```text
UNDERSTAND_AND_NORMALIZE
        -> MINIMAL_DOMAIN_FRAMING
        -> ROUTE
```

### 1. Understand + Normalize

Read the complete available context as one semantic unit. Preserve the original input, critical literals, actors, relationships, requested outcome, constraints, jurisdiction, time/freshness and sensitivity. Normalization may improve surface form and canonical terminology but must not invent facts or overwrite the source input.

### 2. Minimal Domain Framing

Resolve only high-confidence, materially useful domain, sector, industry, product/service, capability, classification, standards and best-practice context needed for routing or downstream work.

Lifecycle stage, project/procurement existence, procurement route, budget/funding, quantity, detailed specification, exact codes, exact standards applicability, supplier/OEM and delivery timing are normally downstream facts and do not block routing when meaning is clear.

### 3. Route

Select one collection mode:

- `NONE`
- `ATLAS_DIRECT`
- `ARGUS_COLLECTION`
- `HYBRID`

`collection_mode` is authoritative for **ARGUS need**, not user consent.

## Mission Control

Mission Control is the exclusive human supervisory surface for:

- objective and scope;
- approval / rejection;
- explicit ARGUS authorization;
- pause / resume / abort;
- priorities and exceptions;
- collection expansion / reduction / redirect / stop;
- risk acknowledgement.

A UI interaction has no direct execution authority. It becomes a Mission Control command that the Control Plane validates.

## Control Plane

The Control Plane owns:

- task identity and lifecycle state;
- policy and permission evaluation;
- collection-need decision;
- routing and provider admission;
- approval state;
- ARGUS authorization state;
- ARGUS activation state;
- plans, work units and execution leases;
- dependency and external-state reconciliation;
- persistence authorization;
- audit/control receipts.

It remains authoritative until the task is completed, paused, aborted or superseded.

## ARGUS need, authorization and activation

These are three separate concepts:

```text
NEED
collection_mode = ARGUS_COLLECTION | HYBRID
        |
        v
AUTHORIZATION
explicit user decision through Mission Control
        |
        v
ACTIVATION
Control Plane admits handoff + provider only when all gates pass
```

An ARGUS route with no explicit authorization must stop at `AWAITING_APPROVAL`.

No authorization may be inferred from `collection_mode`, previous ARGUS use, a previous task, silence, continued conversation, specialist availability or an existing collection mission.

One explicit user action may authorize both the exact routing preview and ARGUS mission, but the Control Plane records routing approval and ARGUS authorization as separate states bound to the same task/digest.

## ARGUS boundary

ARGUS capability is `intelligence_collection` / `argus.collection`.

After explicit authorization, ATLAS passes a bounded mission and governed semantic handoff containing:

- source task/plan identity;
- whole normalized semantic context;
- material high-confidence framing;
- explicit unresolved downstream facts;
- PIR/EEI or other collection requirements;
- risk/integrity metadata;
- stop conditions and return expectations.

Within the authorized mission ARGUS may resolve targets, plan collection, discover/acquire sources, extract/normalize evidence, resolve entities, deduplicate, suggest collection-side classifications, corroborate, reconcile sources, expose gaps/conflicts/coverage and return a collection package.

ATLAS retains planning, permissions, approvals, canonical semantic meaning, classification acceptance, substantive/strategic analysis, forecasting/scenarios, opportunity qualification, pursuit decisions, assurance, persistence authorization, Observability, Dashboard and final delivery.

## Canonical lifecycle

Portable host-facing lifecycle states are:

```text
CREATED
  -> NORMALIZING
  -> FRAMING
  -> ROUTING
  -> AWAITING_APPROVAL   (when required)
  -> COLLECTING / ANALYZING
  -> VERIFYING
  -> PERSISTING
  -> COMPLETED
```

Control states are also `PAUSED`, `BLOCKED` and `ABORTED`.

The Control Plane owns lifecycle transitions; adapters and dashboards only project them.

## Adapter plane and host portability

A compatible host may provide:

- model reasoning/generation;
- conversation context;
- files;
- search/browser access;
- code execution;
- databases;
- plugins/connectors/MCP servers;
- persistence;
- external actions.

ATLAS requests semantic capabilities and admits concrete providers through routing/security controls. It should not hard-code a specific tool vendor unless the task itself requires that implementation.

A host may render Mission Control and Dashboard differently, but it may not redefine preprocessing, approval, routing, evidence, lifecycle or persistence semantics.

## Provider independence

Capabilities are semantic contracts; skills, tools, plugins, MCP servers, models, connectors, functions, subagents and specialist methods are providers.

Availability is not admission. Installation is not trust. Provider routing remains subordinate to capability admission, permissions, provenance, dependency/conflict checks, the digest-bound routing preview, applicable approvals and verification.

## Whole-context and classification invariant

ATLAS never collapses domain, buyer/end-user sector, supply-side sector, industry/activity, product/service, platform/system, procurement category, customs/trade code and capability into one code.

Current governed reference schemes include ISIC Rev. 5, NACE Rev. 2.1, NAICS 2022, CPC 3.0, CPA 2.2, UNSPSC, CPV 2008, HS 2022 and NATO Codification when materially applicable.

Crosswalks are explicit (`EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`, `CANDIDATE`). Uncertain exact codes remain unresolved; classification metadata does not prove compliance or eligibility.

`spec/domain-intelligence.yaml` remains a deprecated compatibility alias to `spec/domain-context-services.yaml` and is not active architectural authority.
