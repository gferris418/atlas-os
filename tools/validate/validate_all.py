#!/usr/bin/env python3
"""Run the complete ATLAS repository and AI-readiness validation suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(root: Path, script: str) -> int:
    command = [sys.executable, str(root / script), str(root)]
    result = subprocess.run(command, cwd=root, check=False)
    return result.returncode


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    checks = (
        "tools/validate/validate_repository.py",
        "tools/validate/validate_ai_readiness.py",
    )
    for script in checks:
        returncode = run(root, script)
        if returncode != 0:
            return returncode
    print("ATLAS complete validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
