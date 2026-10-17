# Architecture

ATLAS-OS is a normative execution-governance core surrounded by surface adapters. The core owns context, completeness, governed domain classification, domain-framework alignment, planning, routing, evidence, approval, output profiles, verification, persistence, versioning, and user-visible execution state. Adapters use native surface capabilities and map them into those contracts without copying or changing them.

```text
USER INTENT
     |
     v
+----------------------+
|    ATLAS-OS CORE     |
| context/completeness |
| standards/planning   |
| routing/evidence     |
| approval             |
| verification/state   |
+-----------+----------+
           |
    +------+------+------+
    |      |      |      |
  Codex ChatGPT  Work  Future
```

The executable `atlas_runtime` package is a conformance reference, not a second source of truth. Its behavior is tested against the declarative specifications and invariants.

The dependency direction is manifest -> core specs -> schemas/registries -> adapters -> execution. Legacy material is outside the active resolution path.

