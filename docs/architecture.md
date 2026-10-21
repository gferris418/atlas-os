# Architecture

ATLAS-OS is a normative execution-governance core surrounded by surface adapters. The core owns context, completeness, governed domain classification, domain-framework alignment, planning, routing, evidence, approval, output profiles, verification, persistence, versioning, capability admission, and user-visible execution state. Adapters use native surface capabilities and map them into those contracts without copying or changing them.

```text
USER INTENT
     |
     v
+-------------------------------+
|         ATLAS-OS CORE         |
| context / completeness        |
| standards / planning          |
| routing / evidence            |
| capability admission          |
| approval / verification       |
| persistence / state           |
+---------------+---------------+
                |
       +--------+--------+
       |                 |
       v                 v
  CONTROL PLANE      ASSURANCE
  routing            injection boundaries
  provider choice    provider risk review
  phase selection    capability evaluation
       |                 |
       +--------+--------+
                |
       +--------+-------------------+
       |                            |
       v                            v
  EXECUTION / KNOWLEDGE        FORESIGHT / LEARNING
  host tools                  horizon scan
  specialist skills          evidence reconciliation
  canonical persistence      scenarios / red-team
  memory integrity           forecast vintages
                             outcome calibration
                |
                v
      +---------+---------+---------+-------------+
      |         |         |         |             |
    Codex    ChatGPT     Work   Hermes Agent   Any AI host
```

"OS" describes the governed execution layer around an AI agent; it does not describe the host machine's operating system. The core is independent of model provider, agent framework, desktop OS, and deployment location. Known adapters document concrete capability mappings, while the validated generic surface seam permits new AI hosts without changing core semantics.

## Provider-independent capabilities

ATLAS registers semantic capabilities rather than embedding provider brands into core semantics. A skill, plugin, model, connector, or external framework is a provider of one or more capabilities and remains subordinate to [`spec/capability-admission.yaml`](../spec/capability-admission.yaml).

Availability is not admission. Installation is not trust. A clean static security scan is not certification. A static quality review is not a measured benchmark. Provider-specific accuracy, cost, latency, or reliability claims remain unverified until tested in the target runtime.

The current capability set includes governed admission, untrusted-content assurance, canonical-memory integrity, forecasting/foresight governance, and learning/calibration. Named third-party systems may serve as reference providers or conditional adapters, but they do not become core dependencies without an explicit integration contract, runtime availability, security review, fallback semantics, and regression evidence.

## Forecasting and foresight

ATLAS owns the canonical forecast record and learning loop. Replaceable forecast providers may contribute horizon scanning, evidence reconciliation, scenario construction, adversarial review, update logic, and calibration, but must preserve forecast vintages and cannot rewrite prior predictions after outcomes become known.

The baseline provider-independent forecast path is:

```text
HORIZON SCAN
    -> EVIDENCE / CONTRADICTIONS
    -> ASSUMPTIONS / SCENARIOS
    -> FORECAST REGISTER
    -> ADVERSARIAL REVIEW
    -> FROZEN VINTAGE
    -> NEW EVIDENCE / UPDATE
    -> OUTCOME RESOLUTION
    -> CALIBRATION / ERROR ATTRIBUTION
    -> FRAMEWORK LEARNING
```

A sophisticated forecasting process is not evidence of forecasting accuracy. Accuracy requires prospective frozen predictions, predeclared resolution rules, suitable comparators, and enough resolved observations to support calibration claims.

## Specialist-domain boundary

Specialist domain systems remain nested methods, not parallel operating systems. Before specialist routing, ATLAS displays a digest-bound preview of what will be done, how, by which provider, with what permission and data scope, and under which fallback and unresolved gates. ARGUS, for example, consumes the ATLAS domain-context handoff only after that exact proposal is approved, performs government/public-sector opportunity intelligence, and returns domain analysis and proposed actions. It does not own the ATLAS execution spine, plan, approval state, or final delivery.

Specialists may internally use admitted providers such as research, procurement, company, trade, legal, financial, capture, or proposal systems only within their registered domain contract. Provider identity must never become the canonical identity of an ATLAS or specialist-domain record.

The executable `atlas_runtime` package is a conformance reference, not a second source of truth. Its behavior is tested against the declarative specifications and invariants.

The dependency direction is manifest -> core specs -> schemas/registries -> adapters -> execution. Legacy material is outside the active resolution path.
