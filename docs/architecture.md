# Architecture

ATLAS-OS is the single orchestration architecture. Hosts supply models and tools; providers supply capabilities; ARGUS supplies structured intelligence collection. None of them replaces the ATLAS Control Plane.

```text
User / Event
    |
    v
Mission Control
    |
    v
Control Plane
    |
    +--> Understand + Normalize
    +--> Minimal Domain Framing
    +--> Route
            |
            +--> No tool
            +--> Direct search
            +--> Deep research
            +--> ARGUS
            +--> Specialist
            +--> Connected source
            +--> Code execution
            +--> External action
            +--> Multi-capability
                    |
                    v
              Provider Result
                    |
                    v
                  ATLAS
            reassess / verify / reroute
                    |
                    v
              Deliver / Persist
```

## Six permanent layers

1. **Mission Control** — user objectives, approvals, scope, priority, pause/resume/abort.
2. **Control Plane** — state, policy, permissions, routing, provider selection, approvals, reconciliation, persistence authorization.
3. **Context Plane** — understand and normalize the whole request, then add only material domain framing.
4. **Capability Plane** — host-native capabilities, search, research, ARGUS, specialists, connectors, code, and external actions.
5. **Assurance Plane** — evidence governance, security, validation, and verification.
6. **Delivery Plane** — final output, persistence, receipts, and observability.

## Exactly three preprocessing steps

Preprocessing is always:

1. `UNDERSTAND_AND_NORMALIZE`
2. `MINIMAL_DOMAIN_FRAMING`
3. `ROUTE`

Planning, provider admission, approvals, execution, evidence review, verification, persistence, and delivery are governed execution controls, not additional preprocessing steps.

## Provider return rule

Every material provider return goes back to ATLAS. ATLAS decides whether to continue, verify, retry, reroute, request approval, request clarification, complete, or fail. A provider never selects its own next mission.
