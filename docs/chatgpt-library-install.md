# ChatGPT Library installation and update

ATLAS-OS may be cached in ChatGPT Library for routine execution so that normal startup does not depend on refetching the private GitHub repository.

## Authority and provenance

The repository remains the source-development and release origin. The installed Library copy is a pinned runtime snapshot and must retain provenance to the exact Git commit from which it was built.

Within a verified installed snapshot, authority remains:

1. `atlas-os.yaml`
2. referenced normative specifications under `spec/`
3. schemas and registries
4. surface integration contracts
5. active migration controls

A Library snapshot must never invent a version or release state that differs from `atlas-os.yaml`.

## Main-branch snapshot artifact

Every successful push to `main` runs the full validation workflow and then builds the deterministic package with:

```bash
python tools/package/build_release.py . dist
```

The workflow uploads one Actions artifact with the stable name:

```text
atlas-os-main-snapshot
```

The artifact contains:

- `atlas-os-<version>.zip`
- `atlas-os-<version>.tar.gz`
- `atlas-os-<version>.manifest.json`
- `SHA256SUMS`

The package manifest records the source commit and payload checksums. This artifact is a transport snapshot, not a GitHub release and not evidence that the candidate has reached `RELEASED` state.

## ChatGPT update procedure

When the user explicitly asks to install, update, or synchronize ATLAS-OS:

1. Resolve the latest successful `Validate ATLAS-OS` workflow run for a push to `main`.
2. Record that run's head commit SHA.
3. Retrieve the `atlas-os-main-snapshot` artifact from that run.
4. Verify `SHA256SUMS` for the packaged files.
5. Read `atlas-os-<version>.manifest.json` and require its `source_commit` to equal the workflow run head SHA.
6. Open the packaged repository and resolve the version only from `atlas-os.yaml`.
7. Install or replace the ChatGPT Library runtime snapshot while preserving the previous installation receipt and replacement lineage.
8. Perform Library read-back verification before reporting the new snapshot as saved or active.

Do not poll GitHub during ordinary ATLAS startup. Treat the installed Library snapshot as current until the user explicitly reports an update or requests synchronization.

## Failure handling

Do not silently substitute an older GitHub release when the requested source is `main`. If the expected `atlas-os-main-snapshot` artifact is unavailable, report that update transport is unavailable and either use the exact repository files from the requested commit or rerun the `main` validation workflow. Never claim a Library update succeeded without source-commit verification and durable read-back evidence.

## Security and retention

The workflow uses commit-pinned GitHub Actions. Snapshot artifacts are retained for 90 days. An update creates a fresh successful `main` run and therefore a fresh artifact; routine operation continues from the already-installed Library copy and does not depend on artifact retention.
