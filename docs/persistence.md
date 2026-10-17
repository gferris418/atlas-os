# Persistence

ATLAS separates active task state from canonical library state. Task state supports interruption and resumption. Canonical state stores durable specifications, decisions, configurations, and reusable artifacts only through an explicit persistence decision.

Durable records identify version, timestamp, timezone, provenance, status, dependencies, and replacement lineage. Local-time-aware timestamps also include an unambiguous offset. The latest three relevant revisions remain readily available unless more are required by dependencies, audit, migration, or governance.

Before replacing or archiving canonical material, enumerate dependents, migrate references, validate the replacement, and preserve history. Active dependents block removal.

