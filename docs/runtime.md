# Runtime

The canonical execution spine begins with intake and context preservation, then normalizes without semantic loss, assesses material completeness, classifies only material context, aligns it with applicable domain standards and frameworks, produces a dependency-aware plan, routes capabilities, acquires evidence, executes, verifies, persists deliberately, and delivers. Native host understanding, conversation, generation, and tool behavior are used directly; ATLAS does not recreate them.

Execution depth ranges from L0 direct to L4 high-impact. The runtime chooses the lowest depth that still controls complexity, ambiguity, external impact, and risk. A conversion or simple factual response should remain direct. A multi-stage external workflow requires visible state, evidence, approvals, and independent verification.

Nontrivial work is decomposed into atomic units with one objective and observable completion criteria. One user-visible unit is active at a time and must finish before the next activates. Safe reads and checks may run concurrently inside that unit when this improves performance without weakening evidence.

Every prompt receives a compact control-plane update. Updates are event-driven—start, unit completion, blocker, approval, verification, and delivery—not timer-driven or token-by-token. The default rendering is three text lines and requires no image generation or external service:

```text
ATLAS [####------] 40%
Now 1/3 · EXECUTION: implement current work unit
Quality PENDING | Blocker None
```

Quality and performance are joint gates. The runtime selects the lightest technique that preserves correctness and required controls, avoids duplicate host work, and does not add structure that cannot change a decision or verification result.

Failures are explicit: `BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, and `VALIDATION_FAILED`. A localized failure does not stop independent work, but no failure is relabeled as success.

Resumption restores structured task state, then reconciles it with real external systems before continuing.

Domain alignment is mandatory for substantive work. The runtime either records current authoritative frameworks and their applicability, documents why none apply, or enters `RESEARCH_REQUIRED`. It never converts a framework mapping into an unsupported compliance claim.

