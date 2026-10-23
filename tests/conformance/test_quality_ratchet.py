from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"
QUALITY_REQUIREMENTS = ROOT / "requirements-quality.txt"


class QualityRatchetContractTests(unittest.TestCase):
    def test_quality_tools_are_pinned_separately_from_runtime_dependencies(self) -> None:
        self.assertTrue(QUALITY_REQUIREMENTS.is_file())
        text = QUALITY_REQUIREMENTS.read_text(encoding="utf-8")
        self.assertIn("coverage==", text)
        self.assertIn("mypy==", text)
        self.assertIn("ruff==", text)
        self.assertIn("types-PyYAML==", text)

    def test_validate_workflow_enforces_runtime_quality_gates(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("requirements-quality.txt", workflow)
        self.assertIn("name: Ruff", workflow)
        self.assertIn("python -m ruff check atlas_runtime", workflow)
        self.assertIn("name: Mypy", workflow)
        self.assertIn("python -m mypy atlas_runtime", workflow)
        self.assertIn("name: Runtime coverage ratchet", workflow)
        self.assertIn("--source=atlas_runtime", workflow)
        self.assertIn("--fail-under=75", workflow)


if __name__ == "__main__":
    unittest.main()
