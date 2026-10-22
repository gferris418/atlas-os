# Access Asia integration overlay

This integration overlays Access Asia's business lifecycle and persistence-routing rules on the generic ATLAS execution/governance model. It does not change ATLAS core semantics.

Machine-readable contracts:
- [`opportunity-lifecycle.yaml`](opportunity-lifecycle.yaml) — opportunity/project working-file lifecycle.
- [`system-of-record.yaml`](system-of-record.yaml) — canonical system ownership and persistence routing across HubSpot, SharePoint, ARGUS GitHub and ATLAS GitHub.

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
