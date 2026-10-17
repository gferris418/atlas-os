# ATLAS-OS rc.7 release-readiness record

## Control plane

- Timestamp: `2026-10-18T00:01:01+06:00`
- Duration: unavailable from the host timer; no estimate substituted.
- Input: Fix the pending audit issues and make ATLAS-OS ready for ChatGPT usage.
- Goal: Produce a secure, reproducible, version-bound ChatGPT release candidate without fabricating external conformance evidence.
- Task: Remediate AUD-001 through AUD-006, verify the integrated candidate, and prepare independent host verification.
- Playbook: Regression-first remediation.
- Frameworks: ATLAS execution spine; NIST SSDF SP 800-218; SLSA build-integrity principles; CWE-20, CWE-59, and CWE-345.
- SOP: Plan → reproduce → patch → focused verify → independent review → full verify → persist → deliver.
- Output: ATLAS-OS `2.0.0-rc.7` candidate changes and this execution record.
- Quality: Local gates PASS; independent host gates PENDING.

## Outcome

Every code-level finding from the 2026-10-17 audit is remediated and locally verified. ATLAS-OS `2.0.0-rc.7` is ready for practical use through the version-bound ChatGPT compatibility profile at `integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md`.

Stable `v2.0.0` release status remains on HOLD because `MIG-029`, `MIG-037`, and `DTIF-RECONCILIATION` require evidence that cannot be truthfully generated inside this repository session. `MIG-029` is now `IN_PROGRESS` with local readiness evidence. The exact external procedure is recorded in `integrations/chatgpt/RELEASE-VERIFICATION.md`.

## Remediation map

| Finding | Resolution | Evidence |
|---|---|---|
| AUD-001 release identity | Publication requires an exact manifest tag; stable tags also require stable manifest state and no open blockers | Unit test plus rejected `v2.0.0` negative build |
| AUD-002 filesystem escape | Directory-descriptor-relative, no-follow traversal; root/parent identity re-walk; cleanup on detected swap | Root, nested, post-construction, parent-swap, and move-outside/symlink-back tests |
| AUD-003 false completion | Unknown states are rejected and stalled non-complete plans cannot return completion | Planning regression tests |
| AUD-004 duplicate IDs | Duplicate work-unit identifiers are rejected before graph construction | Planning regression test |
| AUD-005 timestamp conflict | Supplied timestamps require an offset consistent with the declared IANA timezone | Runtime and adapter regression tests |
| AUD-006 mutable supply chain | Actions are commit-pinned; universal dependency graph is hash-locked; CI audits dependencies; Dependabot is configured | Validator, locked download, and local `pip-audit` |

## Security-finding closure

- Outcome: `fixed`.
- Vulnerable path: a caller constructed `FileSystemLibraryAdapter` over a symlinked or swapped logical library tree, and path-based resolution could create a canonical output outside the workspace.
- Invariant: every newly published file remains reachable only through the unchanged, real-directory library path beneath the configured workspace; no symlink component is followed.
- Patch strategy: retain a workspace directory descriptor, traverse each component with `O_NOFOLLOW`, publish relative to the held parent descriptor, re-walk every component after publication, compare directory device/inode identity, and remove the newly published file before failing if identity changed.
- Legitimate behavior retained: ordinary writes, read-back and SHA-256 receipts, idempotent same-content retries, conflicting-overwrite rejection, and surface delivery all pass. An identical retry no longer requires permission to create a temporary file.
- Original issue no longer reproduces: all five symlink/swap focused tests pass and no probe leaves a file in the outside target.
- Compatibility: the reference filesystem adapter fails closed where secure no-follow directory operations are unavailable; another platform adapter must provide equivalent guarantees.

## Verification

- Unit: 54 passed.
- Conformance: 14 passed.
- Regression: 7 passed.
- Integration: 7 passed, including the ChatGPT bootstrap profile.
- Total: 82 passed.
- Repository validator: PASS, 47 structured files.
- Python compile: PASS.
- Undefined-name/static correctness (`ruff --select F`): PASS.
- Hash-locked dependency download: PASS.
- Dependency vulnerability audit: PASS, no known vulnerabilities.
- Release-tag negative test: PASS; `v2.0.0` was rejected against manifest `v2.0.0-rc.7`.
- Clean temporary candidate package: PASS twice with byte-identical checksums.

## Remaining external gates

1. Execute `integrations/chatgpt/RELEASE-VERIFICATION.md` in a genuinely fresh ChatGPT chat and ChatGPT Work session and attach approved evidence to `MIG-029`.
2. Verify control revision `chatgpt-bootstrap-2026-10-17-r1` independently on ChatGPT, Codex, and Work and attach evidence to `MIG-037`.
3. Supply and reconcile authoritative DTIF source data, or make a separately reviewed governance decision about that migration; absence of data is not closure evidence.
4. Commit the reviewed changes before building the final source-commit-bound archives. Publication, tagging, committing, and pushing were not performed by this remediation.
