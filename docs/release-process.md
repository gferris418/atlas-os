# Release process

The lifecycle is `DRAFT -> CANDIDATE -> VERIFIED -> RELEASED -> SUPERSEDED -> ARCHIVED`.

1. Complete implementation and required migrations.
2. Run unit, conformance, and regression suites.
3. Run repository validation.
4. Reconcile all release-blocking controls with evidence.
5. Build deterministic archives and inspect their manifest and checksums.
6. Commit the release state.
7. Create the matching semantic tag.
8. Publish the GitHub release and attach artifacts.

The stable `v2.0.0` tag is forbidden while any release-blocking control is open. Candidate artifacts use the exact identifier in `atlas-os.yaml`. Packaging does not imply acceptance, release, or publication.

Publication builds pass the triggering tag to `build_release.py --tag`. The build fails unless the tag exactly matches `v<manifest version>` and the manifest channel/status is compatible; a stable tag additionally fails while any declared release blocker is open.

