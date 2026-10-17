# ATLAS OS

**Candidate:** `v2.0.0-rc.1`  
**Classification:** Internal  
**Release readiness:** **HOLD** pending independent cross-surface proof.

ATLAS OS v2 consolidates the v1.12 Library release into one Git-oriented source tree. `atlas-os.yaml` is the product-level authority. Component revisions remain visible for compatibility and lineage, but they no longer act as competing product releases.

## Authority model

1. `atlas-os.yaml` — single product/release authority.
2. `spec/`, `schemas/`, and `registries/` — active component sources.
3. `integrations/` — governed external-framework contracts.
4. `tests/` — conformance and release evidence.
5. `migration/` — open migration controls and transition records.
6. `legacy/` — historical authority snapshots; never active runtime authority.

## Current blockers

- `MIG-029`: independent New Chat and ChatGPT Work bootstrap proof is pending.
- `MIG-037`: independent cross-surface latest-control propagation proof is pending.
- DTIF data reconciliation remains open before archive-only disposition.

These blockers are intentionally carried forward. This candidate does **not** convert missing proof into a pass.

## Validate

```bash
python -m unittest discover -s tests/unit -v
python tools/validate/validate_repository.py .
```

## Build deterministic release archives

```bash
python tools/package/build_release.py . dist
```

## GitHub status

Canonical repository: `https://github.com/gferris418/atlas-os` (private). The repository is the Git source of truth for the v2 line. Final `v2.0.0` publication remains blocked until MIG-029 and MIG-037 are closed.

## Repository management
See `docs/repository-management.md` and `GOVERNANCE.md` for the Gate-B repository ruleset and release policy.
