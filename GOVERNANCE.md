# ATLAS-OS governance

This file is the human companion to the canonical machine governance policy at [`governance.yaml`](governance.yaml), validated by [`schemas/governance.schema.json`](schemas/governance.schema.json). If this document conflicts with a schema-valid machine contract, the machine contract governs. [`atlas-os.yaml`](atlas-os.yaml) remains the sole product and release authority.

## Authority

Machine precedence is declared in `governance.yaml`: product manifest, governance policy, AI discovery, core specifications, schemas, registries, integration contracts, active migration records, human guidance, then immutable legacy material. Surface adapters and human documentation cannot redefine core semantics.

## Change classification

Changes use the governed classes `PATCH`, `MINOR`, `MAJOR`, `MIGRATION`, `GOVERNANCE`, `DOCUMENTATION`, `REGISTRY`, or `INTEGRATION`. Runtime semantics, schemas, persistence, compatibility, release gates, authority, and security require stronger review than documentation-only edits.

## Release lifecycle

`DRAFT -> CANDIDATE -> VERIFIED -> RELEASED -> SUPERSEDED -> ARCHIVED`

Generation, execution, verification, acceptance, and release are distinct states. Open release-blocking controls prohibit `RELEASED`; missing evidence never becomes a pass. A candidate may be packaged only while blockers and lifecycle state are represented truthfully.

## Evidence and approval

Material claims require provenance under `spec/evidence.yaml`. Model output alone is not verified evidence. Approval policy is governed by `spec/approvals.yaml`; destructive or irreversible actions, publication, financial commitments, external communications, permission changes, security-sensitive changes, and major canonical-state writes are scoped approval-gated operations.

## Domain standards and best practices

`spec/domain-practices.yaml` and `registries/frameworks.yaml` govern framework selection. Current official sources are required where currency matters, binding requirements take precedence, and alignment must not be misrepresented as certification or verified compliance.

## Dependency protection and retention

At least three relevant canonical revisions remain readily available. Archival requires dependent replacement, completed migration, and audit permission. Canonical history is never silently overwritten.

## Migration and deprecation

Migration state is governed by `schemas/migration.schema.json` and `registries/migrations.yaml`. Blockers close only with evidence, a closed migration requires every acceptance criterion to pass, and deprecated material retains replacement lineage until dependents migrate.

## Legacy

`legacy/` is immutable historical material. Active authority must not resolve to legacy content.
