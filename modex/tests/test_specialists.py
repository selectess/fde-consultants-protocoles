"""Tests for the 4 FDE specialists + their integration into the 8-agent Collective."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from modex.specialists import (
    run_specialists, specialists_markdown, SPECIALISTS, SpecialistOutput,
    DEEPSCR_ROLES, FDE_SPECIALIST_ROLES, ALL_AGENTS)
from modex.collective import ModexCollective

P = {
    "q1_process": "Predict B2B SaaS churn at renewal", "q1_volume": "2000 accounts",
    "q1_owner": "VP CS", "q2_decision_type": "classification", "q2_latency": "<1s",
    "q2_accuracy_target": "0.80 AUC", "q3_volume": "50k rows", "q3_quality": "clean",
    "q3_compliance": "GDPR", "q3_refresh": "daily", "q4_direct_cost": "12k/churn",
    "q4_regulatory": "EU", "q4_distribution": "90/10", "q5_current_type": "manual",
    "q5_current_performance": "55% recall", "q5_frustrations": "late", "q6_primary_metric": "churn -18%",
    "q6_threshold": "200% ROI", "q6_measurement": "monthly cohort",
    "evidence_trail": ["modex/collective.py", "modex/specialists.py"],
}


def test_there_are_exactly_four_specialists_and_eight_agents():
    assert len(SPECIALISTS) == 4
    assert set(FDE_SPECIALIST_ROLES) == {"scoping", "architecture", "agent", "production"}
    assert len(ALL_AGENTS) == 8 and set(ALL_AGENTS) == set(DEEPSCR_ROLES) | set(FDE_SPECIALIST_ROLES)


def test_specialists_produce_grounded_output():
    outs = run_specialists(P)
    assert len(outs) == 4
    roles = set()
    for o in outs:
        assert isinstance(o, SpecialistOutput)
        assert o.findings and o.recommendation and o.reference
        roles.add(o.role)
    assert roles == set(FDE_SPECIALIST_ROLES)
    assert "specialist" in specialists_markdown(outs).lower()


def test_scoping_specialist_flags_vague_six_q():
    out = next(o for o in run_specialists({"q1_process": "use AI", "q6_primary_metric": ""})
               if o.role == "scoping")
    assert any(("vague" in f.lower() or "sharpen" in f.lower()) for f in out.findings)


def test_architecture_specialist_reacts_to_compliance_and_latency():
    out = next(o for o in run_specialists(P) if o.role == "architecture")
    joined = " ".join(out.findings).lower()
    assert "gdpr" in joined or "rbac" in joined or "in-region" in joined
    assert "latency" in joined or "containerized" in joined or "cache" in joined


def test_collective_is_now_eight_agents():
    a = ModexCollective().run_autonomous(P, max_iterations=8)
    roster = a.to_dict()["roles"]
    assert set(roster["deepscr"]) == set(DEEPSCR_ROLES)
    assert set(roster["fde_specialists"]) == set(FDE_SPECIALIST_ROLES)


def test_builder_consults_specialists_and_deliverable_carries_them():
    r = ModexCollective().run(P)
    assert sum(1 for k in r.roles if k in FDE_SPECIALIST_ROLES) == 4
    md = ModexCollective._draft_deliverable(P, "claim", None, [], run_specialists(P))
    assert "FDE Specialist Analysis" in md


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
