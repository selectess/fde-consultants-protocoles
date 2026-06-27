"""A certified engagement must write a real, reproducible certificate SHA-256,
and `bash modex/verify.sh <project>` must verify it (gap 11 — no hollow hashes)."""
import json
import subprocess
from pathlib import Path

from modex.collective import ModexCollective

REPO = Path(__file__).resolve().parents[2]
FULL_6Q = {
    "q1_process": "churn", "q1_volume": "2000", "q1_owner": "VP",
    "q2_decision_type": "classification", "q2_latency": "<1s", "q2_accuracy_target": "0.80",
    "q3_volume": "50k", "q3_quality": "clean", "q3_compliance": "GDPR", "q3_refresh": "d",
    "q4_direct_cost": "12k", "q4_regulatory": "EU", "q4_distribution": "90/10",
    "q5_current_type": "manual", "q5_current_performance": "55%", "q5_frustrations": "late",
    "q6_primary_metric": "-18%", "q6_threshold": "200%", "q6_measurement": "cohort",
    "evidence_trail": ["modex/collective.py", "modex/specialists.py"],
}


def test_certified_engage_writes_verifiable_sha(tmp_path):
    mem = tmp_path / "fde-memory"
    result = ModexCollective(memory_dir=mem).run_autonomous(FULL_6Q, max_iterations=8)
    assert result.status == "certified", result.status
    ts = json.loads((mem / "trust-score.json").read_text())
    lv = ts.get("last_verdict")
    assert lv is not None, "trust-score.json must carry a last_verdict block"
    assert lv["score"] >= 85
    assert len(lv["sha256"]) == 64 and all(c in "0123456789abcdef" for c in lv["sha256"])


def test_verify_sh_passes_on_certified_engage(tmp_path):
    mem = tmp_path / "fde-memory"
    ModexCollective(memory_dir=mem).run_autonomous(FULL_6Q, max_iterations=8)
    proc = subprocess.run(
        ["bash", str(REPO / "modex" / "verify.sh"), str(tmp_path)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert proc.returncode == 0, f"verify.sh failed: {proc.stdout}{proc.stderr}"
