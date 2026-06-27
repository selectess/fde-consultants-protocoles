"""MCP tool: fde_roi

Wraps skill/scripts/roi_calculator.py as an MCP tool.
Computes ROI, payback months, 5-year NPV from a business case JSON.
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

from roi_calculator import ROISpec, calculate as compute_roi


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="fde_roi",
        description=(
            "Compute Year 1 ROI, payback months, 5-year NPV, and a recommendation "
            "for an FDE business case. Input is a JSON object matching the ROISpec "
            "schema (baseline_volume_per_period, baseline_cost_per_unit, "
            "ai_auto_resolution_rate, build_cost, etc)."
        ),
    )
    def fde_roi(business_case_json: str) -> dict[str, Any]:
        """Compute ROI metrics for an FDE business case.

        Args:
            business_case_json: JSON string with ROISpec fields.

        Returns:
            dict with year1_roi, payback_months, npv_5y, sensitivity, recommendation.
        """
        try:
            data = json.loads(business_case_json)
            spec = ROISpec(**data)
        except (json.JSONDecodeError, TypeError) as e:
            return {
                "error": f"Invalid JSON or schema: {e}",
                "year1_roi": None,
                "payback_months": None,
                "npv_5y": None,
                "sensitivity": {},
                "recommendation": "INVALID_INPUT",
            }

        result = compute_roi(spec)
        # result.recommendations is a list[str]; join into a single string for JSON.
        recommendation = " ".join(result.recommendations) if result.recommendations else ""

        return {
            "year1_roi": result.year_1_roi_percent,
            "year2_roi": result.year_2_roi_percent,
            "payback_months": result.payback_months,
            "npv_5y": result.five_year_npv,
            "annual_baseline_cost": result.annual_baseline_cost,
            "annual_net_impact": result.annual_net_impact,
            "recommendation": recommendation,
        }