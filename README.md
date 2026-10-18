# ATLAS OS

**Current candidate:** `v2.0.0-rc.8`
**Classification:** Internal  
**Release status:** **CANDIDATE / HOLD** pending independent cross-surface proof.

ATLAS-OS is a model-agnostic execution-governance specification for AI agents. It turns user intent into a controlled execution spine that preserves context, plans dependencies, routes capabilities, tracks evidence and uncertainty, enforces approval boundaries, verifies results, separates task state from canonical knowledge, and produces reproducible outputs.

ATLAS is not an autonomous model or a collection of prompts. The repository is the canonical machine-readable contract; ChatGPT, Codex, Work, and future surfaces implement adapters around the same core semantics.

## Execution spine

```text
INTAKE -> CONTEXT PRESERVATION -> NORMALIZATION -> COMPLETENESS CHECK
       -> TASK CLASSIFICATION -> DOMAIN CLASSIFICATION
       -> DOMAIN FRAMEWORK ALIGNMENT
       -> DEPENDENCY-AWARE PLANNING
       -> CAPABILITY ROUTING -> EVIDENCE ACQUISITION -> EXECUTION
       -> VERIFICATION -> PERSISTENCE -> DELIVERY
```

Execution depth is proportional: trivial work remains direct, while complex or high-impact work activates stronger planning, evidence, approval, and verification controls.

ATLAS uses capable host-platform features directly. It does not recreate ChatGPT or another host's language understanding, conversation, generation, reasoning, or tool behavior unless a deterministic fallback is required. ATLAS adds the smallest useful layer of standards, evidence, authority, persistence, interoperability, and verification.

## Authority model

1. [`atlas-os.yaml`](atlas-os.yaml) is the only product/release authority.
2. [`spec/`](spec/) defines normative core behavior.
3. [`schemas/`](schemas/) validates machine-readable state.
4. [`registries/`](registries/) declares capabilities, surfaces, controls, and migrations.
5. [`integrations/`](integrations/) adapts the core contract to execution surfaces.
6. [`migration/`](migration/) records open transition controls and evidence.
7. [`legacy/`](legacy/) contains historical references and is never active authority.
8. [`library/`](library/) stores authorized, reusable output artifacts by profile-defined collection.

Component revisions may describe compatibility and lineage, but cannot declare a competing product release.

## Lightweight control plane

Every prompt exposes compact operational state without private reasoning. Nontrivial work is split into atomic units with one active completion target; the display updates only at meaningful state changes:

```text
ATLAS/core [####------] 40% | 2026-10-17T23:30:00+06:00 | 420 ms
Goal update repository | Task 1/3 · EXECUTION: implement current work unit
Input requested repository update | Processing validating the active unit
Playbook test-first change | Framework ATLAS execution spine
SOP plan → execute → verify → persist → deliver | Plan plan-change:READY | Clarification NOT_REQUIRED
Output implementation pending | Profile output.technical-spec
Library READY · library/specifications/change.md (markdown)
Quality PENDING | Blocker None
```

The text-only visual is deterministic and constant-cost. Input and processing are safe summaries, never private chain-of-thought. Safe operations may be batched within the active unit, but a unit is not marked complete until its completion criteria are verified.

Every dashboard and work-unit selection is bound to a concrete plan identifier. The machine-readable dashboard contract is in [`spec/dashboard.yaml`](spec/dashboard.yaml) and [`schemas/dashboard.schema.json`](schemas/dashboard.schema.json).

## Evidence and routing

ATLAS distinguishes `VERIFIED`, `SUPPORTED`, `INFERRED`, `ASSUMED`, `SPECULATIVE`, and `UNKNOWN`. Source quality, completeness, confidence, and inference remain separate. Routing selects the best available capability using task fit, authority, permissions, risk, and fallback behavior; the presence of a tool alone is not a reason to call it.

Specialist domain methods remain separate systems. ATLAS activates one only from an explicit structured capability requirement, an active registration in [`registries/domain-methods.yaml`](registries/domain-methods.yaml), and any required valid domain-context handoff. A specialist never owns the ATLAS execution spine, plan, or approvals. See the compact [artifact model](docs/artifact-model.md) for the distinction between frameworks, methodologies, playbooks, SOPs, workflows, protocols, schemas, adapters, and related structures.

## Output standards

ATLAS lets the host generate naturally, then selects the smallest task-fit [output profile](registries/output-profiles.yaml). Eight baseline profiles cover concise answers, analysis, decisions, sourced research, execution progress, technical specifications, structured data, and artifact delivery. Explicit user formats take precedence.

