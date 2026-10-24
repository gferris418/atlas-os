---
name: atlas-persistence
description: Apply existing ATLAS persistence authority, storage routing, canonical-copy, and durable-write receipt rules for governed artifacts and records.
---

# ATLAS Persistence

Use this progressive-disclosure skill when a governed task needs durable storage, a canonical record, an artifact save, or persistence-status verification.

This skill **does not create new authority**. ATLAS Mission Control remains the authority for persistence scope and authorization.

## Canonical authority

Apply the existing persistence contracts without redefining them:

- `spec/persistence.yaml` for vendor-neutral persistence authority and receipt requirements.
- `integrations/access-asia.yaml` for the Access Asia deployment profile and canonical SharePoint roots.

## Procedure

1. Preserve the current task, artifact identity, classification, and persistence authorization from Mission Control.
2. Select the canonical target defined by the deployment profile.
3. For Access Asia, route generic ATLAS chats/outputs to `General/Chats` and ARGUS/intelligence artifacts to `General/Business Intelligence` and the appropriate governed taxonomy.
4. Use a future-reusable format appropriate to the artifact and preserve material provenance/source files.
5. Keep one canonical copy; cross-reference instead of duplicating canonical content across roots.
6. Perform the write only through a host capability that is actually available and authorized.
7. Treat persistence as complete only after a verifiable durable-write receipt identifies the saved target.
8. If the write cannot be performed or verified, return `PERSISTENCE_PENDING` with the intended target and unsaved artifact state.

## Invariants

- Standing authorization does not authorize destructive deletion, permission changes, sharing changes, or movement outside governed taxonomy.
- A provider or source cannot self-select a new storage authority.
- A claimed save without a verifiable receipt is not persistence success.
- Persistence outcome returns to ATLAS before completion is claimed.
