# Runtime

The canonical runtime preserves untouched input, interprets task intent and targets, then applies the Collection-Need Gate before provider selection or deep collection.

## Collection modes

- `NONE` — no external collection required.
- `ATLAS_DIRECT` — ordinary retrieval/research stays in ATLAS.
- `ARGUS_COLLECTION` — bounded structured intelligence collection is delegated to ARGUS.
- `HYBRID` — ARGUS collects while ATLAS retains substantive analysis/decision work.

The legacy `request_route` field remains a compatibility projection. `collection_mode` is authoritative for ARGUS activation.

Examples:

```text
Bangladesh Bank foreign exchange policy
  -> ATLAS_DIRECT

ST Engineering
  -> ARGUS_COLLECTION / C1-C2 target collection

coastal patrol vessel for Bangladesh Coast Guard
  -> ARGUS_COLLECTION / C3 buyer-product opportunity collection

share the annual procurement plan of Bangladesh Navy
  -> ARGUS_COLLECTION / C3 procurement-plan collection

compare ST Engineering and L3Harris for Bangladesh opportunities
  -> HYBRID
  -> ARGUS collects; ATLAS compares/qualifies/decides
```

## Execution spine

After the lossless input boundary:

1. `INTENT_AND_TARGET_INTERPRETATION`
2. `COLLECTION_NEED_GATE`
3. `CONDITIONAL_DOMAIN_CONTEXT`
4. `CAPABILITY_AND_EXECUTION_PLAN`
5. `DATA_PLANE_EXECUTION`
6. `ASSURANCE_AND_VERIFICATION`
7. `OUTPUT_AND_PERSISTENCE`

Mission Control, Control Plane, Observability and Dashboard are cross-cutting ATLAS authorities/surfaces. ARGUS never creates a competing execution spine.

## Provider routing

Before routing an external or specialist provider, ATLAS presents the digest-bound routing preview. Approval binds to that exact proposal. Changed providers, permissions, task classes, prerequisites, data scope or execution sequence invalidate stale approval.

ARGUS canonical specialist requirement is `intelligence_collection`. A governed `READY` or `PARTIAL` domain-context handoff plus collection mission may proceed under the pinned contract. `BLOCKED` never authorizes dependent collection.

ARGUS returns evidence/collection state to ATLAS. ATLAS performs strategic analysis, forecasting, scenario work, opportunity qualification, business decisions, assurance, persistence and final delivery.

## Domain Context Services

Use only material context. Keep sector, industry/activity, product/service, procurement category, customs code and capability distinct. Verify official scheme editions when currency matters. Never infer certification, compliance, procurement eligibility or legal status merely from classification.

## Dashboard

Dashboard is read-only and event-driven. Show collection mode and ARGUS status when material. A request from Dashboard to expand, redirect, stop or restart collection becomes a Mission Control command evaluated by Control Plane.

## Failure / resumption

Failures remain explicit (`BLOCKED`, `PARTIAL`, `UNVERIFIED`, `CAPABILITY_UNAVAILABLE`, `AUTHORIZATION_REQUIRED`, `EVIDENCE_INSUFFICIENT`, `DEPENDENCY_FAILED`, `VALIDATION_FAILED`). Resumption restores structured state and reconciles it with actual external state before dependent work continues.
