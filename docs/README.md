---
description: ATLAS-OS v3 documentation: Mission Control, architecture, framework, playbook, SOP, routing, evidence, classification standards, ARGUS boundary, and host integration.
---

# ATLAS OS

ATLAS-OS is a portable operating framework for AI work. When ATLAS is active, every user prompt enters Mission Control first. ATLAS then preserves user authority, applies the three-step preprocessing flow, chooses the next execution mechanism, reconciles every provider return, governs classification reference data, and verifies outcomes before delivery.

**Version:** `3.0.2`

## Operating invariant

> **Mission Control is the first ATLAS governance gate. ATLAS governs. Providers execute bounded capabilities. Every provider returns to ATLAS. The user retains authority over consequential actions.**

Mission Control precedes preprocessing and is not a fourth preprocessing step. The preprocessing sequence remains exactly: **Understand + Normalize → Minimal Domain Framing → Route**.

Host skill loading remains capability- and relevance-dependent. ATLAS-OS guarantees Mission Control-first behavior while ATLAS is active; it does not claim universal prompt injection on hosts that have not loaded ATLAS.

## Start here

- [Architecture](architecture.md)
- [Framework](framework.md)
- [Playbook](playbook.md)
- [Standard Operating Procedure](sop.md)
- [Capabilities and Routing](capabilities-routing.md)
- [Evidence and Verification](evidence-verification.md)
- [Classification Standards Registry](classification-standards.md)
- [ARGUS Interface](argus-interface.md)
- [Host Integration](host-integration.md)
- [Implementation Guide](implementation-guide.md)
- [Examples](examples.md)

GitHub is the source of truth for machine contracts and implementation. GitBook is the published human-readable projection.
