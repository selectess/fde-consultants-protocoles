"""Tests for the Modex Collective — the $260 multi-agent tier with the
self-prompting protocol (5 judgments + inter-agent routing + human-informed loop)."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skill" / "scripts"))

from modex.collective import (
    ModexCollective, CollectiveResult, AutonomousResult, Judgment,
    FIVE_LENSES, judge, route_next, _verdict,
)


# A complete, concrete 6-Q problem (scores 100 on the decomposition rubric).
PROBLEM = {
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


@pytest.fixture
def memdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ---- The five judgments ---------------------------------------------------
def test_verdict_thresholds():
    assert _verdict(0.95) == "pass"
    assert _verdict(0.8) == "pass"
    assert _verdict(0.6) == "weak"
    assert _verdict(0.3) == "fail"


def test_judge_returns_exactly_five_lenses():
    event = {"stage": "scoping", "role": "lead",
             "payload": {"decomposition": {"overall_score": 100}, "ready": True, "claim": "x"}}
    judgments = judge(event, {})
    assert [j.lens for j in judgments] == list(FIVE_LENSES)
    assert all(isinstance(j, Judgment) for j in judgments)
    assert all(j.verdict in ("pass", "weak", "fail") for j in judgments)
    assert all(0.0 <= j.score <= 1.0 for j in judgments)


def test_judge_strong_scoping_all_pass_no_prompts():
    event = {"stage": "scoping", "payload": {"decomposition": {"overall_score": 100}, "ready": True}}
    judgments = {j.lens: j for j in judge(event, {})}
    assert judgments["evidence"].verdict == "pass"
    assert judgments["telos"].verdict == "pass"
    # a passing lens emits no self-prompt / route
    assert judgments["evidence"].next_prompt is None
    assert judgments["evidence"].route_to is None


def test_judge_weak_evidence_emits_self_prompt_to_researcher():
    event = {"stage": "prototyping", "payload": {"best": None, "hypotheses_count": 3}}
    j_ev = next(j for j in judge(event, {}) if j.lens == "evidence")
    assert j_ev.verdict == "fail"
    assert j_ev.route_to == "researcher"
    assert j_ev.next_prompt and "evidence" in j_ev.next_prompt.lower()


def test_judge_risk_flags_irreversible_ship():
    event = {"stage": "certification", "payload": {"shipped": True, "trust": {"trust_score": 100}}}
    j_risk = next(j for j in judge(event, {}) if j.lens == "risk")
    assert "irreversible" in j_risk.rationale.lower()


def test_judge_coherence_drops_on_repeated_failure():
    event = {"stage": "certification", "payload": {"shipped": False, "trust": {"trust_score": 80}}}
    j = next(x for x in judge(event, {"repeated_failure": True}) if x.lens == "coherence")
    assert j.verdict != "pass"
    assert j.route_to == "lead"


# ---- The self-prompting router -------------------------------------------
def test_route_advances_pipeline_when_all_pass():
    judgments = [Judgment(l, 1.0, "pass", "ok") for l in FIVE_LENSES]
    budgets = {r: 2 for r in ("lead", "researcher", "builder", "certifier")}
    r1 = route_next("lead", judgments, {}, budgets)
    r2 = route_next("researcher", judgments, {}, budgets)
    r3 = route_next("builder", judgments, {}, budgets)
    assert r1 and r1[0] == "researcher"
    assert r2 and r2[0] == "builder"
    assert r3 and r3[0] == "certifier"


def test_route_certified_terminates():
    judgments = [Judgment(l, 1.0, "pass", "ok") for l in FIVE_LENSES]
    budgets = {r: 2 for r in ("lead", "researcher", "builder", "certifier")}
    assert route_next("certifier", judgments, {"shipped": True}, budgets) is None


def test_route_evidence_fail_loops_back_to_researcher():
    judgments = [Judgment("evidence", 0.2, "fail", "weak", "fix it", "researcher")]
    budgets = {"lead": 2, "researcher": 2, "builder": 2, "certifier": 2}
    nxt = route_next("researcher", judgments, {}, budgets)
    assert nxt is not None and nxt[0] == "researcher"
    assert budgets["researcher"] == 1  # budget consumed → guarantees termination


def test_route_certifier_veto_routes_to_weakest_owner():
    judgments = [Judgment(l, 1.0, "pass", "ok") for l in FIVE_LENSES]
    budgets = {"lead": 2, "researcher": 2, "builder": 2, "certifier": 2}
    ctx = {"shipped": False, "trust": {"lowest_component": "evidence"}, "veto": "blocked"}
    nxt = route_next("certifier", judgments, ctx, budgets)
    assert nxt is not None and nxt[0] == "researcher"  # evidence is owned by the researcher


def test_route_exhausted_budget_stops():
    judgments = [Judgment("evidence", 0.2, "fail", "weak", "fix", "researcher")]
    budgets = {"lead": 0, "researcher": 0, "builder": 0, "certifier": 0}
    ctx = {"shipped": False, "trust": {"lowest_component": "evidence"}}
    assert route_next("certifier", judgments, ctx, budgets) is None


# ---- Single-pass engagement (preserved behaviour) ------------------------
def test_single_pass_run_returns_result(memdir):
    result = ModexCollective(memory_dir=memdir).run(PROBLEM)
    assert isinstance(result, CollectiveResult)
    assert result.schema == "fde-modex-collective-result-v1"
    assert result.claim
    assert "trust_score" in result.trust_score
    assert isinstance(result.shipped, bool)
    # separation of powers: shipping is decided by the certifier verdict
    assert result.shipped == (result.trust_score.get("verdict") == "certified")
    json.dumps(result.to_dict(), default=str)  # serialisable


# ---- Autonomous (self-prompting) engagement ------------------------------
def test_run_autonomous_terminates_and_keeps_human_informed(memdir):
    auto = ModexCollective(memory_dir=memdir).run_autonomous(
        PROBLEM, max_iterations=8, retries_per_agent=1)
    assert isinstance(auto, AutonomousResult)
    assert auto.status in ("certified", "stopped_unresolved", "max_iterations_reached")
    assert 1 <= auto.iterations <= 8
    # the inter-agent dialogue happened
    assert len(auto.transcript) >= 1
    assert len(auto.blackboard) == len(auto.transcript)
    # every step carried all five judgments
    for step in auto.transcript:
        assert set(step["judgments"].keys()) == set(FIVE_LENSES)
    # the human was kept informed (step + judgment + done notifications)
    levels = {n["level"] for n in auto.notifications}
    assert "step" in levels and "judgment" in levels and "done" in levels
    # notifications + blackboard were persisted to memory
    assert (memdir / "notifications.md").exists()
    assert (memdir / "blackboard.jsonl").exists()


def test_run_autonomous_shows_agents_prompting_each_other(memdir):
    auto = ModexCollective(memory_dir=memdir).run_autonomous(PROBLEM, max_iterations=8)
    # at least one step routed a self-prompt to another agent
    routed = [s for s in auto.transcript if s["to"] and s["self_prompt"]]
    assert routed, "expected at least one inter-agent self-prompt"


def test_run_autonomous_is_deterministic(memdir):
    a = ModexCollective(memory_dir=memdir / "a").run_autonomous(PROBLEM, max_iterations=8, retries_per_agent=1)
    b = ModexCollective(memory_dir=memdir / "b").run_autonomous(PROBLEM, max_iterations=8, retries_per_agent=1)
    assert a.status == b.status
    assert a.iterations == b.iterations
    assert [s["judgments"] for s in a.transcript] == [s["judgments"] for s in b.transcript]


def test_human_in_loop_default_never_awaits_ack(memdir):
    auto = ModexCollective(memory_dir=memdir).run_autonomous(PROBLEM, max_iterations=8, human_in_loop=False)
    assert auto.status != "awaiting_human_ack"


def test_collective_requires_verified_evidence(memdir):
    """The fixed flaw: a well-formed engagement WITHOUT real evidence must NOT certify;
    WITH a verified real evidence_trail it can (DeepSCR: trust the evidence, not the claim)."""
    no_ev = ModexCollective(memory_dir=memdir / "a").run(PROBLEM)
    assert no_ev.shipped is False
    assert no_ev.trust_score["verdict"] != "certified"
    grounded = dict(PROBLEM)
    grounded["evidence_trail"] = ["modex/collective.py", "skill/SKILL.md:103"]
    with_ev = ModexCollective(memory_dir=memdir / "b").run(grounded)
    assert with_ev.trust_score["evidence_verified"] >= 1
    assert with_ev.trust_score["components"]["evidence"] == 30
    assert with_ev.shipped is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
