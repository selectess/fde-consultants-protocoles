"""Tests for the Frozen Arbiters — Contract, Oracles, Verdict grammar,
trajectory audit, distillation gate, and their integration into the
Collective's autonomous loop (the agent pleads, it never grades itself)."""
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skill" / "scripts"))

from modex.arbiters import (
    FrozenContract, OracleRegistry, TrajectoryAuditor, DistillationGate,
    make_verdict, ContractError, FrozenError,
)
from modex.collective import ModexCollective
from modex.tests.test_collective import PROBLEM


def _contract(stage_clauses=None, budgets=None) -> FrozenContract:
    return FrozenContract(
        goal="Triage engagement certified above baseline",
        clauses={"C1": "Ground the scope in the real 6-Q", "C2": "Falsify hypotheses on held-out cases",
                 "C3": "Assemble a shippable deliverable", "C4": "Certify independently or veto"},
        metrics={"assurance": {"baseline": 62.0, "threshold": 85.0}},
        budgets=budgets or {"iterations": 10},
        non_goals=["elegance", "future-proofing"],
        stage_clauses=stage_clauses if stage_clauses is not None else {
            "scoping": "C1", "prototyping": "C2", "production": "C3", "certification": "C4"},
    )


# ---- Arbiter 1: the Contract ------------------------------------------------
def test_contract_seals_and_blocks_mutation():
    c = _contract()
    c.seal()
    with pytest.raises(FrozenError):
        c.goal = "a different goal"
    with pytest.raises(FrozenError):
        c.seal()  # sealing twice is also a mutation


def test_contract_is_tamper_evident():
    c = _contract()
    c.seal()
    assert c.verify_integrity()
    c.clauses["C5"] = "smuggled clause"  # bypass __setattr__ via dict mutation
    assert not c.verify_integrity()      # ...but the seal catches it


def test_contract_rejects_unknown_stage_clause():
    with pytest.raises(ContractError):
        _contract(stage_clauses={"scoping": "C99"})


def test_contract_amendments_are_append_only_and_chained():
    c = _contract()
    c.seal()
    a1 = c.append_amendment("conservative reading of Q3 refresh cadence")
    a2 = c.append_amendment("second clarification")
    assert [a1, a2] == c.amendments and a1["link"] != a2["link"]
    assert c.verify_integrity()          # amendments never alter the sealed payload


def test_contract_victory_is_a_ceiling():
    c = _contract()
    c.seal()
    assert not c.victory({"assurance": 84.9})
    assert c.victory({"assurance": 85.0})


# ---- Arbiter 2: the Oracles ---------------------------------------------------
def test_oracle_registry_freezes():
    reg = OracleRegistry()
    reg.register("gate", lambda s: (True, 1.0, "ok"))
    reg.freeze()
    with pytest.raises(FrozenError):
        reg.register("edited_grader", lambda s: (True, 1.0, "self-serving"))


def test_oracle_runs_are_citable_and_ledgered():
    reg = OracleRegistry()
    reg.register("gate", lambda s: (s > 0, float(s > 0), f"subject={s}"))
    reg.freeze()
    r1, r2 = reg.run("gate", 1), reg.run("gate", -1)
    assert r1.run_id.startswith("run#0001") and r1.passed
    assert r2.run_id.startswith("run#0002") and not r2.passed
    assert len(reg.ledger) == 2 and reg.passing_ids() == {r1.run_id}


def test_oracle_earns_trust_by_mutation_testing():
    reg = OracleRegistry()
    reg.register("strict", lambda s: (s == "good", 1.0, ""))
    reg.register("blind", lambda s: (True, 1.0, ""))     # rubber-stamps everything
    assert reg.prove("strict", known_bad=["bug1", "bug2"])
    assert not reg.prove("blind", known_bad=["bug1"])    # missed the injected bug
    assert reg.proven == {"strict": True, "blind": False}


# ---- Arbiter 3: the Verdict grammar ------------------------------------------
def test_uncited_verdict_is_null():
    v = make_verdict("tests pass", "pass")               # no run id, no clause
    assert v.decision == "null" and not v.valid


def test_cited_verdict_is_valid():
    v = make_verdict("run 34/34", "pass", cites_run="run#0001-abc")
    assert v.valid and v.to_dict()["valid"]


