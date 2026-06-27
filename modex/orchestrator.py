#!/usr/bin/env python3
"""Modex Runtime — 1-agent local orchestrator.

Executes one sub-agent (Certifier by default) on an input, validates the output,
and returns a Trust Score.

Usage:
    from modex.orchestrator import ModexRuntime
    runtime = ModexRuntime(role="certifier")
    result = runtime.run(input_data={"deliverable_path": "..."})
    print(result)
"""
import hashlib
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

# Make skill/scripts/ importable (this file lives at <repo>/modex/orchestrator.py)
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "skill" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Local imports
from decompose_problem import ProblemSpec, score_concreteness
from roi_calculator import ROISpec, calculate as compute_roi
from evals_runner import heuristic_score as score_evals
from ontology_extractor import heuristic_extract as extract_ontology, to_mermaid
from scientific_search import FDECoordinator, default_golden_cases


@dataclass
class ModexResult:
    """Result of a Modex runtime execution."""
    schema: str
    role: str
    input_data: dict[str, Any]
    output: dict[str, Any]
    trust_score: dict[str, Any]
    sha256: str
    executed_at: str
    duration_seconds: float
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModexRuntime:
    """Orchestrator for 1 sub-agent in the Modex collective.

    By default runs the Certifier role (independent Trust Score computation).
    Other roles can be plugged in by overriding `execute()`.
    """

    def __init__(self, role: str = "certifier", memory_dir: Optional[Path] = None):
        """Initialize the Modex runtime.

        Args:
            role: One of 'lead', 'researcher', 'builder', 'certifier'.
            memory_dir: Path to fde-memory/. Defaults to './fde-memory'.
        """
        if role not in ("lead", "researcher", "builder", "certifier"):
            raise ValueError(f"Invalid role: {role}. Must be one of lead, researcher, builder, certifier")
        self.role = role
        self.memory_dir = Path(memory_dir) if memory_dir else Path("./fde-memory")

    def run(self, input_data: dict[str, Any]) -> ModexResult:
        """Execute the role on the input data.

        Args:
            input_data: Dict with keys depending on the role.
                - For certifier: {"claim_present": bool, "has_3_failure_modes": bool, ...}
                - For lead: {"problem_json": str}
                - For researcher: {"problem_json": str, "golden_set_json": str}
                - For builder: {"deliverable_markdown": str}

        Returns:
            ModexResult with output + Trust Score.
        """
        start = datetime.now(timezone.utc)
        try:
            if self.role == "certifier":
                output = self._execute_certifier(input_data)
            elif self.role == "lead":
                output = self._execute_lead(input_data)
            elif self.role == "researcher":
                output = self._execute_researcher(input_data)
            elif self.role == "builder":
                output = self._execute_builder(input_data)
            else:
                raise ValueError(f"Unknown role: {self.role}")
            error = None
        except Exception as e:
            output = {}
            error = str(e)
        end = datetime.now(timezone.utc)
        duration = (end - start).total_seconds()
        sha256 = hashlib.sha256(
            json.dumps(output, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return ModexResult(
            schema="fde-modex-runtime-result-v1",
            role=self.role,
            input_data=input_data,
            output=output,
            trust_score=output.get("trust_score", {}),
            sha256=sha256,
            executed_at=start.isoformat(),
            duration_seconds=duration,
            error=error,
        )

    @staticmethod
    def _verify_evidence_trail(evidence_trail) -> tuple:
        """Verify each 'path' or 'path:line' reference resolves to a real file on disk."""
        verified = 0
        details: list[dict[str, Any]] = []
        for ref in evidence_trail or []:
            path_part = str(ref).split(":", 1)[0].strip()
            exists = bool(path_part) and (REPO_ROOT / path_part).is_file()
            verified += 1 if exists else 0
            details.append({"ref": ref, "verified": exists})
        return verified, details

    def _execute_certifier(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Certifier role: compute Trust Score independently.

        Required input_data keys:
            - claim_present: bool
            - has_3_failure_modes: bool
            - has_evidence_trail: bool
            - antipatterns_clean: bool
            - claim_text (optional): str
            - deliverable_path (optional): str
        """
        claim_present = bool(input_data.get("claim_present", False))
        has_3_failure_modes = bool(input_data.get("has_3_failure_modes", False))
        has_evidence_trail = bool(input_data.get("has_evidence_trail", False))
        # GROUND-TRUTH verification (fixes "certify form, not truth"): if an
        # evidence_trail (list of 'path' or 'path:line' refs) is supplied, the
        # evidence component is awarded ONLY if >=1 reference resolves to a real
        # file on disk. Structure alone no longer certifies. DeepSCR: trust the
        # evidence, not the claim.
        evidence_trail = input_data.get("evidence_trail")
        evidence_verified = None
        evidence_details: list[dict[str, Any]] = []
        if evidence_trail is not None:
            evidence_verified, evidence_details = self._verify_evidence_trail(evidence_trail)
            has_evidence_trail = evidence_verified >= 1
        antipatterns_clean = bool(input_data.get("antipatterns_clean", False))
        claim_text = input_data.get("claim_text", "")
        deliverable_path = input_data.get("deliverable_path", "")
        weights = {"claim": 25, "contradiction": 25, "evidence": 30, "antipatterns": 20}
        components = {
            "claim": weights["claim"] if claim_present else 0,
            "contradiction": weights["contradiction"] if has_3_failure_modes else 0,
            "evidence": weights["evidence"] if has_evidence_trail else 0,
            "antipatterns": weights["antipatterns"] if antipatterns_clean else 0,
        }
        score = sum(components.values())
        if score >= 85:
            verdict = "certified"
        elif score >= 60:
            verdict = "needs_revision"
        else:
            verdict = "rejected"
        sha256 = ""
        if deliverable_path:
            p = Path(deliverable_path)
            if p.exists() and p.is_file():
                sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
        lowest = min(components.keys(), key=lambda k: components[k])
        trust_score = {
            "schema": "fde-trust-score-v1",
            "deliverable": deliverable_path,
            "claim": claim_text,
            "components": components,
            "trust_score": score,
            "verdict": verdict,
            "sha256": sha256,
            "lowest_component": lowest,
            "evidence_verified": evidence_verified,
            "evidence_details": evidence_details,
            "independent_of_lead": True,
            "weights": weights,
        }
        return {"trust_score": trust_score}

    def _execute_lead(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Lead role: validate a 6-Q problem decomposition.

        Required input_data keys:
            - problem_json: str (JSON of ProblemSpec fields)
        """
        problem_json = input_data.get("problem_json", "{}")
        try:
            data = json.loads(problem_json)
            spec = ProblemSpec(**data)
        except (json.JSONDecodeError, TypeError) as e:
            return {"error": f"Invalid JSON or schema: {e}", "concreteness_score": 0}
        result = score_concreteness(spec)
        return {
            "decomposition": result,
            "ready": result["is_ready"],
            "claim": f"Decomposition of {spec.q1_process[:50] or 'unknown process'}",
        }

    def _execute_researcher(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Researcher role: falsify hypotheses against a real held-out gate.

        This is the DeepSCR "contradiction" stage: generate an architecture
        hypothesis tree, score each on development evidence, then run the
        held-out promotion gate (scientific_search.FDECoordinator). Only a
        hypothesis that survives the gate is promoted.

        Required input_data keys:
            - problem_json: str (6-Q problem spec)
            - golden_set_json (optional): str (held-out cases; derived from the
              6-Q if omitted)

        On minimal/partial input the held-out gate is skipped gracefully so the
        1-agent local runtime never hard-fails.
        """
        problem_json = input_data.get("problem_json", "{}")
        try:
            problem = json.loads(problem_json)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {e}"}

        research: dict[str, Any] = {
            "problem_valid": True,
            "q2_decision_type": problem.get("q2_decision_type", "unknown"),
        }
        try:
            import io
            import contextlib
            import tempfile

            golden_json = input_data.get("golden_set_json")
            if golden_json:
                golden_cases = json.loads(golden_json)
                # Accept either a bare list or the {"cases": [...]} envelope
                # (same normalization as the scientific_search CLI loader).
                if isinstance(golden_cases, dict):
                    golden_cases = golden_cases.get("cases", [])
            else:
                golden_cases = default_golden_cases(problem)
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as lf:
                lessons_out = Path(lf.name)
            coordinator = FDECoordinator(problem, golden_cases, lessons_out)
            with contextlib.redirect_stdout(io.StringIO()):
                htr = coordinator.run_htr()
            best = htr.get("best_hypothesis")
            research.update({
                "held_out_gate_run": True,
                "hypotheses_tested": htr.get("tree_size", 0),
                "held_out_cases": htr.get("held_out_cases", 0),
                "promoted_hypothesis_id": best["hypothesis_id"] if best else None,
                "promoted_hypothesis": best["description"] if best else None,
                "lessons_count": htr.get("lessons_count", 0),
                "lesson": (
                    f"Promoted {best['hypothesis_id']} ({best['description']}) "
                    f"via the held-out gate."
                    if best else
                    "No hypothesis survived the held-out gate; do not promote to Stage 3."
                ),
            })
            try:
                lessons_out.unlink()
            except OSError:
                pass
        except Exception as e:
            # Lightweight fallback for minimal/partial input.
            research.update({
                "held_out_gate_run": False,
                "lesson": f"Lightweight check only (held-out gate skipped: {e}).",
            })
        return {"research": research}

    def _execute_builder(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Builder role: score a deliverable on the 6-trait rubric.

        Required input_data keys:
            - deliverable_markdown: str
        """
        deliverable = input_data.get("deliverable_markdown", "")
        result = score_evals(deliverable)
        return {"evals": result}


def main():
    """CLI entry point for Modex runtime."""
    import argparse
    parser = argparse.ArgumentParser(description="Modex 1-agent local runtime")
    parser.add_argument("--role", default="certifier",
                        choices=["lead", "researcher", "builder", "certifier"])
    parser.add_argument("--claim-present", action="store_true")
    parser.add_argument("--has-3-failure-modes", action="store_true")
    parser.add_argument("--has-evidence-trail", action="store_true")
    parser.add_argument("--antipatterns-clean", action="store_true")
    parser.add_argument("--claim-text", default="")
    parser.add_argument("--deliverable-path", default="")
    parser.add_argument("--input-json", default=None,
                        help="JSON file with input_data (alternative to flags)")
    args = parser.parse_args()
    if args.input_json:
        with open(args.input_json) as f:
            input_data = json.load(f)
    else:
        input_data = {
            "claim_present": args.claim_present,
            "has_3_failure_modes": args.has_3_failure_modes,
            "has_evidence_trail": args.has_evidence_trail,
            "antipatterns_clean": args.antipatterns_clean,
            "claim_text": args.claim_text,
            "deliverable_path": args.deliverable_path,
        }
    runtime = ModexRuntime(role=args.role)
    result = runtime.run(input_data)
    print(json.dumps(result.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()