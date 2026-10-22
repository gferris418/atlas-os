# Standard Operating Procedure

## SOP-001 — Governed ATLAS Execution

### Phase A — Intake

1. Receive the request.
2. Create or resolve the task identity.
3. Preserve the original input and relevant context.
4. Initialize Mission Control, Control Plane, and the compact dashboard.

### Phase B — Preprocessing

Perform exactly:

1. `UNDERSTAND_AND_NORMALIZE`
2. `MINIMAL_DOMAIN_FRAMING`
3. `ROUTE`

Do not add a fourth preprocessing step.

### Phase C — Routing

ATLAS selects one or more mechanisms: `NO_TOOL`, `DIRECT_SEARCH`, `DEEP_RESEARCH`, `ARGUS`, `SPECIALIST`, `CONNECTED_SOURCE`, `CODE_EXECUTION`, `EXTERNAL_ACTION`, or `MULTI_CAPABILITY`.

If the selected action is approval-gated, stop at `AWAITING_APPROVAL` until explicit scoped authorization is available.

### Phase D — Execution

Execute one bounded work unit at a time unless ATLAS explicitly authorizes safe parallel work. Retries may not expand scope or bypass approval.

### Phase E — Provider Return

Return the result to ATLAS. ATLAS chooses one of:

- `CONTINUE`
- `VERIFY`
- `RETRY`
- `REROUTE`
- `REQUEST_APPROVAL`
- `REQUEST_CLARIFICATION`
- `COMPLETE`
- `FAIL`

### Phase F — Verification

Confirm the requested outcome, reconcile provider state, verify material claims, expose unresolved gaps, and require receipts for consequential actions.

### Phase G — Delivery and Persistence

Deliver the final answer/artifact. Persist canonical state only under the persistence contract and only with an authorized, verifiable write.
