# Machine-Readable AI Contract Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every active ATLAS authority, host adapter, release-control state, and output profile machine-readable and AI-consumable while preserving human renderings as non-authoritative views.

**Architecture:** Add one machine-readable AI entrypoint that points to the canonical product manifest, normative specifications, registries, host adapters, verification controls, and output contract. Replace Markdown-only adapter authority with schema-validated YAML adapter manifests, require canonical structured output for every active profile, and make repository validation reject drift between migration records, registries, and AI manifests. External host proofs remain evidence-gated and cannot be closed without independent evidence.

**Tech Stack:** Python 3.12, YAML, JSON Schema 2020-12, unittest, GitHub Actions.

## Global Constraints

- `atlas-os.yaml` remains the sole product/release authority.
- All active normative or operational authority must resolve to YAML or JSON.
- Markdown/PDF/HTML may remain human renderings but cannot be sole authority.
- Every active output profile must have a canonical JSON or YAML representation.
- Every active supported AI host must have a schema-valid adapter manifest.
- Release blockers must remain open unless their acceptance criteria are supported by independent evidence.
- Repository validation must fail on authority drift, registry/migration status drift, missing AI manifests, or non-machine-readable active profiles.

---

### Task 1: Add machine-readable AI authority and adapter contracts

**Files:**
- Create: `schemas/ai-manifest.schema.json`
- Create: `schemas/ai-host-adapter.schema.json`
- Create: `ai/manifest.yaml`
- Create: `integrations/*/adapter.yaml`
- Modify: `atlas-os.yaml`
- Modify: `registries/surfaces.yaml`
- Test: `tests/conformance/test_ai_readiness.py`

**Interfaces:**
- Consumes: `atlas-os.yaml`, `registries/surfaces.yaml`, existing integration directories.
- Produces: `authority.ai_manifest`, `ai/manifest.yaml`, one `adapter.yaml` for every active surface.

- [ ] Add failing conformance tests for the AI manifest and adapter manifests.
- [ ] Verify the test fails because the manifests do not exist and current surface registry paths point to Markdown.
- [ ] Add minimal schemas/manifests and repoint active surfaces to structured adapter files.
- [ ] Verify focused tests pass.
- [ ] Run repository validation through CI.

### Task 2: Make every output profile canonically machine-readable

**Files:**
- Modify: `registries/output-profiles.yaml`
- Modify: `spec/output.yaml`
- Modify: `schemas/registry.schema.json`
- Modify: `atlas_runtime/runtime.py`
- Test: `tests/conformance/test_ai_readiness.py`
- Test: `tests/unit/test_runtime.py`

**Interfaces:**
- Consumes: active output profiles and `prepare_library_record`.
- Produces: structured canonical output with optional human render formats.

- [ ] Add failing tests requiring all active profiles to declare `machine_readable: true`, a structured canonical format, and a human-render policy.
- [ ] Verify failure against the current seven non-machine-readable profiles.
- [ ] Implement the minimum profile/schema/runtime changes.
- [ ] Verify profile selection, validation, and library planning remain compatible.
- [ ] Run affected unit and regression suites through CI.

### Task 3: Machine-read release verification and pending controls

**Files:**
- Create: `schemas/release-verification.schema.json`
- Create: `integrations/chatgpt/release-verification.yaml`
- Create: `integrations/hermes-agent/release-verification.yaml`
- Create: `integrations/codex/release-verification.yaml`
- Create: `integrations/work/release-verification.yaml`
- Modify: `migration/MIG-029.yaml`
- Modify: `migration/MIG-037.yaml`
- Modify: `registries/migrations.yaml`
- Modify: `tools/validate/validate_repository.py`
- Test: `tests/conformance/test_ai_readiness.py`

**Interfaces:**
- Consumes: migration records and host verification requirements.
- Produces: schema-valid evidence requests and consistent migration status.

- [ ] Add failing tests requiring structured release-verification records and exact migration/registry status agreement.
- [ ] Verify current `MIG-029` status drift is detected (`IN_PROGRESS` vs registry `blocked`).
- [ ] Add structured verification records and synchronize status without weakening acceptance criteria.
- [ ] Extend repository validation to enforce consistency.
- [ ] Run full validation through CI.

### Task 4: Version, verify, and publish the candidate change

**Files:**
- Modify: `atlas-os.yaml`
- Modify: `.agents/skills/atlas-os/SKILL.md`
- Modify: `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`
- Modify: `CHANGELOG.md`
- Create: `docs/releases/v2.0.2-rc.3.md`

**Interfaces:**
- Consumes: passing repository state.
- Produces: `v2.0.2-rc.3` / `atlas-bootstrap-2026-10-22-r7` candidate identity.

- [ ] Update candidate identity after contract tests are green.
- [ ] Run all unit, conformance, regression, integration, and repository validation checks in GitHub Actions.
- [ ] Confirm `MIG-029` and `MIG-037` remain externally evidence-gated unless independent host evidence exists.
- [ ] Merge only after protected `validate` passes.

## Unresolved externally observable decisions

None. Human presentation remains optional, but canonical persisted output is structured. External release controls retain their existing independent-evidence requirements.