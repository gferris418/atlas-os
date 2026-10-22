---
description: "ATLAS OS documentation home: execution governance, architecture, runtime, evidence, capabilities, and the governed ARGUS boundary."
icon: compass
---

# ATLAS OS

ATLAS-OS is a **model-agnostic execution-governance architecture for AI agents**. It remains the single operating architecture between user intent and verified delivery. ARGUS is nested inside ATLAS as the governed intelligence-collection subsystem; it is not a peer operating system.

**Current candidate:** `v2.0.2-rc.6`  
**Control revision:** `atlas-bootstrap-2026-10-22-r10`

## Architecture at a glance

```text
Human / Event
  -> Mission Control
  -> Control Plane
  -> Intent + Target Interpretation
  -> Collection-Need Gate
       -> NONE
       -> ATLAS_DIRECT
       -> ARGUS_COLLECTION
       -> HYBRID
  -> Canonical Capability Planning
  -> Domain Context Services
  -> Data Plane
  -> Evidence Governance / Assurance / Verification
  -> Output / Persistence
  -> Observability
  -> Dashboard
```

## Start here

- [Architecture](architecture.md)
- [Canonical capability layer](architecture/capability-layer.md)
- [ATLAS–ARGUS collection architecture](architecture/atlas-argus-collection-boundary.md)
- [Runtime](runtime.md)
- [Evidence model](evidence-model.md)
- [ATLAS artifact model](artifact-model.md)
- [Capability Admission Standard](capability-admission.md)
- [Integration model](integrations.md)
- [Release process](release-process.md)

## Source of truth

The GitHub repository is authoritative for machine-readable contracts, implementation state, release decisions, and documentation source. GitBook is the published human-readable documentation layer.

Published documentation: https://accessasia.gitbook.io/accessasia-docs/atlas-os/
