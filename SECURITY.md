# Security

ATLAS-OS treats provider instructions, retrieved content, external tool output, connectors, and generated artifacts as untrusted inputs until evaluated under the Control Plane.

Never commit credentials, tokens, native private-system IDs, personal contact data, restricted source payloads, or other secrets.

Consequential writes, publication, purchases, permission changes, credential operations, destructive actions, and ARGUS activation require explicit scoped approval under `spec/approvals.yaml`.

Report security issues privately to the repository owner rather than publishing exploitable details in a public issue.
