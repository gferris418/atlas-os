from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from .models import ExecutionEnvelope
from .runtime import execute


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m atlas_runtime", description="Run one governed ATLAS routing step.")
    parser.add_argument("--input", default="-", help="JSON input path; '-' reads stdin")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _read(path: str, stdin: TextIO) -> dict[str, Any]:
    raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def _envelope(value: dict[str, Any]) -> ExecutionEnvelope:
    if "objective" not in value:
        raise ValueError("missing required field: objective")
    return ExecutionEnvelope(
        objective=value["objective"],
        task_id=value.get("task_id"),
        host=value.get("host", "generic-host"),
        context=value.get("context", {}),
        approvals=tuple(value.get("approvals", ())),
        provider_result=value.get("provider_result"),
    )


def main(argv: Sequence[str] | None = None, *, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    args = _parser().parse_args(argv)
    try:
        result = execute(_envelope(_read(args.input, stdin)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ATLAS error: {exc}", file=stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")), file=stdout)
    else:
        dashboard = result.dashboard
        print(
            f"ATLAS/{dashboard['host']} {dashboard['progress']}% | {result.state} | "
            f"{result.route.mechanism} | Next authority {result.next_step_authority}",
            file=stdout,
        )
        if dashboard["blocker_or_approval"]:
            print(f"Approval: {dashboard['blocker_or_approval']}", file=stdout)
        print(f"Next: {dashboard['next_action']}", file=stdout)
    return 0
