from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any


_CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "atlas-argus-execution-v2.json"


def _load_contract(path: Path = _CONTRACT_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("contract_id") != "ATLAS_ARGUS_EXECUTION":
        raise ValueError("unexpected ATLAS ARGUS contract_id")
    if payload.get("status") != "CURRENT":
        raise ValueError("ATLAS ARGUS execution contract must be CURRENT")
    flow = payload.get("pre_execution_flow")
    if flow != ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"]:
        raise ValueError("ATLAS pre-execution flow must remain the exact three-step invariant")
    approval = payload.get("approval", {})
    if approval.get("key") != "ARGUS_ACTIVATION" or approval.get("explicit_user_approval_required") is not True:
        raise ValueError("ATLAS ARGUS activation approval invariant mismatch")
    if payload.get("activation_authority") != "ATLAS" or payload.get("next_step_authority") != "ATLAS":
        raise ValueError("ATLAS must retain activation and next-step authority")
    if payload.get("provider_return_target") != "ATLAS":
        raise ValueError("ARGUS provider results must return to ATLAS")
    return payload


EXECUTION_CONTRACT = _load_contract()
PRE_EXECUTION_FLOW = tuple(EXECUTION_CONTRACT["pre_execution_flow"])
ARGUS_APPROVAL = str(EXECUTION_CONTRACT["approval"]["key"])
ARGUS_ROUTE_CONTRACTS = MappingProxyType(
    {
        mechanism: (str(details["capability"]), str(details["provider"]))
        for mechanism, details in EXECUTION_CONTRACT["route_mechanisms"].items()
    }
)


__all__ = [
    "ARGUS_APPROVAL",
    "ARGUS_ROUTE_CONTRACTS",
    "EXECUTION_CONTRACT",
    "PRE_EXECUTION_FLOW",
]
