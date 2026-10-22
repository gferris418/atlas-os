# ATLAS Quality-First Runtime 3.0.3 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add quality-tier governance, machine-readable quality gates, incremental intelligence reuse contracts, a fast plain-text runtime renderer, governed chat-event persistence, and performance telemetry without weakening the canonical ATLAS execution spine.

**Architecture:** Mission Control remains the first governance gate and the preprocessing flow remains exactly `UNDERSTAND_AND_NORMALIZE -> MINIMAL_DOMAIN_FRAMING -> ROUTE`. Required quality tier is derived inside Minimal Domain Framing, providers return quality evidence to ATLAS, and ATLAS owns the quality gate, final verification, persistence authorization, rendering mode, and every next step. ARGUS remains a bounded provider and will receive a compatible Quality Ledger contract separately after ATLAS is merged.

**Tech Stack:** Python 3.12 reference runtime, YAML contracts, unittest, GitHub Actions, ChatGPT plugin skill packaging, SharePoint deployment integration.

## Global Constraints

- Quality / correctness / evidence integrity is priority 1; performance is priority 2.
- No performance optimization may reduce the required quality tier or bypass applicable evidence, verification, governance, or approval requirements.
- Preserve Mission Control-first prompt entry.
- Preserve the exact three-step preprocessing flow.
- ATLAS remains the sole orchestration and next-step authority.
- ARGUS remains a bounded provider and may not create a second execution spine.
- FAST_TEXT changes presentation only; it never changes research depth.
- Chat persistence stores complete user-visible prompt/final response and execution metadata, never hidden reasoning, system/developer instructions, credentials, signed URLs, or raw secret-bearing payloads.
- Organization-specific SharePoint storage rules remain in Access Asia deployment integration.

---

### Task 1: Quality tiers and framing

**Files:**
- Create: `atlas_runtime/quality.py`
- Modify: `atlas_runtime/router.py`
- Modify: `atlas_runtime/models.py`
- Modify: `atlas_runtime/__init__.py`
- Test: `tests/unit/test_quality.py`

**Interfaces:**
- Consumes: normalized objective and minimal framing signals.
- Produces: `required_quality_tier` (`Q0`..`Q5`), mandatory gate names, and quality policy metadata embedded in `domain_framing`.

- [ ] Add focused failing tests for deterministic Q0/Q1, ordinary Q2, high-assurance Q3, decision-grade Q4, and critical Q5 examples; verify quality tier is produced during Minimal Domain Framing while `PRE_EXECUTION_FLOW` remains unchanged.
- [ ] Run `python -m unittest tests.unit.test_quality -v`; expect failures because quality interfaces do not exist.
- [ ] Implement the minimum deterministic quality policy and expose it through the runtime package.
- [ ] Rerun focused tests and the existing unit suite; expect all pass.

### Task 2: Quality Ledger and Quality Gate

**Files:**
- Modify: `atlas_runtime/quality.py`
- Modify: `atlas_runtime/runtime.py`
- Modify: `atlas_runtime/models.py`
- Test: `tests/unit/test_quality.py`
- Test: `tests/unit/test_runtime.py`

**Interfaces:**
- Consumes: required tier plus provider/result quality metadata.
- Produces: normalized Quality Ledger, achieved tier, `PASS|CONTINUE|IRREDUCIBLE_GAP`, blocking reasons, and dashboard quality state.

- [ ] Add failing tests proving insufficient achieved tier blocks completion, mandatory gate failure cannot be offset by high confidence, sufficient ledger passes, and irreducible gaps are disclosed rather than silently accepted.
- [ ] Run focused tests and record the expected failures.
- [ ] Implement gate evaluation at provider-return reconciliation without changing provider ownership.
- [ ] Rerun focused and existing unit tests; expect pass.

### Task 3: Incremental intelligence reuse contract

**Files:**
- Create: `spec/quality-governance.yaml`
- Modify: `spec/evidence.yaml`
- Modify: `spec/verification.yaml`
- Modify: `atlas-os.yaml`
- Test: `tests/conformance/test_quality_governance.py`

