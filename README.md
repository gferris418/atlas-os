# ATLAS-OS

ATLAS-OS is a portable operating framework for governed AI work. It sits between user intent and the capabilities supplied by ChatGPT, Hermes Agent, or another host. ATLAS owns orchestration, routing, approvals, provider reconciliation, verification, classification governance, and persistence authority.

**Current release:** `3.0.2`

## Core invariant

> **When ATLAS is active, every user prompt enters Mission Control first. ATLAS governs. Providers execute bounded capabilities. Every provider returns to ATLAS. The user retains authority over consequential actions.**

ARGUS is the ATLAS-governed **360° Business Intelligence playbook** exposed through the `intelligence_collection` mechanism. It is not a peer operating system and it is not the underlying search/MCP/plugin/database provider. ATLAS selects and authorizes the actual capabilities and providers used for an ARGUS mission; ARGUS applies the intelligence doctrine inside the approved mission and returns its package to ATLAS.

## Runtime

```text
User / Event
    -> Mission Control [FIRST GOVERNANCE GATE]
    -> Control Plane
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
    -> Provider / playbook result returns to ATLAS
    -> Reassess / verify / reroute
    -> Deliver / persist
```

Mission Control runs before preprocessing whenever ATLAS is active. It is a governance entry gate, **not a fourth preprocessing step**. Preprocessing remains **exactly three steps**: Understand + Normalize, Minimal Domain Framing, Route. Planning, approvals, execution, evidence review, verification, persistence, and delivery are governed controls after routing; they are not additional preprocessing stages.

ChatGPT and other hosts may load ATLAS by relevance or explicit selection. The repository therefore guarantees Mission Control-first behavior **once ATLAS is active**, but does not claim universal host-level prompt injection when ATLAS has not been loaded.

## Classification standards registry

ATLAS maintains a versioned reference registry for external classification systems used in routing, research, procurement, supplier matching, analytics, and operational tagging. Domain, sector, industry, economic activity, product, capability, procurement category, trade classification, occupation, geography, and compliance/regulatory classification remain distinct concepts.

The registry preserves historical editions, authoritative provenance, lifecycle state, licensing/storage constraints, and directional crosswalks. `CANDIDATE` discoveries are proposals only and never become canonical automatically. Classification is context and indexing evidence; by itself it does not prove customs treatment, legal compliance, procurement eligibility, sanctions status, licensing, or regulatory approval.

## Repository

```text
atlas-os/
├── atlas-ai.yaml            # AI discovery entrypoint
├── atlas-os.yaml            # product/release authority
├── governance.yaml          # authority and change rules
├── plugin.json              # portable plugin manifest
├── skills/                  # packaged host skills
├── spec/                    # durable normative contracts
├── schemas/                 # public interchange/reference schemas
├── registries/              # capabilities, providers, surfaces, classifications
├── integrations/            # ARGUS, hosts, deployment profiles
├── atlas_runtime/           # compact framework reference runtime
├── tests/                   # unit, conformance, integration
├── tools/validate.py        # repository contract validator
└── docs/                    # GitBook-ready human documentation
```

Business-domain state machines such as bid preparation, project delivery, milestone acceptance, invoicing, payments, and accounting do not belong in `atlas_runtime`. ATLAS governs the permissions, routing, approvals, evidence acceptance, persistence authorization, and external actions around those processes; deployment systems and domain playbooks hold the domain semantics.

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

ATLAS enters Mission Control first, then routes this request to `ARGUS` and stops at `AWAITING_APPROVAL` until explicit `ARGUS_ACTIVATION` approval is supplied.

## Documentation

Human documentation is under [`docs/`](docs/README.md), including the [Classification Standards Registry](docs/classification-standards.md). GitHub is the source of truth for machine contracts and implementation; GitBook is the published human-readable projection.
