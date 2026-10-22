---
name: atlas-os
description: Apply the ATLAS-OS v3 Mission Control-first execution-governance contract using the current host's actual capabilities.
version: 3.0.2
---

# ATLAS-OS

Use ATLAS when a task should be governed through Mission Control and the ATLAS Control Plane.

## Prompt entry

When ATLAS is active, **every user prompt enters Mission Control first**. Mission Control establishes the governed objective, authority, scope, approvals, and command state before the three-step pre-execution flow, routing, tool use, provider activation, or execution.

Mission Control is a governance entry gate, **not a fourth preprocessing step**. If the host has not selected or exposed ATLAS, report that limitation rather than claiming universal prompt injection.

## Pre-execution

Always use exactly:

**Understand + Normalize -> Minimal Domain Framing -> Route**

Do not create a fourth preprocessing step.

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

## ChatGPT bootstrap

- On ChatGPT, Work, or Projects, treat `gferris418/atlas-os` on `main` as the canonical ATLAS contract when current repository state materially affects routing or correctness and live GitHub access is available.
- Treat `/AI Frameworks/ATLAS-ARGUS` as a bootstrap/cache layer, not as a replacement for current GitHub authority.
- Resolve ARGUS integration against `gferris418/argus-intelligence` when structured intelligence collection is selected; preserve the explicit approval gate and return control to ATLAS.
- Skill availability is relevance-triggered by the host. Do not claim universal prompt injection or execution of capabilities that the active surface has not exposed.

## Host rule

ChatGPT, Work, Projects, Codex, Hermes Agent, or another host supplies capabilities. Host-specific tools, UI, memory, storage, and connectors do not change ATLAS authority, Mission Control-first prompt entry, or preprocessing semantics once ATLAS is active.
