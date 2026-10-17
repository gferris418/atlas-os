# ATLAS OS

**Current candidate:** `v2.0.0-rc.3`
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

## Authority model

1. [`atlas-os.yaml`](atlas-os.yaml) is the only product/release authority.
2. [`spec/`](spec/) defines normative core behavior.
3. [`schemas/`](schemas/) validates machine-readable state.
4. [`registries/`](registries/) declares capabilities, surfaces, controls, and migrations.
5. [`integrations/`](integrations/) adapts the core contract to execution surfaces.
6. [`migration/`](migration/) records open transition controls and evidence.
7. [`legacy/`](legacy/) contains historical references and is never active authority.

Component revisions may describe compatibility and lineage, but cannot declare a competing product release.

## Startup dashboard

Substantive tasks expose compact operational state without private reasoning:

```text
ATLAS
Progress: 0%
Active: Understand and structure task
Blocker / Approval: None
Library: Loaded / Not required
```

The machine-readable dashboard contract is in [`spec/dashboard.yaml`](spec/dashboard.yaml) and [`schemas/dashboard.schema.json`](schemas/dashboard.schema.json).

## Evidence and routing

ATLAS distinguishes `VERIFIED`, `SUPPORTED`, `INFERRED`, `ASSUMED`, `SPECULATIVE`, and `UNKNOWN`. Source quality, completeness, confidence, and inference remain separate. Routing selects the best available capability using task fit, authority, permissions, risk, and fallback behavior; the presence of a tool alone is not a reason to call it.

## International standards and domain practices

Every substantive task first uses governed taxonomies to separate jurisdiction, operator and supplier industries, product or service, capability, lifecycle, and information sensitivity. The baseline [taxonomy registry](registries/taxonomies.yaml) covers international terminology, knowledge-organization, metadata, geography, economic-activity, product, customs, procurement, and defense-logistics schemes. Conditional schemes are not applied outside their intended context, and missing codes remain unresolved.

ATLAS then assesses and applies relevant current international standards, recognized professional frameworks, and authoritative domain best practices. It records the framework, issuer, official source, version or edition policy, applicability, implementation mapping, and justified deviations. Applicable law, regulation, and binding requirements take precedence.

The baseline [framework registry](registries/frameworks.yaml) is deliberately extensible rather than exhaustive. If no adequate current framework is known, ATLAS reports `RESEARCH_REQUIRED` and consults official sources instead of silently falling back to generic advice. Alignment does not imply certification or compliance; those claims require scope-specific verification evidence.

See [taxonomy and classification](docs/taxonomy-and-classification.md) for the multi-axial model and the [sample Bangladesh Navy coastal-surveillance-radar workflow](docs/sample-workflow-coastal-surveillance-radar.md) for a complete stage-by-stage example.

## Persistence

Task execution state and durable canonical library state are separate namespaces. Canonical revisions carry identifiers, versions, timestamps, provenance, status, dependencies, and replacement lineage. A revision with active dependents cannot be archived or removed.

## Repository map

- `atlas_runtime/` — reference implementation of core invariants.
- `spec/` — normative declarative specifications.
- `schemas/` — JSON Schemas for state and governance artifacts.
- `registries/` — governed capabilities and control indexes.
- `tests/` — unit, conformance, and scenario regression evidence.
- `tools/validate/` — repository-wide validation.
- `tools/package/` — deterministic candidate packaging.
- `docs/` — architecture, operation, and release guidance.

## Validate

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/conformance -v
python -m unittest discover -s tests/regression -v
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