# ---- Trajectory audit ---------------------------------------------------------
def test_thrashing_and_plateau_detection():
    assert TrajectoryAuditor.detect_thrashing(["lead", "builder", "lead", "builder"])
    assert not TrajectoryAuditor.detect_thrashing(["lead", "researcher", "builder", "certifier"])
    assert TrajectoryAuditor.detect_plateau([70, 70, 70, 70])
    assert not TrajectoryAuditor.detect_plateau([70, 75, 80, 85])
    assert TrajectoryAuditor.tokens_per_point(5000, 10) == 500.0
    assert TrajectoryAuditor.tokens_per_point(5000, 0) is None   # no gain = no ratio


# ---- Distillation gate --------------------------------------------------------
def test_distillation_refuses_unvalidated_trajectories():
    reg = OracleRegistry()
    reg.register("gate", lambda s: (bool(s), 1.0, ""))
    reg.freeze()
    good = reg.run("gate", True)
    gate = DistillationGate(reg)
    assert gate.distill([{"cites_run": "run#9999-fake"}]) is None      # echo chamber refused
    lesson = gate.distill([{"cites_run": good.run_id}])
    assert lesson is not None and gate.policy == []                     # candidate, not policy yet


def test_lesson_enters_policy_only_after_fresh_cases():
    reg = OracleRegistry()
    reg.register("gate", lambda s: (bool(s), 1.0, ""))
    reg.freeze()
    gate = DistillationGate(reg)
    lesson = gate.distill([{"cites_run": reg.run("gate", True).run_id}])
    assert lesson is not None
    assert not gate.admit(lesson, fresh_cases=[True, False], oracle_name="gate")  # fails a fresh case
    assert gate.admit(lesson, fresh_cases=[True, True], oracle_name="gate")
    assert len(gate.policy) == 1


# ---- Integration: the governed autonomous loop --------------------------------
@pytest.fixture
def memdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def test_unsealed_contract_refuses_launch(memdir):
    with pytest.raises(ContractError):
        ModexCollective(memory_dir=memdir).run_autonomous(PROBLEM, contract=_contract())


def test_governed_run_certifies_with_cited_verdicts(memdir):
    contract = _contract()
    contract.seal()
    oracles = OracleRegistry()
    oracles.register("evals_gate", lambda ctx: (
        ctx.get("evals", {}).get("verdict") == "PASS", 1.0, "builder evals must PASS"))
    oracles.freeze()
    # DeepSCR ground truth: certification requires REAL on-disk evidence.
    grounded = {**PROBLEM, "evidence_trail": ["modex/collective.py", "modex/arbiters.py"]}
    res = ModexCollective(memory_dir=memdir).run_autonomous(
        grounded, contract=contract, oracles=oracles)
    rep = res.contract_report
    assert rep is not None
    assert res.status == "certified" and res.shipped
    assert rep["integrity"] and rep["contract_hash"] == contract.hash
    assert rep["rejected_actions"] == [] and not rep["thrashing"]
    assert abs(sum(rep["clause_distribution"].values()) - 1.0) < 0.01   # drift measured
    assert rep["verdicts"] and all(v["valid"] for v in rep["verdicts"])  # no uncited verdict
    assert rep["oracle_ledger"] and rep["oracle_ledger"][0]["run_id"].startswith("run#")


def test_frozen_oracle_overrides_certifier_optimism(memdir):
    contract = _contract()
    contract.seal()
    oracles = OracleRegistry()
    oracles.register("hard_gate", lambda ctx: (False, 0.0, "deliberately failing gate"))
    oracles.freeze()
    res = ModexCollective(memory_dir=memdir).run_autonomous(
        PROBLEM, contract=contract, oracles=oracles)
    assert not res.shipped                                   # the agent cannot ship past its oracle
    assert "hard_gate" in (res.veto or "")
    assert res.contract_report is not None
    assert all(v["decision"] == "fail" for v in res.contract_report["verdicts"])


def test_action_without_clause_is_mechanically_rejected(memdir):
    contract = _contract(stage_clauses={})                   # nothing is covered
    contract.seal()
    res = ModexCollective(memory_dir=memdir).run_autonomous(PROBLEM, contract=contract)
    assert res.status == "contract_violation" and not res.shipped
    assert res.contract_report is not None
    assert res.contract_report["rejected_actions"]


def test_ungoverned_run_unchanged(memdir):
    res = ModexCollective(memory_dir=memdir).run_autonomous(PROBLEM)
    assert res.contract_report is None                       # backward compatible
