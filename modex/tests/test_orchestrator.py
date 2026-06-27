"""Tests for the Modex 1-agent local orchestrator."""
import asyncio
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skill" / "scripts"))

from modex.orchestrator import ModexRuntime, ModexResult


def test_certifier_all_true_returns_100():
    """Certifier with all True booleans returns Trust Score 100."""
    runtime = ModexRuntime(role="certifier")
    result = runtime.run({
        "claim_present": True,
        "has_3_failure_modes": True,
        "has_evidence_trail": True,
        "antipatterns_clean": True,
        "claim_text": "Test claim",
    })
    assert result.role == "certifier"
    assert result.error is None
    assert result.trust_score["trust_score"] == 100
    assert result.trust_score["verdict"] == "certified"
    assert result.trust_score["independent_of_lead"] is True


def test_certifier_all_false_returns_0():
    """Certifier with all False booleans returns Trust Score 0."""
    runtime = ModexRuntime(role="certifier")
    result = runtime.run({
        "claim_present": False,
        "has_3_failure_modes": False,
        "has_evidence_trail": False,
        "antipatterns_clean": False,
    })
    assert result.trust_score["trust_score"] == 0
    assert result.trust_score["verdict"] == "rejected"


def test_certifier_partial_returns_correct_sum():
    """Certifier with 3 True + 1 False returns 80 (25+25+30+0)."""
    runtime = ModexRuntime(role="certifier")
    result = runtime.run({
        "claim_present": True,
        "has_3_failure_modes": True,
        "has_evidence_trail": True,
        "antipatterns_clean": False,
    })
    assert result.trust_score["trust_score"] == 80
    assert result.trust_score["verdict"] == "needs_revision"
    assert result.trust_score["lowest_component"] == "antipatterns"


def test_certifier_with_deliverable_path_computes_sha256():
    """If deliverable_path is given, sha256 is computed."""
    runtime = ModexRuntime(role="certifier")
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test deliverable\nThis is a test.")
        deliverable_path = f.name
    try:
        result = runtime.run({
            "claim_present": True,
            "has_3_failure_modes": True,
            "has_evidence_trail": True,
            "antipatterns_clean": True,
            "deliverable_path": deliverable_path,
        })
        assert result.trust_score["sha256"]
        assert len(result.trust_score["sha256"]) == 64
    finally:
        Path(deliverable_path).unlink()


def test_lead_role_with_complete_spec():
    """Lead role validates a complete 6-Q spec."""
    runtime = ModexRuntime(role="lead")
    problem = {
        "q1_process": "Customer support ticket triage",
        "q1_volume": "1000 tickets per day",
        "q1_owner": "CS Lead Marie",
        "q2_decision_type": "classification",
        "q2_latency": "under 5 seconds",
        "q2_accuracy_target": "85 percent F1",
        "q3_volume": "50k tickets per month",
        "q3_quality": "clean deduplicated",
        "q3_compliance": "GDPR and ISO 27001",
        "q3_refresh": "real-time and weekly retrain",
        "q4_direct_cost": "50 dollars per misrouted ticket",
        "q4_regulatory": "GDPR fines up to 4 percent revenue",
        "q4_distribution": "90 percent minor, 10 percent catastrophic",
        "q5_current_type": "vendor",
        "q5_current_performance": "62 percent accuracy",
        "q5_frustrations": "language support, no personalization",
        "q6_primary_metric": "100k euros per year saved",
        "q6_threshold": "200 percent ROI",
        "q6_measurement": "monthly cohort analysis",
    }
    result = runtime.run({"problem_json": json.dumps(problem)})
    assert result.role == "lead"
    assert result.error is None
    assert result.output["decomposition"]["overall_score"] == 100
    assert result.output["ready"] is True


def test_lead_role_with_invalid_json():
    """Lead role returns error on invalid JSON."""
    runtime = ModexRuntime(role="lead")
    result = runtime.run({"problem_json": "not valid json"})
    # The lead role reports the error in output (not by raising),
    # so we check both output.error and result.error.
    assert result.error is None  # No exception was raised
    assert "error" in result.output
    assert result.output.get("concreteness_score") == 0


