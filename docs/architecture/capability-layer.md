# Canonical capability layer

ATLAS remains the single operating architecture. The capability layer expresses execution semantics inside ATLAS; it is not another control plane, workflow engine or multi-agent architecture.

## Placement

```text
USER / EVENT / FILE
  -> ATLAS bootstrap: Mission Control + Control Plane + Dashboard
  -> Understand + Normalize
  -> Minimal Domain Framing
  -> Route
  -> Canonical Capability Planning
       -> if ARGUS required: explicit user authorization gate
  -> ATLAS execution / authorized ARGUS collection
  -> Evidence Governance
  -> Assurance / Verification
  -> Output / Persistence
```

Capability planning consumes the authoritative `collection_mode`. It cannot change `NONE`, `ATLAS_DIRECT`, `ARGUS_COLLECTION` or `HYBRID`, and it cannot self-activate ARGUS.

`ARGUS_COLLECTION` or `HYBRID` creates an ARGUS requirement only. `argus.collection` becomes executable only after explicit user authorization and the remaining Control Plane gates pass.

## Canonical capabilities

| Capability | Class | Authority |
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

Kernel services are always active. Routed capabilities are selected only when task semantics require them. `argus.collection` may appear in the proposed capability plan when Route establishes collection need, but provider invocation remains blocked until explicit authorization.

## Semantic capability vs provider

ATLAS should request semantic capabilities and let the host adapter expose concrete implementations.

Examples of host-level semantic capability requirements include:

- `WEB_SEARCH`
- `FILE_READ`
- `FILE_WRITE`
- `CODE_EXECUTION`
- `DATABASE_QUERY`
- `EXTERNAL_ACTION`
- `PERSISTENCE`
- `SPECIALIST_METHOD`

The same semantic requirement may be satisfied by a native host function, plugin, connector, MCP server, subagent or API. Provider selection remains governed by ATLAS admission and routing rather than product-name coupling.

## Common capability contract

Every canonical capability records:

- owner and architectural class;
- purpose and accepted task classes;
- activation conditions and exclusions;
- collection dependency mode and allowed collection types;
- read/write/external-action permissions;
- side-effect class;
- evidence requirement;
- security profile;
- input/output contract;
- fallback.

Canonical interfaces:

- `schemas/capability-request.schema.json`
- `schemas/capability-result.schema.json`
- `registries/canonical-capabilities.yaml`

## Kernel services

### Evidence Governance

Research or ARGUS may discover evidence and propose grades. ATLAS Evidence Governance owns canonical claim state. Source, observation, inference and conclusion remain distinct. Canonical statuses are `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `DISPUTED`, `UNVERIFIED`, and `STALE`.

### Execution Governance

Mission Control expresses what the user authorizes or requests. The Control Plane decides whether that action may proceed. Execution Governance supplies side-effect, approval, idempotency, retry, compensation, failure/resume, escalation, kill-switch and audit semantics.

Explicit ARGUS authorization is part of this governance path and cannot be delegated to the specialist provider itself.

### Agent Security

Agent Security applies at install, activate, execute and verify gates. It evaluates prompt injection, indirect injection, tool misuse, excessive agency, memory poisoning, private-data leakage, MCP/connector surfaces, dependency/supply-chain risk, credentials, egress and provider integrity.

External scanners are evidence providers to Agent Security, not ATLAS security authority.

### Classification Crosswalk

Classification is multi-axial. ATLAS keeps domain, sector, industry, economic activity, product/service, capability, procurement category, trade classification and compliance separate. Crosswalk relations are explicit: `EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED` and `CANDIDATE` where uncertainty is material.

## Routed and hybrid capabilities

### Deep Research

Question -> scope -> research facets -> source strategy -> direct retrieval or authorized collection handoff -> Evidence Governance -> synthesis -> contradiction review -> open questions.

Deep research does not imply ARGUS. A policy study may remain `ATLAS_DIRECT`; a target dossier or multi-source landscape may require `ARGUS_COLLECTION` or `HYBRID`, which then requires user authorization.

### Procurement Intelligence

After authorization where ARGUS is needed, ARGUS may collect procurement plans, tenders, projects, buyers, requirements, eligibility evidence, evaluation criteria, funding, incumbents, competitors and chronology. ATLAS retains opportunity qualification, probability, bid/no-bid, partner strategy, pricing/response strategy and submission governance.

### Commercial Contract Review

Supplied contract text stays in ATLAS by default. Output should separate clause, current position, preferred position, deviation, commercial/legal/operational impact, severity, fallback, proposed redline and escalation. Counterparty/project/market collection is a separate Collection-Need decision and, if ARGUS is needed, a separate explicit authorization event.

### Corporate Finance

Covers P&L, cash flow, working capital, project economics, commission economics, FX exposure, receivables/payables, budget vs actual, pricing, landed cost and scenarios. Supplied/internal data does not imply ARGUS; external market/funding/supplier collection may create `HYBRID` and therefore require ARGUS approval.

### Economic Policy Intelligence

Covers monetary, fiscal, foreign-exchange, trade and economic regulation. Policy analysis defaults to ATLAS authoritative research. Entity, programme, buyer, project or opportunity mapping may create `HYBRID`, subject to explicit ARGUS authorization.

## ARGUS collection

ATLAS first determines collection need. Mission Control then obtains the user's explicit authorization. The Control Plane validates the task/digest scope and only then authorizes the collection mission.

ARGUS derives PIR and EEI within the authorized scope and executes:

`PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`

ARGUS establishes what evidence exists and what remains unknown. ATLAS determines what the evidence can support, what it means and what should be done.

## Third-party capability admission

Third-party skills, plugins, MCP servers, tools, connectors, models and subagents are provider candidates. They pass through:

`Discover -> Security/Provenance Review -> Dependency/Permission Review -> Architectural Overlap Check -> Interface Adaptation -> Regression/Security Tests -> Admission`

Admission outcome is `ADOPT`, `ADAPT`, `MERGE`, `REWRITE`, or `REJECT`.

Provider frameworks cannot redefine ATLAS architecture, the three-step preprocessing sequence, Collection-Need routing, explicit ARGUS consent, Evidence Governance, canonical classification or approval authority.
