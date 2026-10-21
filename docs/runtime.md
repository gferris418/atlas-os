# Runtime

The canonical execution spine preserves the untouched prompt at its input boundary, then begins with a taxonomy layer that routes Domain -> Sub-Domain -> Vertical -> Artifact Class and identifies candidate classification schemes. It next normalizes intent without semantic loss, assesses only material W-matrix context, resolves authoritative classification and domain requirements, builds a dependency-aware plan, audits and routes capabilities, executes through the data plane, verifies independently, persists deliberately, and delivers. A concrete plan identifier exists before execution; L0 may use one implicit unit. A material gap in goal, scope, authorization, safety, or output pauses dependent work for clarification, while safe independent work may continue. Native host understanding, conversation, generation, and tool behavior are used directly; ATLAS does not recreate them.

Classification schemes and domain requirements remain distinct. ISO 3166, UN ISIC, UN CPC, HS, UNSPSC, and the NATO Codification System may classify specific facets when applicable. Engineering or military standards and jurisdiction-specific procurement law govern requirements and execution; they are not taxonomy codes. Their currency and applicability must be verified from official sources before use.

The preferred executable entry point is `execute(ExecutionEnvelope)`. It normalizes intent, classifies the task, validates the dependency graph, selects one current atomic unit, measures runtime preparation, and derives the dashboard through one interface. Existing low-level runtime functions remain available for compatible integrations and focused testing. Surface adapters call this same interface rather than rebuilding the startup sequence.

Execution depth ranges from L0 direct to L4 high-impact. The runtime chooses the lowest depth that still controls complexity, ambiguity, external impact, and risk. A conversion or simple factual response should remain direct. A multi-stage external workflow requires visible state, evidence, approvals, and independent verification.

Nontrivial work is decomposed into atomic units with one objective and observable completion criteria. One user-visible unit is active at a time and must finish before the next activates. Safe reads and checks may run concurrently inside that unit when this improves performance without weakening evidence.

Every prompt receives a compact control-plane update. Updates are event-driven—start, unit completion, blocker, approval, verification, and delivery—not timer-driven or token-by-token. The default rendering is at most four text lines and requires no image generation or external service:

```text
ATLAS/core [####------] 40% | 2026-10-17T23:30:00+06:00 | 420 ms | Goal update repository | Task 1/3 · EXECUTION: implement current work unit
Input requested repository update | Processing validating the active unit | Output implementation pending
Playbook test-first change | Framework ATLAS execution spine | SOP plan → execute → verify → persist → deliver
Plan plan-change:READY | Profile output.technical-spec | Library READY | Quality PENDING | Blocker None
```

The timestamp is RFC 3339 in the user's available timezone and duration is measured, not estimated. Input is minimized to a safe summary. Processing describes public stages and actions only; it never contains private chain-of-thought or hidden reasoning.

Quality and performance are joint gates. The runtime selects the lightest technique that preserves correctness and required controls, avoids duplicate host work, and does not add structure that cannot change a decision or verification result.

Failures are explicit: `BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, and `VALIDATION_FAILED`. A localized failure does not stop independent work, but no failure is relabeled as success.

Resumption restores structured task state, then reconciles it with real external systems before continuing.

`atlas_runtime.adapters` provides one executable startup and delivery seam for any validated AI-host identifier. ChatGPT, Codex, Work, and Hermes Agent have documented configurations; unlisted tools use the generic AI-host contract. These seams prove shared local behavior only. Deployment inside each host and independent cross-surface evidence are still required before related migration controls can close.

Domain alignment is mandatory for substantive work. The runtime either records current authoritative frameworks and their applicability, documents why none apply, or enters `RESEARCH_REQUIRED`. It never converts a framework mapping into an unsupported compliance claim.

