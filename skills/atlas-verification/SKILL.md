---
name: atlas-verification
description: Apply existing ATLAS verification and completion policy to provider results, external actions, evidence, and persisted outputs before success is claimed.
---

# ATLAS Verification

Use this progressive-disclosure skill when a provider has returned, an external action has run, a write has been attempted, or ATLAS must decide whether the governed task is complete.

This skill **does not create new authority**. ATLAS Mission Control remains the authority for acceptance, completion, retry, escalation, and delivery.

## Canonical authority

Apply `spec/verification.yaml` as the verification contract. Do not replace it with provider-specific success criteria.

## Procedure

1. Preserve the governed objective, acceptance criteria, route, action scope, provider result, and evidence receipts.
2. Verify that the result corresponds to the current task/intent and has not been superseded.
3. Check required evidence, side effects, output integrity, and persistence receipts where applicable.
4. Treat **provider success** as an input to verification, not as ATLAS completion.
5. Distinguish `VERIFIED`, `PARTIAL`, `FAILED`, and `BLOCKED` outcomes according to the canonical verification contract.
6. Return unresolved gaps, required retries, or evidence deficiencies to Mission Control.
7. Claim completion only when ATLAS acceptance criteria and required verification evidence are satisfied.

## Invariants

- Tool or provider success cannot waive missing acceptance evidence.
- A durable write without a receipt is not verified persistence.
- A stale or mismatched provider result is not accepted as current completion.
- Verification never invents evidence, closes unresolved blockers silently, or creates a new control plane.
