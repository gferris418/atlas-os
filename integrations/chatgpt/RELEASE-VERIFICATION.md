# ChatGPT release verification

This is the human companion to the authoritative machine verification contracts:

- `integrations/chatgpt/release-verification.yaml`
- `integrations/work/release-verification.yaml`

Use them in a genuinely fresh ChatGPT conversation and, separately, in ChatGPT Work. Repository-local tests cannot replace independent host evidence. If this document and the YAML contracts disagree, the schema-valid YAML contract governs verification execution.

## Test identity

- ATLAS version: `2.0.2-rc.4`
- Control revision: `atlas-bootstrap-2026-10-22-r8`
- AI discovery manifest: `atlas-ai.yaml`
- ChatGPT instruction artifact: `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`

## Procedure

1. Start a new session with no earlier ATLAS conversation context.
2. Load the repository through `atlas-ai.yaml` or apply `ATLAS-CHATGPT-INSTRUCTIONS.md` when repository discovery is unavailable.
3. Execute every check in `integrations/chatgpt/release-verification.yaml` and retain the required evidence fields.
4. Confirm the triage-first behavior explicitly: a plain current-tender lookup remains `GENERAL_SEARCH` with no ARGUS specialist, while the specified opportunity-assessment/ranking/monitoring prompt resolves to `INTELLIGENCE` with specialist `ARGUS`.
5. Repeat independently in ChatGPT Work using `integrations/work/release-verification.yaml`.
6. Do not translate repository readiness into `PASS`; only observed host behavior with retained evidence can satisfy `MIG-029`.
7. After `MIG-029` is closed, execute the current control-revision checks for ChatGPT, Codex, Work, and Hermes Agent and attach independent references to `MIG-037`.

## Closure rule

`MIG-029` may close only when every machine acceptance criterion in `migration/MIG-029.yaml` is `PASS`, each criterion links to retained evidence IDs, and that evidence is independently observed for the current product version and control revision. `MIG-037` remains blocked until its dependency and its own independent cross-surface criteria are satisfied.
