# ATLAS signing-key management

ATLAS uses Ed25519 attestations to authenticate control records crossing a
system boundary. The runtime verifies signatures and public-key lifecycle
metadata; the operator remains responsible for private-key custody and trusted
distribution of the public-key registry.

The normative machine contract is
[`schemas/signing-key-registry.schema.json`](../schemas/signing-key-registry.schema.json).
This runbook does not replace an organization's applicable security policy,
incident process, or regulatory requirements.

## Private-key custody

- Generate production keys with an approved HSM, KMS, or secrets platform that
  uses a cryptographically secure random source and supports Ed25519. Prefer a
  non-exportable key when the signing integration permits it.
- If an exportable 32-byte Ed25519 seed is unavoidable, store it only in an
  approved secret manager. Never commit it, place it in configuration or test
  fixtures, write it to logs, include it in dashboards, or transmit it in an
  issue or pull request.
- Restrict signing authority to the service identity and record classes that
  require it. Separate development and test keys from production keys.
- Treat the raw `private_key` argument accepted by `attest_control_record()` as
  an in-memory compatibility boundary, not as a recommendation to keep key
  material in application files. Python does not guarantee immediate memory
  zeroization; minimize the seed's lifetime and copies.

## Public-key admission

Before a key signs production records:

1. Assign a unique `key_id` and record the `Ed25519` algorithm and `ATLAS_OS`
   issuer.
2. Publish only the Base64-encoded public key in a schema-valid signing-key
   registry entry.
3. Set timezone-aware `activated_at` and `expires_at` values, an `ACTIVE`
   status, and the smallest necessary `allowed_record_classes` scope.
4. Record `supersedes` when the key replaces an earlier key.
5. Review the registry change through the protected repository workflow and
   distribute it through an authenticated, integrity-checked channel. Consumers
   should pin an immutable revision or digest; a mutable URL is not a trust
   anchor.
6. Confirm every consumer can resolve the new key with
   `verify_control_record_attestation_with_registry()` before production use.

The pinned-key-only `verify_control_record_attestation()` compatibility path
does not enforce activation, expiry, revocation, or record-class scope. It must
not replace registry-governed verification for production trust decisions.

## Planned rotation

1. Create a new key and registry entry before the old key expires.
2. Set an intentional overlap period in which both entries are `ACTIVE`, and
   set the new entry's `supersedes` field to the old key ID.
3. Distribute and read back the updated registry from every consumer.
4. Switch signing to the new key and verify a representative record at each
   boundary.
5. Stop using the old private key, change its registry status to `RETIRED`, and
   retain the public metadata required for lineage and audit.
6. Destroy or disable old private-key material according to the controlling
   retention policy and record the operator evidence.

Rotation cadence is policy- and risk-dependent. Set `expires_at` so rotation
can complete before expiry; expiry is a fail-closed control, not a reminder.

## Emergency revocation

On suspected compromise:

1. Stop signing with the affected key and prevent further access to its private
   material.
2. Change its registry status to `REVOKED` through the authorized emergency
   change path and publish the updated immutable registry revision.
3. Invalidate consumer caches and verify that the revoked key now fails closed.
4. Activate a replacement key with the minimum required scope and distribute it
   using the admission procedure above.
5. Identify records signed by the affected key, assess their exposure window,
   and reissue or invalidate them according to the owning contract.
6. Preserve incident, approval, distribution, and verification evidence. Do
   not rewrite historical records to conceal the revoked key.

The current runtime rejects a registry entry whose status is not `ACTIVE`.
Systems requiring historical-signature validation need a separately governed
policy for verification time and retained registry revisions; they must not
silently reuse the current-state trust decision.

## Operator verification checklist

- The registry validates against the signing-key registry schema.
- `activated_at < expires_at`, and both timestamps contain offsets.
- Key scope contains only governed record classes actually required.
- No private seed appears in Git history, CI logs, artifacts, fixtures, or
  generated reports.
- The registry verifier passes for an authorized representative record.
- Unknown, expired, revoked, not-yet-active, and out-of-scope keys fail closed.
- Rotation or revocation propagation is read back from every consumer.

