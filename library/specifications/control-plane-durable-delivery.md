# Control-plane and durable-delivery contract

- Record ID: `control-plane-durable-delivery`
- Output profile: `output.technical-spec`
- Format: Markdown
- Generated: `2026-10-17T23:21:54+06:00`
- Status: saved locally; verification evidence is the repository path plus the reported SHA-256 checksum

## Outcome

ATLAS plans before execution, pauses dependent work for material clarification, displays a compact control plane for every prompt, and routes each delivered output to a profile-defined canonical-library collection and supported format.

## Dashboard fields

Every dashboard includes timestamp, measured duration, safe input summary, public processing summary, output summary, goal, task, playbook, frameworks, SOP, output profile, plan status, clarification status, progress, active stage and unit, quality, blocker or approval, and library delivery state.

Processing is an auditable stage-and-action summary. It does not expose private chain-of-thought or hidden reasoning. Input is summarized and minimized rather than copied when it may contain sensitive information.

## Execution gates

- Every prompt has a plan. L0 work uses one implicit work unit.
- Execution requires a `READY` plan.
- Material clarification must be `NOT_REQUIRED` or `RESOLVED` before dependent execution.
- One user-visible atomic work unit is active at a time.

## Library delivery

Output profiles route content to `answers`, `analyses`, `decisions`, `research`, `execution`, `specifications`, `data`, or `artifacts`. Each supported format has a declared filename extension.

Delivery states are:

- `READY`: target resolved; durable write not yet proven.
- `SAVED`: a validated adapter receipt records the exact location, SHA-256 checksum, byte count, and verification timestamp after write/read-back verification.
- `BLOCKED`: policy, authorization, or sensitivity prevents persistence.
- `CAPABILITY_UNAVAILABLE`: no durable storage adapter is accessible.

ATLAS never claims `SAVED` merely because text appeared in a conversation.

## Verification

- Unit tests: 42 passed.
- Conformance tests: 14 passed.
- Regression tests: 7 passed.
- Repository validation: 46 structured files passed.
