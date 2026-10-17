# ATLAS-OS governance

## Authority

`atlas-os.yaml` is the sole product and release authority. Normative precedence is manifest, active core specifications, schemas and registries, integration contracts, active migration records, documentation, then immutable legacy references. Surface adapters cannot redefine core semantics.

## Change classification

Changes are classified as `PATCH`, `MINOR`, `MAJOR`, `MIGRATION`, `GOVERNANCE`, `DOCUMENTATION`, `REGISTRY`, or `INTEGRATION`. Changes to runtime semantics, schemas, persistence, compatibility, or release gates require stronger review than documentation-only edits.

## Release lifecycle

`DRAFT -> CANDIDATE -> VERIFIED -> RELEASED -> SUPERSEDED -> ARCHIVED`

Generation, execution, verification, acceptance, and release are distinct states. Open release-blocking controls prohibit `RELEASED`, and missing evidence cannot be converted into a pass. A candidate may be packaged when its status and blockers are reported truthfully.

## Evidence and approval

Material claims identify provenance and evidence class. Destructive or irreversible actions, publication, financial commitments, external communication, permission changes, security-sensitive changes, and major canonical-state writes require scoped approval when appropriate. Existing approval applies only to its recorded scope.

## Dependency protection and retention

Keep the latest three relevant canonical revisions readily available. Older revisions may be archived only after dependents resolve to a valid replacement, migration is complete, and audit requirements permit it. History is never silently overwritten.

## Migration and deprecation

Migration records have explicit acceptance criteria, evidence, dependencies, owners, and state. Blockers close only with evidence. Deprecated material remains addressable through replacement lineage until dependents migrate.

## Legacy

Files under `legacy/` are immutable historical references. Active references must never resolve ambiguously to legacy paths.

