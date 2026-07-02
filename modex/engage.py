#!/usr/bin/env python3
"""Modex Engage — point at ANY real project, get a certified FDE engagement.

This is the innate end-to-end loop, for any user, by construction:

    1. SCRUTINIZE  the real codebase  (fde_recon — Stage 0 Reconnaissance)
    2. AUTO-BUILD  a 6-Q from recon's signals (no human form-filling)
    3. RUN         the autonomous FDE+DeepSCR loop (ModexCollective.run_autonomous:
                   Lead -> Researcher -> Builder -> Certifier, 5-judgment self-prompting)
    4. CERTIFY     on GROUND TRUTH — the evidence trail is the real files recon found;
                   the Certifier verifies each path resolves on disk before awarding evidence.

No methodology expertise required from the caller. One call → a certified engagement.

Usage:
    from modex.engage import engage
    result = engage("/path/to/any/project")

    python3 -m modex.engage --project /path/to/any/project
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "skill" / "scripts"
for _p in (str(REPO_ROOT), str(SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fde_recon import scan_codebase  # noqa: E402
from scientific_search import FDECoordinator, FDEExecutor, default_golden_cases  # noqa: E402
from modex.arbiters import FrozenContract, OracleRegistry  # noqa: E402
from modex.collective import ModexCollective  # noqa: E402


def build_six_q(recon: dict[str, Any], project_path: str) -> dict[str, Any]:
    """Turn recon output into a 6-Q problem spec + a GROUND-TRUTH evidence trail.

    The evidence trail is absolute paths to the real files recon flagged — the
    Certifier verifies they resolve on disk, so certification is grounded in the
    actual project, not in the formatting of this dict.
    """
    s = recon.get("six_q_signals", {})
    size = recon.get("size", {})
    tests = recon.get("tests", {})
    risks = recon.get("risk_flags", [])
    base = Path(project_path)
    hot = recon.get("hotspots", {}).get("largest_files", [])[:5]
    evidence = [str((base / h["file"]).resolve()) for h in hot if h.get("file")]
    if not evidence:
        evidence = [str(base.resolve())]
    return {
        "q1_process": s.get("q1_process_hint", "Unknown process — scope from recon."),
        "q1_volume": f"{size.get('code_files', 0)} code files, {size.get('total_loc', 0)} LOC",
        "q1_owner": "project owner (to confirm)",
        "q2_decision_type": "recommendation",
        "q2_latency": "engagement-scoped",
        "q2_accuracy_target": "ship-ready FDE deliverable",
        "q3_volume": f"{size.get('total_files', 0)} files total",
        "q3_quality": s.get("q3_data_hint", ""),
        "q3_compliance": "review per project",
        "q3_refresh": "continuous",
        "q4_direct_cost": s.get("q4_cost_of_error_hint", ""),
        "q4_regulatory": "; ".join(risks) or "no risk flags from recon",
        "q4_distribution": "see risk flags",
        "q5_current_type": s.get("q5_current_system_hint", ""),
        "q5_current_performance": f"test-to-code ratio {tests.get('test_to_code_ratio', 0)}, CI={tests.get('has_ci', False)}",
        "q5_frustrations": "; ".join(risks[:3]) or "none surfaced",
        "q6_primary_metric": "certified FDE engagement delivered",
        "q6_threshold": s.get("q6_measurement_hint", ""),
        "q6_measurement": "FDE Assurance Score >=85 on VERIFIED evidence",
        # Ground truth: real files recon found in THIS project.
        "evidence_trail": evidence,
    }


def _measure_candidates(problem: dict[str, Any],
                        golden_cases: Optional[list] = None) -> list[dict[str, Any]]:
    """Independent, deterministic measurement of every candidate architecture
    (same hypothesis tree + held-out gate the Researcher uses, re-run from scratch)."""
    golden = golden_cases if golden_cases is not None else default_golden_cases(problem)
    if isinstance(golden, dict):
        golden = golden.get("cases", [])
    coordinator = FDECoordinator(problem, golden, Path("/dev/null"))
    return [FDEExecutor(h).evaluate(problem, golden)
            for h in coordinator.generate_hypothesis_tree()]


def measured_baseline_oracle(problem: dict[str, Any],
                             golden_cases: Optional[list] = None):
    """`sota_baseline_gate` with a MEASURED baseline, never a declared one.

    A naive baseline would be trivially satisfied: the Researcher already picks
    the top of the same search. So at ship time this oracle re-runs the search
    independently and requires the shipped candidate to:
      (a) REPRODUCE — its promotion must hold on the independent rerun;
      (b) NOT INFLATE — the claimed held-out score must equal the measured one;
      (c) BEAT THE COUNTERFACTUAL — measured held-out >= the best alternative
          the search found (the runner-up is the measured baseline).
    """
    def gate(ctx: dict) -> tuple[bool, float, str]:
        best = ctx.get("best") or {}
        shipped_id = best.get("hypothesis_id")
        claimed = best.get("held_out_score")
        measured = _measure_candidates(problem, golden_cases)
        if not shipped_id:
            # Shipping WITHOUT claiming a winning architecture (e.g. a scoping
            # recommendation) is legitimate — the gate bites on claims, not
            # on their absence. evals/evidence gates still apply.
            promoted_n = sum(1 for r in measured if r["promoted"])
            return True, 1.0, (f"no candidate claimed — baseline gate not applicable "
                               f"(measured {len(measured)} candidates, {promoted_n} promoted)")
        mine = next((r for r in measured if r["hypothesis_id"] == shipped_id), None)
        if mine is None or not mine["promoted"]:
            return False, 0.0, (f"shipped candidate {shipped_id} does not reproduce "
                                f"on the independent rerun ({len(measured)} candidates)")
        if claimed != mine["held_out_score"]:
            return False, 0.0, (f"claimed held-out {claimed}/100 != measured "
                                f"{mine['held_out_score']}/100 for {shipped_id}")
        rivals = [r for r in measured if r["hypothesis_id"] != shipped_id]
        runner = max(rivals, key=lambda r: (r["held_out_score"], r["development_score"]),
                     default=None)
        baseline = runner["held_out_score"] if runner else 0
        ok = mine["held_out_score"] >= baseline
        detail = (f"measured baseline={runner['hypothesis_id'] if runner else 'none'}:"
                  f"{baseline}/100 over {len(measured)} candidates; shipped "
                  f"{shipped_id}={mine['held_out_score']}/100 (reproduced)")
        return ok, mine["held_out_score"] / 100.0, detail
    return gate


def default_governance(goal: str, max_iterations: int = 10,
                       problem: Optional[dict[str, Any]] = None,
                       golden_cases: Optional[list] = None
                       ) -> tuple[FrozenContract, OracleRegistry]:
    """The Frozen Arbiters an engage() run ships with by default when governed.

    Contract: the four DeepSCR stages each serve a clause; anything else is
    mechanically rejected. Oracles: proven against injected bad cases (an
    oracle that misses a planted failure is not trusted), then frozen — the
    agent pleads, it never grades itself.
    """
    contract = FrozenContract(
        goal=goal,
        clauses={
            "C1": "Ground the scope in the real 6-Q built from recon",
            "C2": "Falsify hypotheses against the real codebase",
            "C3": "Assemble a shippable deliverable",
            "C4": "Certify independently on verified evidence, or veto",
        },
        metrics={"assurance": {"baseline": 0.0, "threshold": 85.0}},
        budgets={"iterations": max_iterations},
        non_goals=["elegance", "future-proofing"],
        stage_clauses={"scoping": "C1", "prototyping": "C2",
                       "production": "C3", "certification": "C4"},
    )
    contract.seal()
    oracles = OracleRegistry()
    oracles.register("evals_gate", lambda ctx: (
        ctx.get("evals", {}).get("verdict") == "PASS", 1.0,
        "builder evals must PASS"))
    oracles.register("evidence_on_disk", lambda ctx: (
        bool(ctx.get("problem", {}).get("evidence_trail"))
        and all(Path(p).exists() for p in ctx["problem"]["evidence_trail"]),
        1.0, "every evidence path must resolve on disk"))
    if not oracles.prove("evals_gate", known_bad=[{"evals": {"verdict": "FAIL"}}, {}]):
        raise RuntimeError("evals_gate oracle missed an injected failure")
    if not oracles.prove("evidence_on_disk", known_bad=[
            {"problem": {"evidence_trail": ["/nonexistent/ghost.py"]}},
            {"problem": {"evidence_trail": []}}]):
        raise RuntimeError("evidence_on_disk oracle missed an injected failure")
    if problem is not None:
        oracles.register("sota_baseline_gate",
                         measured_baseline_oracle(problem, golden_cases))
        # Mutation testing against the two lies the gate must catch:
        # a fabricated candidate and an inflated score. (A candidate-less
        # deliverable is NOT a lie — the gate is not applicable there.)
        measured = _measure_candidates(problem, golden_cases)
        top = max(measured, key=lambda r: (r["held_out_score"], r["development_score"]))
        known_bad = [
            {"best": {"hypothesis_id": "H999-fabricated", "held_out_score": 100}},
            {"best": {"hypothesis_id": top["hypothesis_id"],
                      "held_out_score": top["held_out_score"] + 7}},   # inflated claim
        ]
        if not oracles.prove("sota_baseline_gate", known_bad=known_bad):
            raise RuntimeError("sota_baseline_gate oracle missed an injected failure")
    oracles.freeze()
    return contract, oracles


def engage(project_path: str, max_iterations: int = 10,
           memory_dir: Optional[str] = None, governed: bool = False) -> dict[str, Any]:
    """Run a full, certified FDE+DeepSCR engagement on a real project.

    With `governed=True` the run is placed under the Frozen Arbiters: a sealed
    Contract governs every stage and frozen, mutation-tested oracles override
    the Certifier's optimism at ship time (see modex/arbiters.py)."""
    recon = scan_codebase(Path(project_path))
    if recon.get("error"):
        return {"status": "error", "error": recon["error"]}
    six_q = build_six_q(recon, project_path)
    contract = oracles = None
    if governed:
        goal = (f"Certified FDE engagement on {Path(project_path).resolve().name}, "
                f"grounded in on-disk evidence")
        contract, oracles = default_governance(goal, max_iterations=max_iterations,
                                               problem=six_q)
    mc = ModexCollective(memory_dir=Path(memory_dir) if memory_dir else Path("./fde-memory"))
    auto = mc.run_autonomous(six_q, max_iterations=max_iterations,
                             contract=contract, oracles=oracles)
    result = {
        "status": "success",
        "project": str(Path(project_path).resolve()),
        "recon_summary": recon.get("summary"),
        "claim": auto.claim,
        "certified": auto.status == "certified",
        "engagement_status": auto.status,
        "assurance_score": auto.trust_score.get("trust_score"),
        "evidence_verified": auto.trust_score.get("evidence_verified"),
        "iterations": auto.iterations,
        "governed": governed,
        "engagement": auto.to_dict(),
    }
    if governed and auto.contract_report is not None:
        rep = auto.contract_report
        result["contract_hash"] = rep.get("contract_hash")
        result["contract_integrity"] = rep.get("integrity")
        result["clause_distribution"] = rep.get("clause_distribution")
        result["rejected_actions"] = len(rep.get("rejected_actions", []))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Modex Engage — a certified FDE+DeepSCR engagement on any real project")
    ap.add_argument("--project", required=True, help="Path to the project to scrutinize")
    ap.add_argument("--max-iterations", type=int, default=10)
    ap.add_argument("--memory-dir", default="./fde-memory")
    ap.add_argument("--governed", action="store_true",
                    help="Place the run under the Frozen Arbiters (sealed Contract + frozen oracles)")
    args = ap.parse_args()
    result = engage(args.project, max_iterations=args.max_iterations,
                    memory_dir=args.memory_dir, governed=args.governed)
    # Keep stdout readable: drop the verbose transcript from the CLI print.
    summary = {k: v for k, v in result.items() if k != "engagement"}
    print(json.dumps(summary, indent=2, default=str))
    return 0 if result.get("certified") else 2


if __name__ == "__main__":
    sys.exit(main())
