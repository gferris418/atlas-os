# Canonical capability layer

ATLAS remains the single operating architecture. The capability layer is an execution-semantic layer inside ATLAS; it is not another control plane, workflow engine or multi-agent architecture.

## Placement

```text
USER / EVENT / FILE
  -> Mission Control
  -> Control Plane
  -> Intent + Target Interpretation
  -> Collection-Need Gate
  -> Canonical Capability Planning
  -> Domain Context Services
  -> ATLAS Data Plane / authorized ARGUS collection
  -> Evidence Governance
  -> Assurance / Verification
  -> Output / Persistence
  -> Observability / Dashboard
```

Capability planning consumes the already-authoritative `collection_mode`. It cannot change `NONE`, `ATLAS_DIRECT`, `ARGUS_COLLECTION` or `HYBRID`, and it cannot self-activate ARGUS.

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

Kernel services are always active. Routed capabilities are selected only when task semantics require them. `argus.collection` appears only when the Collection-Need Gate has selected `ARGUS_COLLECTION` or `HYBRID`.

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
- input and output schema;
- fallback.

The canonical interfaces are:
- `schemas/capability-request.schema.json`
- `schemas/capability-result.schema.json`
- `registries/canonical-capabilities.yaml`

## Kernel services

### Evidence Governance
Research or ARGUS may discover evidence and propose grades. ATLAS Evidence Governance owns canonical claim state. Source, observation, inference and conclusion remain distinct. Canonical statuses are `CONFIRMED`, `PROBABLE`, `POSSIBLE`, `DISPUTED`, `UNVERIFIED`, and `STALE`.

### Execution Governance
Mission Control decides what should happen. The Control Plane decides whether it may happen. Execution Governance supplies side-effect, approval, idempotency, retry, compensation, failure/resume, escalation, kill-switch and audit semantics. Workflow technology is replaceable implementation detail.

### Agent Security
Agent Security applies at install, activate, execute and verify gates. It evaluates prompt injection, indirect injection, tool misuse, excessive agency, memory poisoning, private-data leakage, MCP/connector surfaces, dependency and supply-chain risk, credentials, egress and provider integrity.

External scanners are evidence providers to Agent Security, not ATLAS security authority.

### Classification Crosswalk
Classification is multi-axial. ATLAS keeps domain, sector, industry, economic activity, product/service, capability, procurement category, trade classification and compliance separate. Crosswalk relations are explicit: `EXACT`, `CLOSE`, `BROADER`, `NARROWER`, `RELATED`.

## Routed and hybrid capabilities

### Deep Research
Question -> scope -> research facets -> source strategy -> direct retrieval or collection handoff -> Evidence Governance -> synthesis -> contradiction review -> open questions.

Deep research does not imply ARGUS. A policy study may remain `ATLAS_DIRECT`; a target dossier or multi-source landscape may require `ARGUS_COLLECTION` or `HYBRID`.

### Procurement Intelligence
ARGUS may collect procurement plans, tenders, projects, buyers, requirements, eligibility evidence, evaluation criteria, funding, incumbents, competitors and chronology. ATLAS retains opportunity qualification, probability, bid/no-bid, partner strategy, pricing/response strategy and submission governance.

### Commercial Contract Review
Supplied contract text stays in ATLAS by default. Output should separate clause, current position, preferred position, deviation, commercial/legal/operational impact, severity, fallback, proposed redline and escalation. Counterparty/project/market collection is a separate Collection-Need decision.

### Corporate Finance
Covers P&L, cash flow, working capital, project economics, commission economics, FX exposure, receivables/payables, budget vs actual, pricing, landed cost and scenarios. Supplied/internal data does not imply ARGUS; external market/funding/supplier evidence may create `HYBRID`.

### Economic Policy Intelligence
Covers monetary, fiscal, foreign-exchange, trade and economic regulation. Policy analysis defaults to ATLAS authoritative research. Entity, programme, buyer, project or opportunity mapping may create `HYBRID`.

## ARGUS collection

ATLAS authorizes the mission. ARGUS derives PIR and EEI internally without expanding the authorized scope, then executes:

`PIR -> EEI -> Collection Plan -> Source Plan -> Collect -> Resolve -> Grade -> Competing Hypotheses -> Gaps -> Package`

ARGUS establishes what evidence exists and what remains unknown. ATLAS determines what it can support, what it means, and what should be done.

## Third-party capability admission

Third-party skills, plugins, MCP servers, tools, connectors and models are provider candidates. They pass through:

`Discover -> Security/Provenance Review -> Dependency/Permission Review -> Architectural Overlap Check -> Interface Adaptation -> Regression/Security Tests -> Admission`

Admission outcome is `ADOPT`, `ADAPT`, `MERGE`, `REWRITE`, or `REJECT`.

Provider frameworks cannot redefine ATLAS architecture, Collection-Need routing, Evidence Governance, canonical classification or approval authority.
