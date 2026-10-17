# ATLAS canonical library

This directory is the repository-backed durable library for reusable ATLAS outputs. Logical collections are selected by the active output profile:

- `answers/`
- `analyses/`
- `decisions/`
- `research/`
- `execution/`
- `specifications/`
- `data/`
- `artifacts/`

An absent collection is created only when it receives an output. A file's existence alone does not prove verified delivery; adapters record a checksum, object version, commit, or equivalent durable-write receipt before reporting `SAVED`.

Do not store secrets, raw sensitive prompts, private chain-of-thought, or restricted material unless the destination and authorization are explicitly approved.
