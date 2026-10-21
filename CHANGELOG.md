# Changelog

All notable changes follow semantic versioning and preserve release lineage. The authoritative current product version is resolved only from `atlas-os.yaml`.

## Unreleased

## v2.0.2-rc.3

- Add `atlas-ai.yaml` as a schema-validated machine discovery entrypoint while preserving `atlas-os.yaml` as the sole product/release authority.
- Move the active provider-neutral control revision into the canonical machine manifest and publish `atlas-bootstrap-2026-10-22-r7`.
- Add machine-readable external verification contracts for ChatGPT, Codex, ChatGPT Work, and Hermes Agent under one JSON Schema.
- Replace free-form migration acceptance criteria and unconstrained evidence with typed criterion state, evidence IDs, provenance, independence, scope, and closure rules.
- Synchronize migration registry lifecycle states with canonical migration records and add CI/release validation for machine-contract drift.
- Keep `MIG-029` and `MIG-037` open until genuinely independent host evidence is captured; machine-readiness is not represented as external conformance proof.

## v2.0.2-rc.2

- Make the canonical execution spine taxonomy-first, with an explicit Domain -> Sub-Domain -> Vertical -> Artifact Class routing layer, ordered domain classifications, proportional W-matrix completeness, capability audit, data-plane execution, assurance, and verified delivery boundaries.
- Publish the provider-neutral `atlas-bootstrap-2026-10-21-r6` control revision across ChatGPT and Hermes Agent.

## v2.0.2-rc.1

- Add the MIT license grant and declare it separately from the product's internal information classification.
- Define ATLAS-OS explicitly as a platform-neutral AI-agent governance layer rather than a device operating system.
- Add project-local Agent Skills installation for Hermes Agent and compatible AI tools, plus portable setup guidance for ChatGPT and generic hosts.
- Generalize the executable adapter and dashboard contracts from a fixed provider list to validated AI-host identifiers.
- Add operator guidance for Ed25519 signing-key custody, admission, rotation,
  revocation, and trusted registry distribution.
- Make repository validation fail when executable handoff, lease, or signing
  registry contract versions drift from their JSON Schema constants.
- Add deterministic routing and CLI error-boundary regression coverage.
- Bind ChatGPT and Hermes Agent to one provider-neutral bootstrap revision and add an independent Hermes verification checklist.
- Expand latest-control propagation acceptance to Hermes Agent while defining how open-ended generic AI hosts enter conformance scope.
- Make independent bootstrap and propagation proof release-blocking for stable `v2.0.2` promotion.

## v2.0.1

- Promote the validated `2.0.1-rc.1` control-plane hardening to the stable channel.
- Add ATLAS-governed execution leases that separate the exact 24-hour initial handoff activation window from correlated ongoing execution, retry, resume, and result return.
- Add lifecycle-governed Ed25519 signing-key trust with activation, expiry, status, record-class scope, supersession, and fail-closed resolution.
- Upgrade the ATLAS/ARGUS seam to Domain Context Handoff `1.2.0`, Execution Lease `1.0.0`, and Signing Key Registry `1.0.0` without changing the ATLAS execution/approval authority boundary.
- Record successful credentialed ATLAS↔ARGUS E2E verification in both `main`-push and pull-request contexts and enforce protected `main` branches before stable promotion.
- Keep `MIG-029`, `MIG-037`, and `DTIF-RECONCILIATION` open as post-GA, non-release-blocking residuals; none is represented as completed.

## v2.0.0

- Promote the validated ATLAS OS v2 execution-governance contract to the stable channel.
- Include provider-independent capability admission, untrusted-content assurance, canonical-memory integrity, forecasting/foresight governance, and learning/calibration controls introduced through the release-candidate line.
- Preserve the ARGUS specialist boundary, immutable activation contract, approval authority, evidence semantics, persistence controls, and deterministic release packaging.
- Record the repository owner's 2026-10-19 release-risk acceptance for external-only bootstrap, propagation, and unavailable-DTIF proofs. `MIG-029`, `MIG-037`, and `DTIF-RECONCILIATION` remain open post-GA and are not represented as completed.
- Keep future independent surface verification and DTIF reconciliation under normal migration governance without blocking the 2.0.0 stable release.

## v2.0.0-rc.12

- Add provider-independent capability admission governance with explicit admission states, evidence gates, overlap analysis, runtime-availability checks, and graceful-degradation rules.
- Add governed capabilities for untrusted-content assurance, canonical-memory integrity, forecasting/foresight, and learning/calibration without making third-party providers hard runtime dependencies.
- Require forecasting workflows to preserve evidence lineage, assumptions, scenarios, skeptical challenge, forecast vintages, falsifiable signposts, and outcome calibration before accuracy claims.
- Preserve ATLAS authority over planning, approvals, evidence semantics, verification, persistence, and delivery while allowing ARGUS and other specialists to use admitted providers within their registered boundaries.
- Document the October 2026 reference-provider review and keep provider-specific rankings distinct from measured production benchmarks.
- Keep `MIG-029`, `MIG-037`, and `DTIF-RECONCILIATION` open; rc.12 remains a release candidate and does not imply stable-release readiness.

## v2.0.0-rc.11

- Add a directly executable `python -m atlas_runtime` boundary over the existing public execution interface.
- Default to the four-line text control plane and offer two-event NDJSON for low-overhead machine streaming.
- Add subprocess acceptance coverage for valid text, NDJSON, and malformed-input behavior.

## v2.0.0-rc.10

- Add one public `execute(ExecutionEnvelope)` interface that composes normalization, task classification, dependency planning, atomic work selection, timing, and control-plane state.
- Route all ChatGPT, Codex, and Work startup adapters through the same execution interface without removing the existing low-level compatibility functions.
- Add a four-line state-derived status view that preserves the required goal, task, input, processing, output, playbook, framework, SOP, plan, quality, library, and blocker fields.

## v2.0.0-rc.9

- Classify every executable operation by governed semantic action classes before approval policy evaluation.
- Fail closed when action classification is missing or unknown, and remove the fixed high-impact verb list.

## v2.0.0-rc.8

- Correlate every specialist handoff to the active task, plan, and work unit through a typed execution context.
- Consolidate generic and specialist selection in one routing module and enforce permission, prerequisites, conflicts, task class, and immutable contract provenance.
- Require domain-method invariants directly in the registry schema.
- Bind high-impact approvals to the exact action, target, input digest, precondition, approver identity, validity interval, and policy revision.
- Pin the ARGUS activation contract to an immutable source commit and SHA-256 digest.

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
