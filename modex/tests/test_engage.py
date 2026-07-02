"""Tests for Modex Engage — the innate end-to-end FDE+DeepSCR loop on a real project."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skill" / "scripts"))

from modex.engage import engage, build_six_q, default_governance
from fde_recon import scan_codebase


def test_engage_runs_end_to_end_on_a_real_project(tmp_path):
    """Point Engage at a real directory → recon + autonomous loop + ground-truth certification."""
    r = engage(str(REPO_ROOT / "modex"), max_iterations=8, memory_dir=str(tmp_path))
    assert r["status"] == "success"
    assert r["recon_summary"]                      # it actually scrutinized the code
    assert r["engagement"]["transcript"]           # the self-prompting loop ran
    assert r["evidence_verified"] >= 1             # certified on REAL files recon found
    assert r["assurance_score"] is not None
    assert r["engagement_status"] in ("certified", "stopped_unresolved", "max_iterations_reached")


def test_six_q_evidence_is_real_ground_truth():
    """The auto-built 6-Q cites only files that actually exist (no fabricated evidence)."""
    recon = scan_codebase(REPO_ROOT / "modex")
    six_q = build_six_q(recon, str(REPO_ROOT / "modex"))
    assert six_q["evidence_trail"]
    assert all(Path(p).is_file() for p in six_q["evidence_trail"])
    # the 6-Q is grounded in recon signals, not boilerplate
    assert "LOC" in six_q["q1_volume"]


def test_engage_bad_path_errors_cleanly():
    r = engage("/does/not/exist/zzz")
    assert r["status"] == "error"


def test_default_governance_is_sealed_proven_frozen():
    """The default Arbiters ship ready: Contract sealed, oracles proven then frozen."""
    contract, oracles = default_governance("test goal", max_iterations=6)
    assert contract.sealed and contract.verify_integrity()
    assert contract.budgets["iterations"] == 6
    assert oracles.frozen
    assert oracles.proven == {"evals_gate": True, "evidence_on_disk": True}


def test_engage_governed_carries_contract_report(tmp_path):
    """`engage(governed=True)` places the run under the Frozen Arbiters and
    surfaces the contract report — integrity, drift, cited verdicts."""
    r = engage(str(REPO_ROOT / "modex"), max_iterations=8,
               memory_dir=str(tmp_path), governed=True)
    assert r["status"] == "success" and r["governed"] is True
    assert r["contract_hash"] and r["contract_integrity"] is True
    rep = r["engagement"]["contract_report"]
    assert rep is not None
    assert abs(sum(rep["clause_distribution"].values()) - 1.0) < 0.01  # drift measured
    assert rep["verdicts"] and all(v["valid"] for v in rep["verdicts"])  # no uncited verdict
    assert rep["oracle_ledger"] and all(x["passed"] for x in rep["oracle_ledger"])


def test_engage_ungoverned_stays_backward_compatible(tmp_path):
    r = engage(str(REPO_ROOT / "modex"), max_iterations=8, memory_dir=str(tmp_path))
    assert r["governed"] is False
    assert "contract_hash" not in r
    assert r["engagement"]["contract_report"] is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
