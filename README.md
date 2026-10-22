# ATLAS-OS

ATLAS-OS is a portable operating framework for governed AI work. It sits between user intent and the capabilities supplied by ChatGPT, Hermes Agent, or another host. ATLAS owns orchestration, routing, approvals, provider reconciliation, quality governance, verification, classification governance, and persistence authority.

**Current release:** `3.0.3`

## Core invariant

> **When ATLAS is active, every user prompt enters Mission Control first. ATLAS governs. Providers execute bounded capabilities. Every provider returns to ATLAS. The user retains authority over consequential actions. Quality and decision utility come before performance.**

ARGUS is the provider for structured `intelligence_collection`; it is not a peer operating system and cannot self-activate or choose the next ATLAS step.

## Runtime

```text
User / Event
    -> Mission Control [FIRST GOVERNANCE GATE]
    -> Control Plane
    -> Understand + Normalize
    -> Minimal Domain Framing [assign Q0-Q5 required quality tier]
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
    -> Quality Gate
         -> PASS -> Final Verify
         -> CONTINUE -> targeted collection / analysis
         -> IRREDUCIBLE_GAP -> explicit gap disclosure + Final Verify
    -> Persist when authorized and durable
    -> Deliver
```

Mission Control runs before preprocessing whenever ATLAS is active. It is a governance entry gate, **not a fourth preprocessing step**. Preprocessing remains **exactly three steps**: Understand + Normalize, Minimal Domain Framing, Route. Required quality tier is derived inside Minimal Domain Framing. Planning, approvals, execution, evidence review, quality gating, verification, persistence, and delivery are governed controls after routing; they are not additional preprocessing stages.

## Quality-first optimization

ATLAS 3.0.3 uses six assurance tiers: `Q0` deterministic, `Q1` verified lookup, `Q2` normal analytical, `Q3` high-assurance research, `Q4` strategic decision-grade intelligence, and `Q5` critical maximum assurance with explicit stopping justification.

Performance is optimized **inside** the required quality tier. Caching, indexing, verified-state reuse, delta refresh, duplicate elimination, deterministic computation, and parallel independent retrieval may reduce latency and cost, but they may not lower the required tier or bypass evidence, verification, governance, approvals, or material uncertainty disclosure.

Provider confidence does not override mandatory quality gates. When reusable intelligence remains fresh, complete, non-contradictory, correctly resolved, and valid for the required tier, ATLAS may reuse it or request only a delta refresh. Otherwise it recollects what is necessary to satisfy the Quality Gate.

## FAST_TEXT and persistence

`FAST_TEXT` is the default compact status renderer for ordinary text surfaces. It shows deterministic stage progress, Mission Control state, Control Plane route, status, blockers, and next action. Rendering mode changes presentation only; it never changes research depth or quality requirements.

For deployments with an authorized durable-write capability, ATLAS can serialize one immutable Markdown audit event per completed user-assistant turn. The event contains the complete user-visible prompt, complete final user-visible response, allowlisted execution metadata, and integrity hashes. It excludes hidden chain-of-thought, system/developer instructions, credentials, temporary signed URLs, and raw secret-bearing tool payloads. Per-token persistence is prohibited.

A host without an authorized write or post-turn hook must report persistence as unavailable or pending rather than claiming continuous background persistence.

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
├── spec/                    # 14 durable normative contracts
├── schemas/                 # 9 public interchange/reference schemas
├── registries/              # capabilities, providers, surfaces, classifications
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
python -m atlas_runtime --input request.json --format text
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

ATLAS enters Mission Control first, assigns the required quality tier during Minimal Domain Framing, then routes this request to `ARGUS` and stops at `AWAITING_APPROVAL` until explicit `ARGUS_ACTIVATION` approval is supplied.

## Documentation

Human documentation is under [`docs/`](docs/README.md), including the [Classification Standards Registry](docs/classification-standards.md). GitHub is the source of truth for machine contracts and implementation; GitBook is the published human-readable projection.
