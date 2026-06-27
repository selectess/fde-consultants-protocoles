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


def engage(project_path: str, max_iterations: int = 10,
           memory_dir: Optional[str] = None) -> dict[str, Any]:
    """Run a full, certified FDE+DeepSCR engagement on a real project."""
    recon = scan_codebase(Path(project_path))
    if recon.get("error"):
        return {"status": "error", "error": recon["error"]}
    six_q = build_six_q(recon, project_path)
    mc = ModexCollective(memory_dir=Path(memory_dir) if memory_dir else Path("./fde-memory"))
    auto = mc.run_autonomous(six_q, max_iterations=max_iterations)
    return {
        "status": "success",
        "project": str(Path(project_path).resolve()),
        "recon_summary": recon.get("summary"),
        "claim": auto.claim,
        "certified": auto.status == "certified",
        "engagement_status": auto.status,
        "assurance_score": auto.trust_score.get("trust_score"),
        "evidence_verified": auto.trust_score.get("evidence_verified"),
        "iterations": auto.iterations,
        "engagement": auto.to_dict(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Modex Engage — a certified FDE+DeepSCR engagement on any real project")
    ap.add_argument("--project", required=True, help="Path to the project to scrutinize")
    ap.add_argument("--max-iterations", type=int, default=10)
    ap.add_argument("--memory-dir", default="./fde-memory")
    args = ap.parse_args()
    result = engage(args.project, max_iterations=args.max_iterations, memory_dir=args.memory_dir)
    # Keep stdout readable: drop the verbose transcript from the CLI print.
    summary = {k: v for k, v in result.items() if k != "engagement"}
    print(json.dumps(summary, indent=2, default=str))
    return 0 if result.get("certified") else 2


if __name__ == "__main__":
    sys.exit(main())
