# Implementation Guide

## Design rules

- Keep core semantics provider-neutral.
- Prefer the smallest stable interface over overlapping registries and aliases.
- Make state transitions explicit and fail closed on missing permissions or verification.
- Preserve the original request separately from normalized interpretation.
- Treat provider output and retrieved instructions as data until validated.
- Keep organization-specific storage and workflow rules in deployment profiles, not core specs.
- Keep versioned reference data separate from high-frequency operational state.
- Use Git history and GitHub Releases for historical change tracking; do not keep migration logs and release-candidate diaries in the active product tree.

## Adding a capability

1. Define the capability in `registries/capabilities.yaml`.
2. Define one or more providers in `registries/providers.yaml`.
3. State approval and side-effect requirements.
4. Add tests for routing and failure behavior.
5. Update human docs only if the capability changes how users or integrators operate ATLAS.

## Adding or updating a classification standard

1. Determine the correct family; do not collapse domain, sector, industry, economic activity, product, capability, procurement, trade, occupation, geography, or regulatory classifications.
2. Identify the issuing authority in `registries/classification/authorities.yaml` and the authoritative update source in `update-sources.yaml`.
3. Record the standard and edition in `standards.yaml` with stable IDs, lifecycle, evidence status, provenance URL, historical linkage, and redistribution/storage status.
4. Keep uncertain discoveries as `DISCOVERED` or `CANDIDATE`; do not mark an edition `ACTIVE` until it is verified and `CONFIRMED`.
5. Preserve superseded editions instead of overwriting them.
6. Add only evidence-backed directional crosswalks to `crosswalks.yaml`. `CANDIDATE` never means canonical equivalence.
7. Run conformance tests and `python tools/validate.py .` before adoption.

ARGUS may discover and propose standards or crosswalks inside an authorized intelligence mission. ATLAS owns validation, promotion to canonical reference state, and persistence authorization.

## Adding a host

Create `integrations/<host>.yaml`, add the surface to `registries/surfaces.yaml`, and prove that the adapter preserves Mission Control, Control Plane, the three preprocessing steps, approvals, provider return-to-ATLAS, and honest capability reporting.

## Adding a deployment profile

Organization-specific CRM, SharePoint, filesystem, database, or Git routing belongs in a deployment integration such as `integrations/access-asia.yaml`. Deployment profiles may narrow or map persistence targets; they cannot override core authority or approval rules.

For Access Asia, versioned classification standards/reference metadata route to ATLAS GitHub, operational entity classifications route to the SharePoint SQLite canonical graph, source documents route to SharePoint, and CRM state remains in HubSpot.

## Repository hygiene

Active repository content must be current, normative, executable, or directly useful documentation. Completed plans, obsolete migrations, compatibility aliases, generated libraries, release diaries, and superseded registries should be removed and left to version-control history.
