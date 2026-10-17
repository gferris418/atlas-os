# Changelog

All notable changes follow semantic versioning and preserve release lineage. The authoritative current product version is resolved only from `atlas-os.yaml`.

## v2.0.0-rc.7

- Bind publication tags to manifest version, channel, lifecycle state, and stable-release blocker state.
- Reject duplicate work-unit IDs, invalid task states, stalled-plan false completion, and contradictory timestamp/timezone metadata.
- Harden filesystem persistence against symlink-root escape and link-swap attacks.
- Pin CI actions immutably, install from a hash-locked dependency graph, and run dependency vulnerability auditing.
- Add a single-file, version-bound ChatGPT compatibility profile with local integration validation.

## v2.0.0-rc.6

- Require a concrete plan identifier before dashboard initialization or work-unit execution.
- Add executable shared startup and delivery adapters for ChatGPT, Codex, and Work surface configurations.
- Add atomic filesystem persistence with path containment, fsync, read-back verification, SHA-256 receipts, idempotent retries, and conflicting-overwrite protection.
- Replace arbitrary persistence evidence dictionaries with validated receipt records.
- Add integration tests for cross-surface plan gating, real durable delivery, and unavailable persistence.
- Keep independent host bootstrap, propagation, and DTIF controls open until their external evidence exists.

## v2.0.0-rc.5

- Require a plan before execution and block dependent work while material clarification is pending.
- Expand the lightweight dashboard with timestamp, measured duration, safe input and processing summaries, output, goal, task, playbook, frameworks, SOP, profile, and persistence state.
- Route every output profile to a logical canonical-library collection and correct supported filename format.
- Require durable-write evidence before reporting an output as `SAVED`; expose blocked or unavailable persistence explicitly.
- Preserve privacy by excluding secrets, raw sensitive prompts, and private chain-of-thought from dashboard and library metadata by default.

## v2.0.0-rc.4

- Prefer native host capabilities and prohibit duplicative ATLAS behavior unless it adds material governance, persistence, interoperability, evidence, or verification value.
- Require atomic work units with one user-visible active completion target.
- Initialize a compact, event-driven text dashboard for every prompt without polling or heavy rendering.
- Make domain classification and alignment optional at L1 and mandatory at L2-L4.
- Prevent classification from reaching `CLASSIFIED` without an explicit material-facet policy.
- Add lean quality and performance rules plus INV-020 conformance coverage.
- Add eight proportional output profiles, progressive disclosure, accessibility and interoperability standards, a structured envelope, and material-only validation.

## v2.0.0-rc.3

- Add governed taxonomy, industry, product, geography, customs, procurement, and defense-logistics classification standards.
- Insert multi-axial domain classification before framework alignment.
- Treat conditional classifications and missing codes as unresolved rather than inferred.
- Add INV-019 and a Bangladesh Navy coastal-surveillance-radar regression scenario.

## v2.0.0-rc.2

- Require domain-framework alignment for every substantive task.
- Add a governed baseline registry of international standards and professional frameworks.
- Prevent framework alignment from being misrepresented as verified compliance or certification.
- Add INV-018 and executable conformance coverage.

## v2.0.0-rc.1

- Establish the ATLAS-OS v2 product authority and execution-governance contract.
- Add machine-readable specifications, schemas, registries, migrations, adapters, tests, validation, and deterministic packaging.
- Carry MIG-029, MIG-037, and DTIF reconciliation as open release blockers.

