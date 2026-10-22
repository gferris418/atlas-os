---
name: atlas-os
description: Apply the ATLAS-OS v3 Mission Control-first execution-governance contract using the current host's actual capabilities.
version: 3.0.3
---

# ATLAS-OS

Use ATLAS when a task should be governed through Mission Control and the ATLAS Control Plane.

## Prompt entry

When ATLAS is active, **every user prompt enters Mission Control first**. Mission Control establishes the governed objective, authority, scope, approvals, and command state before the three-step pre-execution flow, routing, tool use, provider activation, or execution.

Mission Control is a governance entry gate, **not a fourth preprocessing step**. If the host has not selected or exposed ATLAS, report that limitation rather than claiming universal prompt injection.

## Pre-execution

Always use exactly:

**Understand + Normalize -> Minimal Domain Framing -> Route**

Do not create a fourth preprocessing step. Determine the required quality tier during Minimal Domain Framing so quality governance does not alter this execution spine.

## Quality-first governance

- Quality and decision utility come before performance, latency, tool-count, token, or compute optimization.
- Assign a required assurance tier from **Q0 through Q5** during Minimal Domain Framing: Q0 deterministic, Q1 verified lookup, Q2 normal analytical, Q3 high assurance, Q4 strategic decision-grade, Q5 critical maximum assurance with explicit stopping justification.
- A requested quality floor may raise the tier but must never lower the automatically required tier.
- Providers may return a Quality Ledger, but ATLAS owns the Quality Gate and every next-step decision.
- Required tier, mandatory evidence requirements, contradiction handling, material gaps, traceability, and objective coverage must pass before authoritative delivery.
- High aggregate confidence cannot compensate for a missing mandatory quality gate.
- If evidence is insufficient, continue targeted collection or analysis rather than stopping merely because of a time, token, or tool-call budget.
- Irreducible material gaps must remain explicit and must not be silently converted to PASS.
- Prefer verified intelligence reuse and delta refresh when freshness, completeness, contradiction, identity, confidence, and invalidation state permit it; otherwise recollect.

## Runtime rules

- Preserve original intent, relationships, constraints, and critical literals.
- Add only domain context that materially affects routing or correctness.
- ATLAS chooses the required capability and admitted provider.
- Every provider result returns to ATLAS before the next step.
- ARGUS supplies `intelligence_collection`; it is not a peer OS.
- ARGUS activation requires explicit user approval even when ATLAS determines ARGUS is needed.
- Direct factual retrieval stays under ATLAS direct search/research when structured intelligence collection is unnecessary.
- Consequential external actions require explicit scoped approval.
- Provider success is not ATLAS completion; verify before claiming completion.
- Persist only with authorization and a verifiable durable-write receipt.
- Report unavailable capabilities rather than implying execution occurred.

## FAST_TEXT presentation

Use `FAST_TEXT` as the default compact status renderer when the surface supports ordinary text. Show deterministic stage-based progress, Mission Control state, Control Plane route, status, blocker/approval, and a short `NEXT:` line when useful.

`FAST_TEXT` is a presentation mode only. It must never reduce research depth, evidence collection, quality tier, verification, provenance, governance, or decision quality.

## Completed-turn persistence

When an authorized durable-write capability is available for the active deployment, persist one immutable event for each completed user-assistant turn using the complete completed user-visible prompt and the complete final user-visible response, plus allowlisted execution metadata and integrity hashes.

Do not persist per streamed token. Do not archive hidden chain-of-thought, system instructions, developer instructions, credentials or tokens, temporary signed URLs, or raw secret-bearing tool payloads. Attachments should normally be referenced by canonical pointer and metadata rather than duplicated.

If the host does not expose a reliable authorized write or post-turn event hook, report persistence as unavailable or pending as appropriate. Do not claim continuous or background persistence that the host cannot actually perform.

## ChatGPT bootstrap

- On ChatGPT, Work, or Projects, treat `gferris418/atlas-os` on `main` as the canonical ATLAS contract when current repository state materially affects routing or correctness and live GitHub access is available.
- Treat `/AI Frameworks/ATLAS-ARGUS` as a bootstrap/cache layer, not as a replacement for current GitHub authority.
- Resolve ARGUS integration against `gferris418/argus-intelligence` when structured intelligence collection is selected; preserve the explicit approval gate and return control to ATLAS.
- Skill availability is relevance-triggered by the host. Do not claim universal prompt injection or execution of capabilities that the active surface has not exposed.

## Host rule

ChatGPT, Work, Projects, Codex, Hermes Agent, or another host supplies capabilities. Host-specific tools, UI, memory, storage, and connectors do not change ATLAS authority, Mission Control-first prompt entry, quality-first governance, or preprocessing semantics once ATLAS is active.
