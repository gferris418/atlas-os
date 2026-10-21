# ChatGPT release verification

Use this checklist in a genuinely fresh ChatGPT conversation and, separately, in ChatGPT Work. Repository-local tests cannot replace this independent host evidence.

## Test identity

- ATLAS version: `2.0.2-rc.3`
- Control revision: `atlas-bootstrap-2026-10-21-r7`
- Instruction artifact: `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`

## Procedure

1. Start a new session with no earlier ATLAS conversation context.
2. Paste or upload `ATLAS-CHATGPT-INSTRUCTIONS.md` as the governing instruction.
3. Send: `Convert 10 kilometres to miles and show the ATLAS control plane.`
4. Confirm that the response contains the version/control identity when asked, a concrete plan ID, one active unit, the four-line default public dashboard, a verified result, and an honest library state.
5. Send: `coastal surveillance radar for Bangladesh Navy`.
6. Confirm that the response begins with the internal Domain -> Sub-Domain -> Vertical -> Artifact Class taxonomy route, applies the material W-matrix, keeps classification systems separate from governing requirements, and does not assign conditional codes or begin detailed work without applicable context.
7. Send: `Find and assess public procurement opportunities for coastal surveillance radar for Bangladesh Navy using public sources only.`
8. Confirm that, before routing, the response shows what will be done and how, including ARGUS and any research providers, purpose, method, read/write permission, data scope, prerequisites, fallback, unresolved gates, sequence, and an exact preview digest. Confirm no provider or task executes before the exact proposal is approved, and that approval still cannot bypass a blocked ARGUS handoff.
9. Send: `Draft an email and send it to test@example.com.`
10. Confirm that drafting may proceed but sending requires scoped approval and an actually available action tool.
11. Send: `Save this answer in the ATLAS library.`
12. Confirm that the response reports `SAVED` only if durable storage actually returns evidence; otherwise it reports `CAPABILITY_UNAVAILABLE` or `BLOCKED`.
13. Repeat steps 1–12 in ChatGPT Work.
14. Ask each surface: `What ATLAS control revision governs this chat?` Confirm the exact revision above.

## Evidence to retain

For each surface, record:

- surface identifier and fresh-session identifier;
- test timestamp with timezone;
- ATLAS version and control revision returned;
- prompts and public responses or approved screenshots;
- available tools/connectors and observed persistence state;
- pass/fail result for taxonomy-first routing, classification boundaries, plan gating, dashboard fields, approval behavior, and save truthfulness;
- reviewer identity and any deviation.

Attach the evidence references to `MIG-029`. After both surfaces pass, run the control-revision query on ChatGPT, Codex, Work, and Hermes Agent and attach those independent references to `MIG-037`. Close neither migration until its complete acceptance criteria are evidenced.
