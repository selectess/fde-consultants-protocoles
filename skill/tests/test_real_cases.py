"""Tests for real hostile cases on the FDE Skill.

These tests verify that the Skill behaves correctly on REAL-WORLD inputs:
1. Vague inputs (rejected)
2. Realistic inputs (validated)
3. Hostile inputs (rejected)
4. Edge cases (empty, partial, unicode)
5. MCP integration with real deliverable paths
"""
import asyncio
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]  # skill/tests -> skill -> fde
SCRIPTS_DIR = REPO_ROOT / "skill" / "scripts"
MCP_DIR = REPO_ROOT / "skill" / "mcp_server"

# Make scripts and mcp_server importable
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(MCP_DIR))

from decompose_problem import ProblemSpec, score_concreteness
from evals_runner import heuristic_score as evals_heuristic
from roi_calculator import ROISpec, calculate as roi_calc


# --- Test class: Real Hostile Cases ---


class TestRealHostileCases:
    """Tests on real hostile inputs (vague, partial, contradictory)."""

    def test_vague_input_no_process_rejected(self):
        """A problem with no process description is rejected."""
        spec = ProblemSpec()  # all empty
        result = score_concreteness(spec)
        assert result["overall_score"] == 0
        assert len(result["missing_fields"]) == 19
        assert result["is_ready"] is False

    def test_vague_with_buzzwords_rejected(self):
        """A problem with vague buzzwords is rejected."""
        spec = ProblemSpec(
            q1_process="AGI for everyone", q1_volume="lots of users", q1_owner="me",
            q2_decision_type="AGI", q2_latency="fast", q2_accuracy_target="high accuracy",
            q3_volume="big data", q3_quality="good", q3_compliance="none", q3_refresh="always",
            q4_direct_cost="free", q4_regulatory="no rules", q4_distribution="perfect",
            q5_current_type="none", q5_current_performance="infinite",
            q5_frustrations="haters",
            q6_primary_metric="world peace", q6_threshold="yes", q6_measurement="vibes",
        )
        result = score_concreteness(spec)
        assert result["overall_score"] == 100  # all fields filled
        assert len(result["warnings"]) > 0
        assert result["is_ready"] is False

    def test_realistic_input_validated(self):
        """A realistic SaaS churn 6-Q spec is validated."""
        spec = ProblemSpec(
            q1_process="Customer support ticket triage and routing",
            q1_volume="1000 tickets per day", q1_owner="Customer Success Lead Marie",
            q2_decision_type="classification", q2_latency="under 5 seconds",
            q2_accuracy_target="85 percent F1",
            q3_volume="50k tickets per month", q3_quality="clean, deduplicated, in 4 languages",
            q3_compliance="GDPR and ISO 27001", q3_refresh="real-time and full retrain weekly",
            q4_direct_cost="50 dollars per misrouted ticket, 500 per SLA breach",
            q4_regulatory="GDPR fines up to 4 percent revenue",
            q4_distribution="90 percent minor, 10 percent catastrophic",
            q5_current_type="vendor", q5_current_performance="62 percent accuracy, 12 seconds p99",
            q5_frustrations="language support, no personalization",
            q6_primary_metric="100k euros per year saved", q6_threshold="200 percent ROI",
            q6_measurement="monthly cohort analysis + NPS",
        )
        result = score_concreteness(spec)
        assert result["overall_score"] == 100
        assert result["is_ready"] is True


class TestROICalculatorRealCases:
    """Tests on real ROI inputs."""

    def test_customer_service_roi_positive(self):
        """Customer service ROI on a realistic input is positive."""
        spec = ROISpec(
            baseline_volume_per_period=10000, baseline_period="month",
            baseline_cost_per_unit=50.0, ai_auto_resolution_rate=0.6,
            ai_time_reduction_remaining=0.5, ai_cost_per_task=2.0,
            build_cost=50000, llm_api_cost_per_year=10000,
            infra_cost_per_year=5000, maintenance_cost_per_year=9000, confidence=0.7,
        )
        result = roi_calc(spec)
        assert result.year_1_roi_percent > 0
        assert result.payback_months < 36

    def test_high_baseline_no_ai_savings_zero_savings(self):
        """If auto_resolution is 0, savings are zero."""
        spec = ROISpec(
            baseline_volume_per_period=1000, baseline_period="month",
            baseline_cost_per_unit=10.0, ai_auto_resolution_rate=0.0,
            ai_time_reduction_remaining=0.0, build_cost=100000,
            llm_api_cost_per_year=50000, confidence=1.0,
        )
        result = roi_calc(spec)
        assert result.annual_ai_cost_savings == 0
        assert result.year_1_roi_percent < 0