Outputs use progressive disclosure and material-only validation. Ordinary conversation avoids schema overhead; machine-readable data, citations, APIs, and artifacts use applicable standards such as JSON Schema 2020-12, RFC 4180, RFC 3339, OpenAPI 3.1, WCAG 2.2 AA, and accessible or archival PDF profiles. Visuals are used only when they make a material relationship clearer. See [output standards and profiles](docs/output-standards.md).

## International standards and domain practices

When classification could materially change the result, ATLAS uses governed taxonomies to separate relevant jurisdiction, actor, product, capability, lifecycle, and sensitivity facets. It does not require unused facets. The baseline [taxonomy registry](registries/taxonomies.yaml) covers international terminology, knowledge-organization, metadata, geography, economic-activity, product, customs, procurement, and defense-logistics schemes. Conditional schemes are not applied outside their intended context, and missing codes remain unresolved.

ATLAS then assesses and applies relevant current international standards, recognized professional frameworks, and authoritative domain best practices. It records the framework, issuer, official source, version or edition policy, applicability, implementation mapping, and justified deviations. Applicable law, regulation, and binding requirements take precedence.

The baseline [framework registry](registries/frameworks.yaml) is deliberately extensible rather than exhaustive. If no adequate current framework is known, ATLAS reports `RESEARCH_REQUIRED` and consults official sources instead of silently falling back to generic advice. Alignment does not imply certification or compliance; those claims require scope-specific verification evidence.

See [taxonomy and classification](docs/taxonomy-and-classification.md) for the multi-axial model and the [sample Bangladesh Navy coastal-surveillance-radar workflow](docs/sample-workflow-coastal-surveillance-radar.md) for a complete stage-by-stage example.

## Persistence

Task execution state and durable canonical library state are separate namespaces. Every delivered output is routed by its output profile to `answers`, `analyses`, `decisions`, `research`, `execution`, `specifications`, `data`, or `artifacts` in the correct supported format. The filesystem adapter contains paths beneath the configured library, writes atomically, syncs, reads back, and returns a SHA-256 receipt before `SAVED` is allowed. Unavailable or unauthorized persistence remains visibly blocked. Canonical revisions carry identifiers, versions, timestamps, provenance, status, dependencies, and replacement lineage. A revision with active dependents cannot be archived or removed.

## ChatGPT Library distribution

For private-repository ChatGPT installs and updates, a successful push to `main` publishes a deterministic GitHub Actions artifact named `atlas-os-main-snapshot`. It contains the versioned repository ZIP/TAR, package manifest, and `SHA256SUMS` generated by `tools/package/build_release.py` after the validation suites pass.

A verified ChatGPT Library installation should be used as the normal runtime cache so ATLAS startup does not refetch GitHub on every prompt. GitHub is consulted when the user explicitly asks to install, update, or synchronize ATLAS-OS. Updates must verify the artifact checksums and require the package manifest `source_commit` to match the selected workflow run head SHA before replacing the Library snapshot.

See [`docs/chatgpt-library-install.md`](docs/chatgpt-library-install.md) for the complete installation, update, failure-handling, and provenance contract. Main-branch snapshot artifacts are transport packages, not releases, and do not change lifecycle state.

## Repository map

- `atlas_runtime/` — reference runtime, executable surface seams, and durable persistence adapter.
- `spec/` — normative declarative specifications.
- `schemas/` — JSON Schemas for state and governance artifacts.
- `registries/` — governed capabilities and control indexes.
- `tests/` — unit, conformance, and scenario regression evidence.
- `tools/validate/` — repository-wide validation.
- `tools/package/` — deterministic candidate packaging.
- `docs/` — architecture, operation, and release guidance.
- `library/` — durable, reusable outputs and storage guidance.

## Validate

```bash
python -m pip install --require-hashes -r requirements.lock
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/conformance -v
python -m unittest discover -s tests/regression -v
python -m unittest discover -s tests/integration -v
python tools/validate/validate_repository.py .
```

## Build deterministic release archives

```bash
python tools/package/build_release.py . dist
```

The package uses the candidate identifier from `atlas-os.yaml`, records the source commit, emits a manifest, and produces SHA-256 checksums.

## Current blockers

- `MIG-029`: independent New Chat and ChatGPT Work bootstrap proof is pending.
- `MIG-037`: independent cross-surface latest-control propagation proof is pending.
- `DTIF-RECONCILIATION`: data reconciliation remains open before archive-only disposition.

Missing proof remains missing proof. These controls prevent a stable `v2.0.0` release but do not prevent a truthful release-candidate package.

See [`GOVERNANCE.md`](GOVERNANCE.md), [`docs/architecture.md`](docs/architecture.md), and [`docs/release-process.md`](docs/release-process.md) for the normative change and release model.
