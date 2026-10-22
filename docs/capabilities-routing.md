# Capabilities and Routing

ATLAS routes by required capability, not by brand or tool name.

## Mechanisms

| Mechanism | Typical use |
| --- | --- |
| `NO_TOOL` | writing, transformation, reasoning from supplied context |
| `DIRECT_SEARCH` | current factual lookup or direct retrieval |
| `DEEP_RESEARCH` | multi-source research and synthesis |
| `ARGUS` | structured intelligence collection, entity/opportunity/supplier/stakeholder landscapes, monitoring |
| `SPECIALIST` | bounded specialist method or domain capability |
| `CONNECTED_SOURCE` | authorized internal/private source |
| `CODE_EXECUTION` | code, deterministic analysis, transformation |
| `EXTERNAL_ACTION` | sending, publishing, buying, changing external state |
| `MULTI_CAPABILITY` | task requires an explicit sequence or combination of capabilities |

## Direct search versus ARGUS

Use direct search/research when the task is primarily factual retrieval or analysis. Use ARGUS when ATLAS needs structured collection across targets, sources, identities, relationships, chronology, evidence gaps, or ongoing monitoring.

Examples:

- “Find the current Bangladesh Railway tenders” → `DIRECT_SEARCH`.
- “Explain Bangladesh Navy procurement regulations” → `DEEP_RESEARCH` or direct authoritative research.
- “Build a dossier on ST Engineering and its Bangladesh opportunity footprint” → `ARGUS`.
- “Forecast likely Navy procurements over 24 months” → `MULTI_CAPABILITY`: ARGUS may collect; ATLAS analyzes and forecasts.

ARGUS need never implies ARGUS permission.