def test_researcher_role_basic():
    """Researcher role does basic problem evaluation."""
    runtime = ModexRuntime(role="researcher")
    problem = json.dumps({"q2_decision_type": "classification"})
    result = runtime.run({"problem_json": problem})
    assert result.role == "researcher"
    assert result.error is None
    assert result.output["research"]["problem_valid"] is True
    assert result.output["research"]["q2_decision_type"] == "classification"


def test_builder_role_with_markdown():
    """Builder role scores a deliverable on the 6-trait rubric."""
    runtime = ModexRuntime(role="builder")
    deliverable = """
# FDE Deliverable
## Executive Summary
This deliverable scores 50k tickets per month.
## Trust Score
We provide concrete artifacts.
"""
    result = runtime.run({"deliverable_markdown": deliverable})
    assert result.role == "builder"
    assert result.error is None
    assert "verdict" in result.output["evals"]
    assert "scores" in result.output["evals"]


def test_invalid_role_raises():
    """Invalid role raises ValueError on init."""
    with pytest.raises(ValueError):
        ModexRuntime(role="invalid")


def test_result_to_dict_round_trip():
    """ModexResult.to_dict() returns a JSON-serializable dict."""
    runtime = ModexRuntime(role="certifier")
    result = runtime.run({"claim_present": True, "has_3_failure_modes": True,
                          "has_evidence_trail": True, "antipatterns_clean": True})
    d = result.to_dict()
    assert isinstance(d, dict)
    assert d["schema"] == "fde-modex-runtime-result-v1"
    assert d["role"] == "certifier"
    # Should be JSON-serializable
    json.dumps(d, default=str)


def test_all_4_roles_run_without_error():
    """All 4 roles (lead, researcher, builder, certifier) run without error on minimal input."""
    for role in ("lead", "researcher", "builder", "certifier"):
        runtime = ModexRuntime(role=role)
        if role == "certifier":
            input_data = {"claim_present": True, "has_3_failure_modes": True,
                          "has_evidence_trail": True, "antipatterns_clean": True}
        elif role == "lead":
            input_data = {"problem_json": json.dumps({
                "q1_process": "x", "q1_volume": "1/day", "q1_owner": "y",
                "q2_decision_type": "classification", "q2_latency": "<1s",
                "q2_accuracy_target": ">90%", "q3_volume": "1000",
                "q3_quality": "clean", "q3_compliance": "none",
                "q3_refresh": "daily", "q4_direct_cost": "$1 per error",
                "q4_regulatory": "none", "q4_distribution": "90% minor",
                "q5_current_type": "manual", "q5_current_performance": "70%",
                "q5_frustrations": "time", "q6_primary_metric": "$10k/year",
                "q6_threshold": ">200% ROI", "q6_measurement": "quarterly",
            })}
        elif role == "researcher":
            input_data = {"problem_json": json.dumps({"q2_decision_type": "classification"})}
        elif role == "builder":
            input_data = {"deliverable_markdown": "# Test deliverable\n## Trust Score\nThis is fine."}
        result = runtime.run(input_data)
        assert result.error is None, f"Role {role} failed: {result.error}"
        assert result.role == role


def test_certifier_verifies_evidence_against_disk():
    """Ground-truth: the evidence component requires a real, resolvable file:line.
    Fixes 'certify form, not truth' — a fabricated evidence trail must NOT be certified."""
    rt = ModexRuntime(role="certifier")
    real = rt.run({"claim_present": True, "has_3_failure_modes": True, "antipatterns_clean": True,
                   "evidence_trail": ["modex/orchestrator.py", "skill/SKILL.md:103"]})
    assert real.trust_score["evidence_verified"] >= 1
    assert real.trust_score["components"]["evidence"] == 30
    fake = rt.run({"claim_present": True, "has_3_failure_modes": True, "antipatterns_clean": True,
                   "evidence_trail": ["does/not/exist.py:1", "nope.md"]})
    assert fake.trust_score["evidence_verified"] == 0
    assert fake.trust_score["components"]["evidence"] == 0
    assert fake.trust_score["verdict"] != "certified"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))