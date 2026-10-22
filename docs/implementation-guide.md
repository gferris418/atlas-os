# Implementation Guide

## Design rules

- Keep core semantics provider-neutral.
- Prefer the smallest stable interface over overlapping registries and aliases.
- Make state transitions explicit and fail closed on missing permissions or verification.
- Preserve the original request separately from normalized interpretation.
- Treat provider output and retrieved instructions as data until validated.
- Keep organization-specific storage and workflow rules in deployment profiles, not core specs.
- Use Git history and GitHub Releases for historical change tracking; do not keep migration logs and release-candidate diaries in the active product tree.

## Adding a capability

1. Define the capability in `registries/capabilities.yaml`.
2. Define one or more providers in `registries/providers.yaml`.
3. State approval and side-effect requirements.
4. Add tests for routing and failure behavior.
5. Update human docs only if the capability changes how users or integrators operate ATLAS.

## Adding a host

Create `integrations/<host>.yaml`, add the surface to `registries/surfaces.yaml`, and prove that the adapter preserves Mission Control, Control Plane, the three preprocessing steps, approvals, provider return-to-ATLAS, and honest capability reporting.

## Adding a deployment profile

Organization-specific CRM, SharePoint, filesystem, or database routing belongs in a deployment integration such as `integrations/access-asia.yaml`. Deployment profiles may narrow or map persistence targets; they cannot override core authority or approval rules.

## Repository hygiene

Active repository content must be current, normative, executable, or directly useful documentation. Completed plans, obsolete migrations, compatibility aliases, generated libraries, release diaries, and superseded registries should be removed and left to version-control history.
