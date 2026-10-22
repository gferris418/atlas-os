# Access Asia integration overlay

This integration overlays Access Asia's business lifecycle, persistence-routing and runtime-optimization rules on the generic ATLAS execution/governance model. It does not change ATLAS core semantics.

Machine-readable contracts:
- [`opportunity-lifecycle.yaml`](opportunity-lifecycle.yaml) — opportunity/project working-file lifecycle.
- [`system-of-record.yaml`](system-of-record.yaml) — canonical system ownership and persistence routing across HubSpot, SharePoint, ARGUS GitHub and ATLAS GitHub.
- [`operating-policy.yaml`](operating-policy.yaml) — fixed-versus-variable runtime contract and efficiency controls.
- [`mcp-roadmap.yaml`](mcp-roadmap.yaml) — phased connector/MCP rollout and infrastructure triggers.

## Lifecycle

```text
ARGUS signal
  -> PROMOTE_TO_PX / tracked registration
  -> General/Business Intelligence/50_OPPORTUNITIES/[ID]
  -> all research, qualification, capture, live-tender review and pre-submission work remains there
  -> SUBMISSION_ACTIVE only
  -> General/REV/OPP Opportunities/[same ID]
  -> award/contract activation
  -> General/OPS/PRJ Projects/[same ID]
```

`PROMOTE_TO_PX`, tender publication, I9/Live procurement status, or preliminary intent to bid are not submission-folder move triggers.

`SUBMISSION_ACTIVE` means formal response-package execution has actually started for a specific solicitation after the bid decision.

## System-of-record ownership

ATLAS applies a **one owner per information class** rule and routes persistence deterministically:

| Information class | Canonical owner |
|---|---|
| Company/contact CRM identity, Access Asia relationship state, interactions, deals | HubSpot |
| Original/working documents and opportunity/project working folders | SharePoint |
| Government-commercial intelligence, ARGUS opportunities, events, matches, evidence metadata | ARGUS GitHub |
| ATLAS policy, runtime, registries and execution/persistence governance | ATLAS GitHub |

The integration rule is **pointers, not copies**. Cross-system references use stable integration keys and logical paths. Native HubSpot IDs, SharePoint item/drive IDs, sharing tokens, credentials, PII and restricted payloads are not stored in public Git; they are resolved through authorized connectors at runtime.

The registered SharePoint logical locator is:

```text
Access Asia Limited
site: /sites/accessasia
library: Documents
Business Intelligence root: General/Business Intelligence
```

The registered Business Intelligence folders are `10_SOURCE_MAP`, `20_ARCHITECTURE`, `30_OPERATIONS`, `40_VALIDATION`, `50_OPPORTUNITIES`, `90_ARCHIVE`, and `99_INBOX`.

## Fixed invariants versus runtime variables

The integration deliberately separates rules that must not drift from decisions that should adapt at runtime.

### Fixed invariants

The following remain authoritative and are referenced rather than copied into local tuning rules:

- canonical system ownership and public-Git safety: `system-of-record.yaml`;
- opportunity and project lifecycle: `opportunity-lifecycle.yaml`;
- approval semantics: `spec/approvals.yaml`;
- canonical execution sequence: `spec/execution-spine.yaml`.

Runtime optimization must not change those authorities.

### Runtime variables

The following may be tuned without changing the business model:

- which connected provider is used for a capability;
- which evidence sources are material for the request;
- task-specific freshness requirements;
- bounded retry count for transient technical failures;
- concurrency for independent read-only work;
- whether verified session context can be reused;
- dry-run inputs and expected-versus-observed comparison data.

These controls live in `operating-policy.yaml` so normal runs do not repeatedly rediscover the same decisions.

## Optimized execution flow

For Access Asia work, the efficient path is:

```text
load authorities once per session
  -> resolve request intent/target
  -> reuse still-valid verified context
  -> discover only connectors materially required for this request
  -> parallelize independent safe reads
  -> reconcile identity/lifecycle state before any write
  -> resolve the canonical owner
  -> evaluate approval policy only for the exact mutation
  -> execute one canonical mutation at a time
  -> verify external state
  -> synchronize pointers/derived state
  -> claim completion only after verification
```

This is an optimization overlay, not a second execution spine. ATLAS remains the governing spine and ARGUS remains a bounded intelligence specialist.

## ATLAS responsibilities

Before a write, ATLAS should classify the information class and route it to the canonical owner defined in `system-of-record.yaml`.

When moving a lifecycle folder, ATLAS treats the operation as a governed canonical-state mutation:

1. resolve the exact current opportunity identifier and location;
2. verify the source folder exists;
3. verify the destination does not already contain the same identifier;
4. preserve the exact folder name `[Year]_[PXnnnnn]_[ShortName]`;
5. apply approval policy where required;
6. execute the move rather than creating a duplicate copy;
7. verify the resulting SharePoint state;
8. synchronize ARGUS structured location/state references;
9. claim completion only after verification.

For CRM writes, ATLAS targets HubSpot rather than ARGUS. ARGUS may hold a supplier/customer intelligence overlay and a stable integration key, but current company/contact/relationship/deal state is resolved from HubSpot.

No separate BID folder is created. Award does not create a new project identifier. Dashboard and observability views are derived/read-only surfaces and are never the canonical business-data store.

## MCP roadmap

The rollout is intentionally staged:

1. **P0 — Stabilize existing connectors:** GitHub, HubSpot and SharePoint authentication, permissions, capabilities, runtime ID resolution and health visibility.
2. **P1 — Read automation and reconciliation:** verify ARGUS/HubSpot party links, PX/HubSpot/SharePoint lineage and actual lifecycle state before mutations; reuse verified context and parallelize independent reads.
3. **P2 — Governed write automation:** automate deterministic low-ambiguity CRM/folder/pointer mutations with approval, idempotency and external-state verification.
4. **P3 — Conditional infrastructure expansion:** add Postgres, secret management, event infrastructure or other MCP servers only when measured workload creates a real capability gap.

A new database is **not required now**. The current architecture should first become predictable and low-friction using the systems already designated as canonical.

## WorkOS position

WorkOS is not a replacement for ATLAS, HubSpot, SharePoint or ARGUS. It becomes useful if Access Asia builds a multi-user internal ATLAS/ARGUS application and needs centralized SSO, RBAC, Directory Sync or enterprise audit controls. Until then it remains an optional future identity/audit layer rather than a dependency of the intelligence workflow.

## HubSpot linkage status

The preferred non-sensitive linkage fields remain:

- Company: `argus_party_id`
- Deal: `access_asia_px_id`

Their creation is currently pending connector reliability. ATLAS/ARGUS runtime must not depend on those fields existing; stable keys can continue to be resolved through governed runtime reconciliation.

## Dry-run readiness

`operating-policy.yaml` defines a mutation-free dry-run mode. Each test case should record the selected collection mode, capabilities, persistence target, approval requirement, evidence/freshness gaps, expected lifecycle transition and verification plan. This allows examples to be compared against the intended architecture before expanding automation.
