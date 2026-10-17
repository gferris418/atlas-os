# Persistence

ATLAS separates active task state from canonical library state. Task state supports interruption and resumption. The canonical library stores delivered outputs through an explicit, authorized persistence decision.

Every output profile declares a collection and filename extension for each supported format. The baseline collections are `answers`, `analyses`, `decisions`, `research`, `execution`, `specifications`, `data`, and `artifacts`. The user-requested format wins when the profile supports it; otherwise the profile default applies. Storage adapters may map these logical collections to an approved repository, document store, or other durable system without changing the core contract.

Delivery state is explicit. `READY` means the target is valid but no durable write has been proven. `SAVED` requires a validated receipt with the exact location, SHA-256 checksum, byte count, and verification timestamp. `BLOCKED` means policy, authorization, or sensitivity prevents the write. `CAPABILITY_UNAVAILABLE` means no durable storage is accessible. ATLAS never reports a conversational response as saved merely because it appeared in chat.

The reference filesystem adapter rejects absolute or traversing paths, contains targets beneath the configured library root, writes through a temporary file, flushes and syncs, atomically publishes only a new target, reads the result back, and calculates its receipt from the verified bytes. Repeating the same content is idempotent; a conflicting overwrite is refused so canonical history cannot be silently destroyed.

Only minimized input and public processing summaries belong in output metadata. Secrets, raw sensitive prompts, private chain-of-thought, and hidden reasoning are not persisted by default. Restricted material requires an approved location and authorization.

Durable records identify version, timestamp, timezone, provenance, status, dependencies, and replacement lineage. Local-time-aware timestamps also include an unambiguous offset. The latest three relevant revisions remain readily available unless more are required by dependencies, audit, migration, or governance.

Before replacing or archiving canonical material, enumerate dependents, migrate references, validate the replacement, and preserve history. Active dependents block removal.

