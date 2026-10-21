# Hermes Agent release verification

This is the human companion to the authoritative machine verification contract at `integrations/hermes-agent/release-verification.yaml`. Use it in a genuinely fresh Hermes Agent session. Repository-local tests cannot replace independent host evidence. If this document and the YAML contract disagree, the schema-valid YAML contract governs verification execution.

## Test identity

- ATLAS version: `2.0.2-rc.3`
- Control revision: `atlas-bootstrap-2026-10-22-r7`
- AI discovery manifest: `atlas-ai.yaml`
- Skill artifact: `.agents/skills/atlas-os/SKILL.md`

## Procedure

1. Start Hermes Agent inside a fresh checkout with no earlier ATLAS conversation context.
2. Resolve the repository through `atlas-ai.yaml`, review the project skill, and run `hermes skills trust` for the checkout.
3. Execute every check in `integrations/hermes-agent/release-verification.yaml` and retain all required evidence fields.
4. Record unavailable host capabilities as unavailable; do not reinterpret them as successful actions or as failures of unrelated core semantics.
5. Do not translate checklist publication, local tests, or repository readiness into `PASS` for `MIG-037`.

## Closure rule

Hermes evidence can satisfy only the Hermes-scoped criteria and evidence requirements declared by `MIG-037`. The migration remains blocked until `MIG-029` is closed and independent current-revision evidence exists for every required supported surface.
