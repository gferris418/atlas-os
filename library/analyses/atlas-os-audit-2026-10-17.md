# ATLAS-OS audit — 2026-10-17

## Control plane

- Timestamp: 2026-10-17T23:46:38+06:00
- Duration: 2 minutes 19 seconds
- Input: Audit the `atlas-os` repository at `c42eb2ac379cf3264fdfc354ee4c70c8481068b4`.
- Goal: Assess correctness, security boundaries, release integrity, verification evidence, and readiness without changing product code.
- Task: Repository-wide, source-backed audit of the `main` branch.
- Playbook: Inventory → threat-boundary review → independent verification → focused negative probes → finding validation → report.
- Frameworks: ATLAS execution spine; NIST SSDF SP 800-218 secure-development principles; SLSA build-integrity principles; CWE weakness classification. These are assessment lenses, not certification claims.
- SOP: Plan → inspect → test → reproduce → rank → persist → deliver.
- Output: This Markdown audit record.
- Quality gate: PARTIAL.

## Executive verdict

ATLAS-OS `2.0.0-rc.6` is a credible release candidate with a coherent specification, executable reference seams, strong local validation, and reproducible packaging. It is **not ready for a stable `v2.0.0` release**. The audit found no critical or high-severity issues, three medium-severity issues, and three low-severity issues. In addition, the repository truthfully declares three unresolved release blockers.

Local verification passed: 45 unit tests, 14 conformance tests, 7 regression tests, 5 integration tests, Python byte-compilation, dependency consistency, and validation of 46 structured files. Two independent package builds produced identical SHA-256 hashes.

## Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| AUD-001 | Medium | Release automation does not bind the Git tag to the manifest version or release state | Validated |
| AUD-002 | Medium | A symlink used as the configured library root defeats workspace containment | Reproduced |
| AUD-003 | Medium | Surface startup accepts invalid terminal/task states and can report `Plan complete` at 0% | Reproduced |
| AUD-004 | Low | `build_plan` silently collapses duplicate task identifiers | Reproduced |
| AUD-005 | Low | Caller-supplied timestamps are not validated against RFC 3339 or the declared timezone | Reproduced |
| AUD-006 | Low | CI dependencies are version-tag pinned rather than immutable-digest pinned, and Python requirements have no hashes | Hardening gap |

### AUD-001 — Release tag is not bound to manifest truth

The release workflow runs for every `v*` tag, builds the version named in `atlas-os.yaml`, and publishes those artifacts under `GITHUB_REF_NAME`. It never checks that the tag equals `v${product.version}`. It also infers prerelease status only from whether the tag contains a hyphen. A mistakenly pushed `v2.0.0` tag while the manifest remains `2.0.0-rc.6` would therefore create a stable-looking GitHub release containing RC6 artifacts despite open blockers.

- Evidence: `.github/workflows/release.yml:3-5`, `.github/workflows/release.yml:21-34`, `atlas-os.yaml:5-8`, `atlas-os.yaml:21-26`.
- Impact: release identity and governance claims can diverge from packaged content.
- CWE mapping: CWE-345, insufficient verification of data authenticity.
- Recommendation: before packaging, fail unless the tag exactly matches the manifest version; reject stable tags unless manifest status/channel and blockers satisfy stable-release policy.

### AUD-002 — Configured library-root symlink escapes the workspace

`FileSystemLibraryAdapter` resolves the configured library root and then treats that resolved path as the containment boundary. If `<workspace>/library` is already a symlink to a writable directory outside the workspace when the adapter is constructed, writes outside the workspace pass the containment check. A focused probe created `outside/answers/escaped.md` through such a root symlink. Existing tests cover a symlink below the library root, but not the root itself.

- Evidence: `atlas_runtime/persistence.py:19-35`, `atlas_runtime/persistence.py:38-64`, `tests/unit/test_runtime.py:398-413`.
- Impact: an attacker able to control workspace layout can cause creation of new files outside the declared workspace. Existing files are not overwritten by the normal write path.
- CWE mapping: CWE-59, improper link resolution before file access.
- Recommendation: require the resolved storage root to remain beneath the resolved workspace root and reject a symlinked configured root; for hostile concurrent filesystems, use directory-descriptor-relative operations with no-follow semantics.

### AUD-003 — Invalid task state can produce false completion

`SurfaceAdapter.start_prompt` accepts raw task dictionaries. `select_next_work_unit` recognizes only `ACTIVE`, `PENDING`, and `COMPLETED`, but does not reject unknown states or distinguish legitimate `BLOCKED`, `FAILED`, and `CANCELLED` terminal outcomes. With one task having status `TYPO`, startup returned active unit `Plan complete`, stage `PLANNING`, and progress `0`.

