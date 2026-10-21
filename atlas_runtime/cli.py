"""Command-line boundary for one governed ATLAS execution step."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from .engine import ExecutionEnvelope, ExecutionResult, execute


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m atlas_runtime",
        description="Select the next atomic ATLAS work unit from a JSON execution request.",
    )
    parser.add_argument(
        "--input",
        default="-",
        metavar="PATH",
        help="JSON request path; '-' (the default) reads stdin.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "ndjson"),
        default="text",
        help="Output format; compact text is the default.",
    )
    return parser


def _read_request(path: str, stdin: TextIO) -> dict[str, Any]:
    raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid JSON input at line {error.lineno}, column {error.colno}"
        ) from error
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _build_envelope(request: dict[str, Any]) -> ExecutionEnvelope:
    try:
        objective = request["objective"]
        plan_id = request["plan_id"]
        work_units = request["work_units"]
    except KeyError as error:
        raise ValueError(f"missing required field: {error.args[0]}") from error
    return ExecutionEnvelope(
        objective=objective,
        plan_id=plan_id,
        work_units=work_units,
        surface=request.get("surface", "core"),
        clarification_status=request.get("clarification_status", "NOT_REQUIRED"),
        task_id=request.get("task_id"),
        capability_requirements=request.get("capability_requirements", ()),
        provider_inventory=request.get("provider_inventory"),
        routing_approval_status=request.get("routing_approval_status", "PENDING"),
        routing_preview_digest=request.get("routing_preview_digest"),
        timestamp=request.get("timestamp"),
        timezone_name=request.get("timezone_name", "UTC"),
    )


def _write_event(stdout: TextIO, event: dict[str, Any]) -> None:
    print(json.dumps(event, sort_keys=True, separators=(",", ":")), file=stdout, flush=True)


def _render_routing_preview(preview: dict[str, Any]) -> str:
    lines = [
        f"Routing preview · {preview['digest']}",
        f"Objective: {preview['objective']}",
        f"Execution: {preview['task_id'] or 'task ID pending'} · {preview['plan_id']} · {preview['surface']}",
        f"Work unit: {preview['work_unit'] or 'none'}",
        "Execution sequence: " + (" -> ".join(preview["execution_sequence"]) or "no provider routing"),
        "Unresolved gates: " + (", ".join(preview["unresolved_gates"]) or "none"),
    ]
    for index, step in enumerate(preview["steps"], start=1):
        lines.append(f"{index}. {step['stage']}: {step['description']}")
    lines.append("Proposed providers:")
    for provider in preview["providers"]:
        lines.extend((
            f"- {provider['name']} [{provider['type']}]",
            f"  What: {provider['purpose']}",
            f"  How: {provider['method']}",
            f"  Permission: {provider['permission']} | Data: {provider['data_scope']} | "
            f"Fallback: {provider['fallback'] or 'none'}",
            f"  Prerequisites: {', '.join(provider['prerequisites']) or 'none'}",
            f"  Unresolved gates: {', '.join(provider['unresolved_gates']) or 'none'}",
        ))
    lines.append(f"Review: {preview['approval_prompt']}")
    lines.append(f"Approve this exact preview with digest {preview['digest']}")
    return "\n".join(lines)


def _write_result(stdout: TextIO, result: ExecutionResult, output_format: str) -> None:
    if output_format == "text":
        print(result.compact_status, file=stdout)
        if result.routing_preview["status"] == "PROPOSED":
            print(file=stdout)
            print(_render_routing_preview(result.routing_preview), file=stdout)
        return
    _write_event(stdout, {
        "active_unit": result.active_unit,
        "event": "result",
        "plan": list(result.plan),
        "routing_decisions": list(result.routing_decisions),
        "routing_preview": result.routing_preview,
        "state": result.state,
        "task_classes": list(result.task_classes),
    })


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """Run the CLI and return a process exit code."""

    arguments = _parser().parse_args(argv)
    try:
        request = _read_request(arguments.input, stdin)
        envelope = _build_envelope(request)
        if arguments.format == "ndjson":
            _write_event(stdout, {
                "event": "accepted",
                "plan_id": envelope.plan_id,
                "surface": envelope.surface,
            })
        result = execute(envelope)
        _write_result(stdout, result, arguments.format)
    except (OSError, TypeError, ValueError) as error:
        print(f"ATLAS error: {error}", file=stderr)
        return 2
    return 0


__all__ = ["main"]
