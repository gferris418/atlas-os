from __future__ import annotations

import unittest

from atlas_runtime.interoperability import (
    AdmissionState,
    BindingRegistry,
    ProviderManifest,
    admit_provider,
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


if __name__ == "__main__":
    unittest.main()
