"""MCP tool: fde_decompose

Wraps skill/scripts/decompose_problem.py as an MCP tool.
Validates a 6-Q decomposition of a problem and returns score + warnings.

Input: a JSON object with the 6-Q fields (q1_process, q1_volume, ...).
Output: JSON with concreteness_score, missing_fields, warnings, ready, spec.
"""
import json
import pathlib
import sys
from typing import Any

# Make decompose_problem.py importable
SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from mcp.server.fastmcp import FastMCP

from decompose_problem import ProblemSpec, score_concreteness

# Constants from the script (mirror the canonical lists)
REQUIRED_FIELDS = [
    "q1_process", "q1_volume", "q1_owner",
    "q2_decision_type", "q2_latency", "q2_accuracy_target",
    "q3_volume", "q3_quality", "q3_compliance", "q3_refresh",
    "q4_direct_cost", "q4_regulatory", "q4_distribution",
    "q5_current_type", "q5_current_performance", "q5_frustrations",
    "q6_primary_metric", "q6_threshold", "q6_measurement",
]
DECISION_TYPES = ["classification", "ranking", "generation", "recommendation", "prediction"]

# Register the tool on the shared FastMCP instance from server.py
# Importing it here would create a circular import; instead we expect
# server.py to have created `mcp` and we register via the module-level decorator.
# We use a relative import workaround: server.py imports us AFTER instantiating mcp.

# To avoid circularity, we accept the FastMCP instance as an argument.
def register(mcp: FastMCP) -> None:
    """Register the fde_decompose tool on the given FastMCP server."""

    @mcp.tool(
        name="fde_decompose",
        description=(
            "Validate a 6-Q decomposition of an FDE problem. Returns concreteness "
            "score (0-100), missing fields, warnings, and a 'ready' boolean. "
            "Use this at Stage 1 (Scoping) before any prototype work."
        ),
    )
    def fde_decompose(problem_json: str) -> dict[str, Any]:
        """Validate a 6-Q problem decomposition.

        Args:
            problem_json: JSON string with the 6-Q fields.

        Returns:
            dict with keys: concreteness_score, missing_fields, warnings, ready, spec.
        """
        try:
            data = json.loads(problem_json)
            spec = ProblemSpec(**data)
        except (json.JSONDecodeError, TypeError) as e:
            return {
                "concreteness_score": 0,
                "missing_fields": list(REQUIRED_FIELDS),
                "warnings": [f"Invalid JSON or schema: {e}"],
                "ready": False,
                "spec": None,
            }

        result = score_concreteness(spec)
        score = result["overall_score"]
        missing = result["missing_fields"]
        warnings = list(result["warnings"])

        # Check Q2 enum
        if spec.q2_decision_type and spec.q2_decision_type not in DECISION_TYPES:
            warnings.append(
                f"Q2 decision type '{spec.q2_decision_type}' should be one of: "
                + ", ".join(DECISION_TYPES)
            )

        return {
            "concreteness_score": score,
            "missing_fields": missing,
            "warnings": warnings,
            "ready": len(missing) == 0 and len(warnings) == 0,
            "spec": data,
        }