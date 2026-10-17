# Contributing

1. Branch from `main` and classify the proposed change using `GOVERNANCE.md`.
2. Preserve `atlas-os.yaml` as the sole product version authority.
3. Update specifications, schemas, registries, tests, and migration records together when their contracts change.
4. Run every validation command documented in `README.md`.
5. Explain evidence, compatibility impact, open blockers, and required approvals in the pull request.

When `requirements.txt` changes, regenerate the universal hash lock with `uv pip compile requirements.txt --generate-hashes --universal --output-file requirements.lock`, review the resolution, and run the locked install plus vulnerability audit before committing it.

Do not close migration controls, weaken assertions, or change release state merely to obtain a green build.