- Evidence: `atlas_runtime/adapters.py:28-52`, `atlas_runtime/runtime.py:388-412`, `schemas/task.schema.json:7-17`.
- Impact: control-plane state can incorrectly imply successful plan completion, weakening execution governance and operator decisions.
- CWE mapping: CWE-20, improper input validation.
- Recommendation: validate task state at the adapter boundary and return explicit blocked/failed/cancelled outcomes; reserve `Plan complete` for a non-empty plan in which every work unit is `COMPLETED`.

### AUD-004 — Duplicate task identifiers are collapsed

`build_plan` constructs a dictionary keyed by task ID without first checking uniqueness. A two-task input with the same ID returned a one-item plan. `select_next_work_unit` does reject duplicates, so the integrated surface path eventually fails, but the public planning seam itself is lossy and inconsistent.

- Evidence: `atlas_runtime/runtime.py:344-366`, compared with duplicate validation at `atlas_runtime/runtime.py:388-391`.
- Recommendation: reject duplicates before graph construction and add a direct unit test for `build_plan`.

### AUD-005 — Timestamp and timezone can disagree

When a timestamp is supplied, `prepare_library_record` stores it without parsing it or checking it against `timezone_name`. A probe accepted timestamp `2026-01-01T00:00:00+06:00` with timezone `UTC`. `create_dashboard` similarly accepts an arbitrary supplied timestamp. Schema validation catches some malformed values only if callers perform that separate step, but the persistence adapter can save records without it.

- Evidence: `atlas_runtime/runtime.py:510-515`, `atlas_runtime/runtime.py:518-579`, `atlas_runtime/runtime.py:602-677`.
- Impact: audit records may carry ambiguous or contradictory temporal provenance.
- Recommendation: parse supplied timestamps, require an offset, and either normalize to or verify consistency with the declared IANA timezone.

### AUD-006 — Supply-chain references are mutable

GitHub Actions are referenced by moving major-version tags, and Python requirements are exact-version pinned but not hash-locked. This is a hardening gap rather than evidence of compromise.

- Evidence: `.github/workflows/validate.yml:15-20`, `.github/workflows/release.yml:14-21`, `requirements.txt:1-2`.
- Recommendation: pin Actions to reviewed commit SHAs and use a hash-locked dependency workflow with automated update review and vulnerability scanning.

## Verified controls

- Product authority is centralized in `atlas-os.yaml`; the validator rejects competing product-version declarations.
- Release blockers are represented as machine-readable migration records and stable release status is rejected while declared blockers are open.
- Planning enforces dependency order and a one-active-work-unit limit on valid task states.
- High-impact actions require scoped approval in the reference runtime.
- Canonical persistence uses temporary files, file sync, no-overwrite publication, directory sync, read-back verification, and SHA-256 receipts for ordinary non-hostile paths.
- Schema and registry validation is broad, deterministic, and covered by repository tests.
- Packaging rejects tracked dirty state and is reproducible. Both audit builds produced:
  - tar.gz: `889da28dc0507458549e2d99b09f604385af3f23d496bb86a8b8de268dc9483e`
  - zip: `f42ab048f9e15a0493c09a0c1ca08ebd60ea9cb39e7ebebcee5216f43acc5988`
  - manifest: `9c6c5442c5d287949ff6a21217816cb4bcff0d8563293401472432758c0872aa`

## Readiness and coverage gaps

- `MIG-029`, `MIG-037`, and `DTIF-RECONCILIATION` remain open and release-blocking.
- Hosted GitHub Actions results, branch protection, and release state could not be independently read because GitHub returned `403 Forbidden` from this environment.
- A dependency-vulnerability scanner was not installed; `pip check` passed, but that detects consistency rather than known vulnerabilities.
- No concurrency/crash-injection stress test covers the persistence adapter.
- No independent live proof currently demonstrates ChatGPT, Codex, and Work behavior across fresh sessions.
- The security-scan cloud package exposed its main procedure but not its referenced preflight/core resources or finalizer, and no host scan service was available. Security coverage therefore used a source-backed prompt-only review rather than a sealed Codex Security report.

## Recommended atomic remediation order

1. Bind release tag, manifest version, status, channel, and blocker state in CI; add negative release tests.
2. Reject a symlinked or out-of-workspace storage root; add root-symlink and race-oriented tests.
3. Validate task states at surface startup and distinguish completion from blocked/failed/cancelled plans.
4. Reject duplicate IDs in `build_plan`.
5. Validate timestamp/zone consistency at runtime boundaries.
6. Pin CI actions immutably and add hash-locked dependency vulnerability scanning.
7. Complete the three declared migration proofs before stable release.

## Audit disposition

- Local candidate quality: PASS.
- Security boundary quality: PARTIAL.
- Release integrity: PARTIAL.
- Stable-release readiness: HOLD.
- Product-code changes made by this audit: none.

## Subsequent remediation

The code-level findings in this rc.6 audit were remediated in the `2.0.0-rc.7` candidate. See `library/execution/atlas-os-rc7-release-readiness.md` for the implementation, security closure, and fresh verification record. The independent host and DTIF blockers remain open.