**Interfaces:**
- Consumes: prior verified intelligence, Quality Ledger freshness/completeness/contradiction/invalidation state, and changed evidence.
- Produces: machine-readable `REUSE`, `REFRESH_DELTA`, or `RECOLLECT` recommendation while ATLAS retains authority.

- [ ] Add failing conformance tests for quality hierarchy, Q0-Q5 definitions, no quality downgrade for performance, incremental reuse rules, invalidation triggers, and exact three-step preprocessing preservation.
- [ ] Implement the normative YAML contract and register it in the product manifest.
- [ ] Run conformance tests and validation; expect pass.

### Task 4: FAST_TEXT runtime renderer and progress semantics

**Files:**
- Create: `atlas_runtime/render.py`
- Modify: `atlas_runtime/runtime.py`
- Modify: `atlas_runtime/__init__.py`
- Test: `tests/unit/test_render.py`

**Interfaces:**
- Consumes: `ExecutionResult` dashboard state.
- Produces: one mandatory compact status line and one optional `NEXT:` line; progress is deterministic/monotonic by stage and presentation mode never changes quality tier.

- [ ] Add failing tests for compact plain text, progress range/stage mapping, no rich table markup, and unchanged quality tier across render modes.
- [ ] Implement renderer and stage progress mapping.
- [ ] Run focused and full unit tests; expect pass.

### Task 5: Chat-event persistence contract

**Files:**
- Create: `atlas_runtime/persistence.py`
- Create: `spec/chat-event-persistence.yaml`
- Modify: `integrations/access-asia.yaml`
- Modify: `atlas-os.yaml`
- Modify: `skills/atlas-os/SKILL.md`
- Modify: `.agents/skills/atlas-os/SKILL.md`
- Test: `tests/unit/test_persistence.py`
- Test: `tests/conformance/test_chat_event_persistence.py`

**Interfaces:**
- Consumes: complete user-visible prompt, complete final user-visible response, task/route/quality metadata, and canonical artifact pointers.
- Produces: deterministic Markdown chat-event payload plus persistence requirement/state; deployment path `General/Business Intelligence/30_OPERATIONS/CHAT_LOGS/YYYY-MM/CHAT_<conversation-id>_T<turn>.md`.

- [ ] Add failing tests for deterministic Markdown event format, hashes, exclusion of private reasoning/system instructions/secrets, and exact storage policy.
- [ ] Implement serializer and normative/deployment contracts; require verified persistence before claiming persistence success when the host exposes the connector, while documenting that hosts without a post-turn/write hook cannot be falsely represented as continuously persisted.
- [ ] Run unit/conformance suites; expect pass.

### Task 6: Performance telemetry, release, and integration verification

**Files:**
- Create: `spec/performance-telemetry.yaml`
- Modify: `spec/observability.yaml`
- Modify: `atlas-os.yaml`
- Modify: `atlas-ai.yaml`
- Modify: `governance.yaml`
- Modify: `plugin.json`
- Modify: `integrations/chatgpt.yaml`
- Modify: `integrations/chatgpt-bootstrap.yaml`
- Modify: `README.md`
- Modify: `docs/README.md`
- Modify: `tools/validate.py`
- Modify: `tests/conformance/test_chatgpt_plugin_bootstrap.py`

**Interfaces:**
- Consumes: runtime events and quality/persistence state.
- Produces: latency, tool-call, cache/reuse, duplicate-retrieval, persistence-latency metrics that are explicitly non-authoritative for quality-tier selection.

- [ ] Add failing conformance/validation assertions for release 3.0.3, plugin packaging, telemetry semantics, quality-first ordering, and mirrored skill equality.
- [ ] Implement minimum release/config/docs changes.
- [ ] Run all repository validation commands plus ChatGPT plugin release gate and cross-repository compatibility checks.
- [ ] Review diff on standards/spec axes; merge only after all required checks pass.

## External observable decision seams

- SharePoint persistence is required for Access Asia deployments when an authorized write capability is available. A host without a reliable write/post-turn hook must report persistence as unavailable or pending; it must not claim background persistence.
- Event files are immutable per completed turn by default; conversation roll-ups are derived views, not canonical competing transcripts.
- Q5 means maximum-assurance / critical with explicit stopping justification, not literally unbounded exhaustive retrieval.
