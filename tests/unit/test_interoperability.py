from atlas_runtime.interoperability import (
    AdmissionState,
    BindingRegistry,
    ProviderManifest,
    admit_provider,
)


def test_provider_manifest_maps_fine_grained_capabilities():
    manifest = ProviderManifest.from_dict(
        {
            "provider_id": "microsoft.sharepoint",
            "protocol": "mcp",
            "provides": ["document.search", "document.read", "document.write"],
            "permissions": {"read": "automatic", "write": "approval_required"},
            "evidence": {"citations": True, "provenance": True},
        }
    )
    assert manifest.provider_id == "microsoft.sharepoint"
    assert manifest.provides("document.read")
    assert not manifest.provides("tender.search")


def test_admission_requires_schema_and_provenance():
    manifest = ProviderManifest.from_dict(
        {
            "provider_id": "example.provider",
            "protocol": "mcp",
            "provides": ["document.read"],
            "evidence": {"citations": True, "provenance": True},
        }
    )
    receipt = admit_provider(manifest)
    assert receipt.state is AdmissionState.CERTIFIED
    assert receipt.checks["schema"] is True
    assert receipt.checks["provenance"] is True


def test_binding_registry_resolves_primary_then_fallback():
    registry = BindingRegistry.from_dict(
        {
            "document.read": {
                "primary": "microsoft.sharepoint",
                "fallbacks": ["host.files"],
            }
        }
    )
    assert registry.candidates("document.read") == (
        "microsoft.sharepoint",
        "host.files",
    )
