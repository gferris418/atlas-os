# Access Asia opportunity lifecycle integration

This integration overlays Access Asia's business-file lifecycle on the generic ATLAS execution/governance model. It does not change ATLAS core semantics.

Machine-readable policy: [`opportunity-lifecycle.yaml`](opportunity-lifecycle.yaml)

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

## ATLAS responsibilities

When moving a lifecycle folder, ATLAS should treat the operation as a governed canonical-state mutation:

1. resolve the exact current opportunity identifier and location;
2. verify the source folder exists;
3. verify the destination does not already contain the same identifier;
4. preserve the exact folder name `[Year]_[PXnnnnn]_[ShortName]`;
5. apply approval policy where required;
6. execute the move rather than creating a duplicate copy;
7. verify the resulting SharePoint state;
8. synchronize ARGUS structured location/state references;
9. claim completion only after verification.

No separate BID folder is created. Award does not create a new project identifier.