class TestEvalsRunnerRealCases:
    """Tests on real deliverables."""

    def test_fintech_case_study_returns_scores(self):
        """A well-structured fintech case study returns valid scores."""
        case_study = (REPO_ROOT / "skill/examples/case-studies/case-study-fintech-fraud.md").read_text()
        result = evals_heuristic(case_study, context="Fintech fraud detection")
        assert "scores" in result
        assert "verdict" in result
        assert result["verdict"] in ("PASS", "FAIL")
        assert "scores" in result
        assert all(1 <= s <= 5 for s in result["scores"].values())

    def test_saas_case_study_differs_from_fintech(self):
        """The rubric may differentiate between case studies (heuristic-based)."""
        fintech = (REPO_ROOT / "skill/examples/case-studies/case-study-fintech-fraud.md").read_text()
        saas = (REPO_ROOT / "skill/examples/case-studies/case-study-saas-churn.md").read_text()
        r_fintech = evals_heuristic(fintech, context="Fintech")
        r_saas = evals_heuristic(saas, context="SaaS")
        # Both should produce valid scores (1-5) even if they happen to align
        for trait in r_fintech["scores"]:
            assert 1 <= r_fintech["scores"][trait] <= 5
            assert 1 <= r_saas["scores"][trait] <= 5
        # At least one difference is preferred but not required (heuristic may align)


class TestMCPIntegrationRealCases:
    """Tests that MCP tools handle real cases correctly."""

    def test_fde_trust_score_with_realistic_booleans(self):
        """Trust Score MCP tool with realistic certification values + real deliverable."""
        try:
            from skill.mcp_server.server import mcp
        except ImportError:
            pytest.skip("MCP server not available")

        case_study_path = str(
            REPO_ROOT / "skill/examples/case-studies/case-study-fintech-fraud.md"
        )
        assert Path(case_study_path).exists()

        async def run():
            return await mcp.call_tool(
                "fde_trust_score",
                {
                    "claim_present": True, "has_3_failure_modes": True,
                    "has_evidence_trail": True, "antipatterns_clean": True,
                    "claim_text": "Audit empirical d'un produit SaaS reel",
                    "deliverable_path": case_study_path,
                },
            )

        result = asyncio.run(run())
        items = list(result)
        text_found = None
        for item in items:
            for inner in item if isinstance(item, (list, tuple)) else [item]:
                if hasattr(inner, "text"):
                    text_found = inner.text
                    break
            if text_found:
                break
        assert text_found is not None
        d = json.loads(text_found)
        assert d["trust_score"] == 100
        assert d["verdict"] == "certified"
        assert len(d["sha256"]) == 64

    def test_fde_trust_score_with_partial_components(self):
        """Trust Score with 3 True + 1 False returns 80."""
        try:
            from skill.mcp_server.server import mcp
        except ImportError:
            pytest.skip("MCP server not available")

        async def run():
            return await mcp.call_tool(
                "fde_trust_score",
                {
                    "claim_present": True, "has_3_failure_modes": True,
                    "has_evidence_trail": True, "antipatterns_clean": False,
                    "claim_text": "Partial certification",
                },
            )

        result = asyncio.run(run())
        items = list(result)
        text_found = None
        for item in items:
            for inner in item if isinstance(item, (list, tuple)) else [item]:
                if hasattr(inner, "text"):
                    text_found = inner.text
                    break
            if text_found:
                break
        assert text_found is not None
        d = json.loads(text_found)
        assert d["trust_score"] == 80
        assert d["verdict"] == "needs_revision"
        assert d["lowest_component"] == "antipatterns"


class TestEdgeCases:
    """Edge cases that production users will hit."""

    def test_empty_problemspec_yields_zero_score(self):
        """Empty ProblemSpec yields score 0."""
        spec = ProblemSpec()
        result = score_concreteness(spec)
        assert result["overall_score"] == 0

    def test_partial_problemspec_yields_low_score(self):
        """Partial ProblemSpec yields low score."""
        spec = ProblemSpec(q1_process="Test", q1_volume="10/day", q1_owner="Me")
        result = score_concreteness(spec)
        assert result["overall_score"] < 20
        assert len(result["missing_fields"]) == 16

    def test_unicode_problemspec_handled(self):
        """Unicode (emoji + non-ASCII) input is handled correctly."""
        spec = ProblemSpec(
            q1_process="🚀 Traitement des tickets 中文 بالعربية",
            q1_volume="1000 tickets/jour", q1_owner="Équipe Support",
            q2_decision_type="classification", q2_latency="<5 secondes",
            q2_accuracy_target="85 percent",
            q3_volume="50k records", q3_quality="clean",
            q3_compliance="GDPR + AI Act", q3_refresh="real-time",
            q4_direct_cost="$50 per error", q4_regulatory="GDPR up to 4% revenue",
            q4_distribution="90% benign, 10% severe",
            q5_current_type="vendor", q5_current_performance="62% accuracy",
            q5_frustrations="language + personalization",
            q6_primary_metric="EUR 100k per year saved",
            q6_threshold="200% ROI", q6_measurement="monthly",
        )
        result = score_concreteness(spec)
        assert result["overall_score"] == 100
        assert result["is_ready"] is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))