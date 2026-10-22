# Contributing

ATLAS-OS keeps a deliberately small architecture surface. Changes should strengthen an existing contract before introducing a new one.

## Rules

1. Preserve the exact three-step preprocessing flow.
2. Keep ATLAS as the sole next-step and orchestration authority.
3. Treat tools, plugins, skills, connectors, models, and ARGUS as providers rather than architectural authorities.
4. Add or change observable behavior through tests first.
5. Keep organization-specific workflow/storage rules in deployment integrations.
6. Do not reintroduce migration diaries, release-candidate logs, compatibility aliases, generated libraries, or duplicate registries into the active tree.
7. Run all validation commands before requesting merge.

```bash
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/conformance -v
python -m unittest discover -s tests/integration -v
python tools/validate.py .
```
