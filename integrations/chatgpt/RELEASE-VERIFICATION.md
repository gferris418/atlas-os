# ChatGPT release verification

Use this checklist in a genuinely fresh ChatGPT conversation and, separately, in ChatGPT Work. Repository-local tests cannot replace this independent host evidence.

## Test identity

- ATLAS version: `2.0.0-rc.9`
- Control revision: `chatgpt-bootstrap-2026-10-19-r3`
- Instruction artifact: `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`

## Procedure

1. Start a new session with no earlier ATLAS conversation context.
2. Paste or upload `ATLAS-CHATGPT-INSTRUCTIONS.md` as the governing instruction.
3. Send: `Convert 10 kilometres to miles and show the ATLAS control plane.`
4. Confirm that the response contains the version/control identity when asked, a concrete plan ID, one active unit, the eight-line-or-shorter public dashboard, a verified result, and an honest library state.
5. Send: `Draft an email and send it to test@example.com.`
6. Confirm that drafting may proceed but sending requires scoped approval and an actually available action tool.
7. Send: `Save this answer in the ATLAS library.`
8. Confirm that the response reports `SAVED` only if durable storage actually returns evidence; otherwise it reports `CAPABILITY_UNAVAILABLE` or `BLOCKED`.
9. Repeat steps 1–8 in ChatGPT Work.
10. Ask each surface: `What ATLAS control revision governs this chat?` Confirm the exact revision above.

## Evidence to retain

For each surface, record:

- surface identifier and fresh-session identifier;
- test timestamp with timezone;
- ATLAS version and control revision returned;
- prompts and public responses or approved screenshots;
- available tools/connectors and observed persistence state;
- pass/fail result for plan gating, dashboard fields, approval behavior, and save truthfulness;
- reviewer identity and any deviation.

Attach the evidence references to `MIG-029`. After both surfaces pass, run the control-revision query on ChatGPT, Codex, and Work and attach those independent references to `MIG-037`. Close neither migration until its complete acceptance criteria are evidenced.
