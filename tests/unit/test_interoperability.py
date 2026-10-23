from __future__ import annotations

import unittest

from atlas_runtime.interoperability import (
    AdmissionState,
    BindingRegistry,
    ProviderManifest,
    admit_provider,
    resolve_provider,
)


class InteroperabilityTests(unittest.TestCase):
    def test_provider_manifest_maps_fine_grained_capabilities(self) -> None:
        manifest = ProviderManifest.from_dict(
            {
                "provider_id": "microsoft.sharepoint",
                "protocol": "mcp",
                "provides": ["document.search", "document.read", "document.write"],
                "permissions": {"read": "automatic", "write": "approval_required"},
                "evidence": {"citations": True, "provenance": True},
            }
        )
        self.assertEqual("microsoft.sharepoint", manifest.provider_id)
        self.assertTrue(manifest.provides("document.read"))
        self.assertFalse(manifest.provides("tender.search"))

    def test_admission_requires_provenance(self) -> None:
        manifest = ProviderManifest.from_dict(
            {
                "provider_id": "example.provider",
                "protocol": "mcp",
                "provides": ["document.read"],
                "permissions": {"read": "automatic"},
                "evidence": {"citations": True, "provenance": True},
            }
        )
        receipt = admit_provider(manifest)
        self.assertIs(AdmissionState.CERTIFIED, receipt.state)
        self.assertTrue(receipt.checks["schema"])
        self.assertTrue(receipt.checks["provenance"])

    def test_schema_invalid_manifest_is_rejected_before_admission(self) -> None:
        invalid_manifests = [
            {
                "provider_id": "example.provider",
                "protocol": "unsupported",
                "provides": ["document.read"],
                "permissions": {"read": "automatic"},
                "evidence": {"provenance": True},
            },
            {
                "provider_id": "example.provider",
                "protocol": "mcp",
                "provides": ["document.read"],
                "permissions": {"read": "sometimes"},
                "evidence": {"provenance": True},
            },
            {
                "provider_id": "example.provider",
                "protocol": "mcp",
                "provides": ["document.read"],
                "permissions": {"read": "automatic"},
                "evidence": {"provenance": "false"},
            },
        ]
        for payload in invalid_manifests:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    ProviderManifest.from_dict(payload)

    def test_missing_permissions_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "permissions"):
            ProviderManifest.from_dict(
                {
                    "provider_id": "example.provider",
                    "protocol": "mcp",
                    "provides": ["document.read"],
                    "evidence": {"provenance": True},
                }
            )

    def test_binding_registry_resolves_primary_then_fallback(self) -> None:
        registry = BindingRegistry.from_dict(
            {
                "document.read": {
                    "primary": "microsoft.sharepoint",
                    "fallbacks": ["host.files"],
                }
            }
        )
        self.assertEqual(
            ("microsoft.sharepoint", "host.files"),
            registry.candidates("document.read"),
        )

    def test_resolver_uses_first_certified_provider_that_really_provides_capability(self) -> None:
        bindings = BindingRegistry.from_dict(
            {"supplier.search": {"primary": "bad.primary", "fallbacks": ["argus"]}}
        )
        bad = ProviderManifest.from_dict(
            {
                "provider_id": "bad.primary",
                "protocol": "mcp",
                "provides": ["company.resolve"],
                "permissions": {"read": "automatic"},
                "evidence": {"provenance": True},
            }
        )
        argus = ProviderManifest.from_dict(
            {
                "provider_id": "argus",
                "protocol": "native",
                "provides": ["supplier.search"],
                "permissions": {"read": "automatic"},
                "evidence": {"provenance": True},
            }
        )
        selected = resolve_provider(
            "supplier.search",
            bindings,
            manifests={"bad.primary": bad, "argus": argus},
            admission={"bad.primary": admit_provider(bad), "argus": admit_provider(argus)},
        )
        self.assertEqual("argus", selected)

    def test_resolver_rejects_unadmitted_provider_and_returns_none_without_valid_fallback(self) -> None:
        bindings = BindingRegistry.from_dict(
            {"tender.search": {"primary": "discovered.only", "fallbacks": []}}
        )
        manifest = ProviderManifest.from_dict(
            {
                "provider_id": "discovered.only",
                "protocol": "mcp",
                "provides": ["tender.search"],
                "permissions": {"read": "automatic"},
                "evidence": {"provenance": True},
            }
        )
        selected = resolve_provider(
            "tender.search",
            bindings,
            manifests={"discovered.only": manifest},
            admission={},
        )
        self.assertIsNone(selected)


if __name__ == "__main__":
    unittest.main()
