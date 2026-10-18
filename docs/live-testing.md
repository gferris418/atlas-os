# Live runtime testing

ATLAS exposes one local executable boundary over the same `execute()` function
used by its surface adapters. It selects the next governed atomic unit; it does
not perform host-specific work for that unit.

From the repository root:

```bash
python -m pip install --require-hashes -r requirements.lock
python -m atlas_runtime --input examples/execution-request.json
```

The default is a compact four-line text control plane. JSON may also be piped
through stdin:

```bash
python -m atlas_runtime < examples/execution-request.json
```

For a machine consumer, NDJSON emits one accepted event and one result event.
Each line is flushed independently:

```bash
python -m atlas_runtime --format ndjson < examples/execution-request.json
```

Exit code `0` means the request reached a valid ATLAS execution state. Invalid
JSON, missing fields, invalid work-unit state, or unreadable input returns exit
code `2` and a concise error on stderr without a traceback.

This command confirms the local execution seam. It does not prove fresh
ChatGPT or Work activation, durable host storage, branch protection, or a
stable production release. Those externally evidenced controls remain tracked
separately.
