# ATLAS-OS

ATLAS-OS is a portable operating framework for governed AI work. It sits between user intent and the capabilities supplied by ChatGPT, Hermes Agent, or another host. ATLAS owns orchestration, routing, approvals, provider reconciliation, verification, and persistence authority.

**Current release:** `3.0.0`

## Core invariant

> **ATLAS governs. Providers execute bounded capabilities. Every provider returns to ATLAS. The user retains authority over consequential actions.**

ARGUS is the provider for structured `intelligence_collection`; it is not a peer operating system and cannot self-activate or choose the next ATLAS step.

## Runtime

```text
User / Event
    -> Mission Control + Control Plane
    -> Understand + Normalize
    -> Minimal Domain Framing
    -> Route
         -> No tool / direct answer
         -> Direct search
         -> Deep research
         -> ARGUS
         -> Specialist
         -> Connected source
         -> Code execution
         -> External action
         -> Multi-capability
    -> Provider result returns to ATLAS
    -> Reassess / verify / reroute
    -> Deliver / persist
```

Preprocessing is **exactly three steps**. Planning, approvals, execution, evidence review, verification, persistence, and delivery are governed controls after routing; they are not additional preprocessing stages.

## Repository

```text
atlas-os/
├── atlas-ai.yaml            # AI discovery entrypoint
├── atlas-os.yaml            # product/release authority
├── governance.yaml          # authority and change rules
├── spec/                    # 11 durable normative contracts
├── schemas/                 # 6 public interchange schemas
├── registries/              # capabilities, providers, surfaces
├── integrations/            # ARGUS, hosts, deployment profiles
├── atlas_runtime/           # compact reference runtime
├── tests/                   # unit, conformance, integration
├── tools/validate.py        # repository contract validator
└── docs/                    # GitBook-ready human documentation
```

Historical release diaries, migration logs, completed plans, compatibility aliases, generated libraries, and superseded registries are intentionally not active repository content. Git history and GitHub Releases provide history.

## Quick start

```bash
python -m pip install -r requirements.txt
python -m atlas_runtime --input request.json --format json
python -m unittest discover -s tests/unit -v
python -m unittest discover -s tests/conformance -v
python -m unittest discover -s tests/integration -v
python tools/validate.py .
```

Example request:

```json
{
  "objective": "Build a dossier on ST Engineering for Bangladesh opportunities.",
  "host": "chatgpt",
  "approvals": []
}
```

ATLAS will route this to `ARGUS` but stop at `AWAITING_APPROVAL` until explicit `ARGUS_ACTIVATION` approval is supplied.

## Documentation

Human documentation is under [`docs/`](docs/README.md). GitHub is the source of truth for machine contracts and implementation; GitBook is the published human-readable projection.
