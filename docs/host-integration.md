# Host Integration

ATLAS is host-neutral. ChatGPT, Hermes Agent, and other systems are adapters that expose capabilities.

Every adapter must:

1. initialize Mission Control and Control Plane before substantive execution;
2. expose only capabilities actually available in that session;
3. render the compact ATLAS state when material;
4. preserve approval boundaries;
5. return provider results to ATLAS;
6. report unavailable capabilities rather than pretending execution occurred.

Host-specific UI, tool names, storage, browser mechanics, and connector APIs remain adapter concerns. They must not change the core three-step preprocessing flow or ATLAS authority model.

The reference adapters live in `integrations/chatgpt.yaml`, `integrations/hermes-agent.yaml`, and `integrations/generic-host.yaml`.
