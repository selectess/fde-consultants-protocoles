"""MCP tool: fde_evals

Wraps skill/scripts/evals_runner.py as an MCP tool.
Scores a deliverable on the 6-trait rubric (1-5) and returns PASS/FAIL.
"""
import json
import pathlib
import sys
from typing import Any

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.fastmcp import FastMCP

from evals_runner import heuristic_score as score_heuristic

# Canonical thresholds (mirror of evals_runner.py)
OVERALL_THRESHOLDS = {
    "min_score": 3,
    "min_ownership": 4,
    "min_decomposition": 4,
}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="fde_evals",
        description=(
            "Score a markdown deliverable on the 6-trait rubric "
            "(curiosity, ownership, decomposition, empathy, product_sense, communication) "
            "and return a PASS/FAIL verdict. Heuristic mode only (no API key needed). "
            "Use at Stage 4 (Feedback) before shipping."
        ),
    )
    def fde_evals(deliverable_markdown: str) -> dict[str, Any]:
        """Score a deliverable on the FDE 6-trait rubric.

        Args:
            deliverable_markdown: The full text of the deliverable to score.

        Returns:
            dict with 6 trait scores (1-5), verdict (PASS/FAIL), antipatterns, top_improvements.
        """
        result = score_heuristic(deliverable_markdown)

        scores = result.get("scores", {})
        verdict = result.get("verdict", "FAIL")
        anti = result.get("antipatterns", [])
        improvements = result.get("top_improvements", [])

        return {
            "scores": scores,
            "verdict": verdict,
            "antipatterns": anti,
            "top_improvements": improvements,
            "thresholds": OVERALL_THRESHOLDS,
        }