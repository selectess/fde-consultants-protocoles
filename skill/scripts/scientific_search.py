"""
scientific_search.py - FDE-native scientific hypothesis refinement.

This script translates scientific research logic into FDE work without requiring
any external research runtime:

1. Generate several architecture hypotheses instead of betting on one PoC.
2. Evaluate each hypothesis on development evidence from the 6-Q scoping data.
3. Promote only candidates that pass a separate held-out validation gate.
4. Turn rejected hypotheses into reusable lessons for future engagements.

Usage:
    python3 scripts/scientific_search.py --problem examples/fintech-fraud-detection.json
    python3 scripts/scientific_search.py --problem examples/fintech-fraud-detection.json \
        --golden-set examples/fintech-fraud-golden-set.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEV_PROMOTION_THRESHOLD = 55


@dataclass(frozen=True)
class Hypothesis:
    """One candidate architecture in the FDE prototype search."""

    hypothesis_id: str
    description: str
    branch_label: str
    traits: tuple[str, ...]
    tradeoffs: tuple[str, ...]


class FDEExecutor:
    """Short-lived evaluator for one FDE hypothesis."""

    def __init__(self, hypothesis: Hypothesis):
        self.hypothesis = hypothesis

    def evaluate(self, problem: dict[str, Any], golden_cases: list[dict[str, Any]]) -> dict[str, Any]:
        dev_score, dev_rationale = self._score_development_evidence(problem)
        golden = self._score_held_out_gate(golden_cases)
        dev_pass = dev_score >= DEV_PROMOTION_THRESHOLD
        promoted = dev_pass and golden["passed"]
        prune_reason = None
        if not dev_pass:
            prune_reason = f"development score below {DEV_PROMOTION_THRESHOLD}"
        elif not golden["passed"]:
            failed = [case["id"] for case in golden["cases"] if not case["passed"]]
            prune_reason = "held-out gate failed: " + ", ".join(failed)

        return {
            "hypothesis_id": self.hypothesis.hypothesis_id,
            "description": self.hypothesis.description,
            "branch_label": self.hypothesis.branch_label,
            "traits": list(self.hypothesis.traits),
            "tradeoffs": list(self.hypothesis.tradeoffs),
            "development_score": dev_score,
            "development_passed": dev_pass,
            "development_rationale": dev_rationale,
            "held_out_score": golden["score"],
            "held_out_passed": golden["passed"],
            "held_out_cases": golden["cases"],
            "promoted": promoted,
            "prune_reason": prune_reason,
            "lesson": self._lesson_from_result(promoted, prune_reason),
        }

    def _score_development_evidence(self, problem: dict[str, Any]) -> tuple[int, list[str]]:
        text = json.dumps(problem, ensure_ascii=False).lower()
        q2 = (problem.get("q2_decision_type", "") + " " + problem.get("q2_accuracy_target", "")).lower()
        q3 = (
            problem.get("q3_volume", "")
            + " "
            + problem.get("q3_quality", "")
            + " "
            + problem.get("q3_refresh", "")
        ).lower()
        q4 = (problem.get("q4_direct_cost", "") + " " + problem.get("q4_regulatory", "")).lower()
        latency = (problem.get("q2_latency", "") + " " + problem.get("q6_threshold", "")).lower()
        traits = set(self.hypothesis.traits)
        score = 20
        rationale = ["base: every candidate starts at 20"]

        if any(token in q3 for token in ["clean", "curated", "labeled", "labelled", "highly", "3 years", "500k"]):
            score += 20
            rationale.append("Q3: usable historical data supports prototype evaluation (+20)")
        else:
            rationale.append("Q3: data quality is not strong enough for a large model")

        if any(token in q4 for token in ["regulatory", "fine", "hipaa", "pci", "gdpr", "medical", "breach", "$", "€"]):
            score += 15
            rationale.append("Q4: high error/regulatory cost requires disciplined evaluation (+15)")

        if "classification" in q2:
            if "structured_features" in traits:
                score += 20
                rationale.append("Q2: structured classification fits feature-based ML (+20)")
            elif "high_precision" in traits:
                score += 15
                rationale.append("Q2: high-precision model family is plausible (+15)")
            elif "semantic_context" in traits:
                score += 6
                rationale.append("Q2: semantic context may help, but classification is not primarily a chat task (+6)")
        elif "regression" in q2 or "forecast" in text:
            if "forecasting" in traits or "structured_features" in traits:
                score += 20
                rationale.append("Q2: forecasting/regression fits structured or time-series modeling (+20)")
            elif "semantic_context" in traits:
                score += 4
                rationale.append("Q2: LLM forecasting is exploratory, not primary evidence (+4)")
        else:
            if "agentic_workflow" in traits:
                score += 18
                rationale.append("Q2: ambiguous workflow may benefit from an agentic tool loop (+18)")
            elif "simple" in traits:
                score += 10
                rationale.append("Q2: simple baseline is useful for proving a floor (+10)")

        if any(token in latency for token in ["< 200ms", "<200ms", "< 1s", "<1s"]):
            if "low_latency" in traits:
                score += 15
                rationale.append("Latency: candidate can plausibly meet strict latency (+15)")
            if "slower" in traits or "high_cost" in traits:
                score -= 20
                rationale.append("Latency: candidate is too slow/costly for the constraint (-20)")
            if "requires_gpu" in traits:
                score -= 8
                rationale.append("Latency: GPU dependency raises serving risk (-8)")
        elif any(token in latency for token in ["seconds", "minutes"]):
            if "human_review" in traits or "explanation" in traits:
                score += 8
                rationale.append("Latency: review/explanation is acceptable within the time budget (+8)")

        if "production_ready" in traits:
            score += 12
            rationale.append("Delivery: production-ready trait improves Stage 3 handoff (+12)")
        if "auditable" in traits and any(token in q4 for token in ["regulatory", "hipaa", "pci", "gdpr", "audit"]):
            score += 10
            rationale.append("Governance: auditability matches regulated context (+10)")

        return max(0, min(100, score)), rationale

    def _score_held_out_gate(self, golden_cases: list[dict[str, Any]]) -> dict[str, Any]:
        traits = set(self.hypothesis.traits)
        case_results = []
        weighted_total = 0.0
        weight_sum = 0.0
        all_passed = True

        for case in golden_cases:
            required = set(case.get("required_traits", []))
            avoided = set(case.get("avoid_traits", []))
            minimum = int(case.get("minimum_score", 60))
            weight = float(case.get("weight", 1.0))
            matched = sorted(required & traits)
            missing = sorted(required - traits)
            violations = sorted(avoided & traits)
            base = 100 if not required else round(100 * len(matched) / len(required))
            score = max(0, base - 20 * len(violations))
            passed = score >= minimum and not violations
            all_passed = all_passed and passed
            weighted_total += score * weight
            weight_sum += weight
            case_results.append(
                {
                    "id": case.get("id", "unnamed-case"),
                    "description": case.get("description", ""),
                    "required_traits": sorted(required),
                    "avoid_traits": sorted(avoided),
                    "matched_traits": matched,
                    "missing_traits": missing,
                    "violated_traits": violations,
                    "minimum_score": minimum,
                    "score": score,
                    "passed": passed,
                }
            )

        average = round(weighted_total / weight_sum) if weight_sum else 0
        return {"score": average, "passed": all_passed, "cases": case_results}

    def _lesson_from_result(self, promoted: bool, prune_reason: str | None) -> str:
        if promoted:
            return "Promoted: keep this pattern as a candidate template for similar FDE engagements."
        if not prune_reason:
            return "Rejected: evidence was insufficient for promotion."
        if "held-out" in prune_reason:
            return "Rejected by held-out validation: update the playbook with the constraint that failed outside the dev evidence."
        return "Rejected by development evidence: improve scoping data or choose a simpler architecture before prototyping."


class FDECoordinator:
    """Long-lived coordinator that turns FDE prototyping into scientific search."""

    def __init__(self, problem: dict[str, Any], golden_cases: list[dict[str, Any]], lessons_out: Path):
        self.problem = problem
        self.golden_cases = golden_cases
        self.lessons_out = lessons_out
        self.hypothesis_tree: list[Hypothesis] = []
        self.results: list[dict[str, Any]] = []
        self.best: dict[str, Any] | None = None

    def generate_hypothesis_tree(self) -> list[Hypothesis]:
        q2 = self.problem.get("q2_decision_type", "").lower()

        if "classification" in q2:
            self.hypothesis_tree = [
                Hypothesis(
                    "H1",
                    "Baseline rules/logistic model with interpretable features",
                    "fde/h1-baseline",
                    ("low_latency", "auditable", "simple", "low_cost", "fallback"),
                    ("fast to ship", "sets a measurable floor", "may miss complex patterns"),
                ),
                Hypothesis(
                    "H2",
                    "Gradient boosting with engineered domain features",
                    "fde/h2-feature-boosting",
                    ("low_latency", "structured_features", "auditable", "production_ready", "high_precision", "low_cost"),
                    ("strong tabular baseline", "good handoff path", "requires feature governance"),
                ),
                Hypothesis(
                    "H3",
                    "Fine-tuned transformer for complex pattern detection",
                    "fde/h3-transformer",
                    ("high_precision", "complex_patterns", "requires_gpu", "higher_cost", "less_auditable"),
                    ("can capture weak signals", "serving and explainability risk", "needs robust evals"),
                ),
                Hypothesis(
                    "H4",
                    "Agentic LLM/RAG review loop for ambiguous cases",
                    "fde/h4-agentic-review",
                    ("semantic_context", "explanation", "tool_use", "human_review", "high_cost", "slower", "needs_governance"),
                    ("useful for escalation", "not ideal as primary low-latency classifier", "requires strict tool permissions"),
                ),
            ]
        elif "regression" in q2 or "forecast" in q2:
            self.hypothesis_tree = [
                Hypothesis(
                    "H1",
                    "Baseline moving average / ARIMA forecast",
                    "fde/h1-arima",
                    ("forecasting", "simple", "auditable", "low_cost", "fallback"),
                    ("transparent baseline", "limited nonlinear signal capture"),
                ),
                Hypothesis(
                    "H2",
                    "Gradient boosting with lagged and external features",
                    "fde/h2-forecast-boosting",
                    ("forecasting", "structured_features", "production_ready", "auditable", "low_cost"),
                    ("strong practical forecast", "depends on feature freshness"),
                ),
                Hypothesis(
                    "H3",
                    "Temporal transformer for high-volume time series",
                    "fde/h3-temporal-transformer",
                    ("forecasting", "complex_patterns", "requires_gpu", "higher_cost"),
                    ("can capture seasonality", "harder handoff", "higher serving cost"),
                ),
                Hypothesis(
                    "H4",
                    "LLM-assisted forecasting commentary layer",
                    "fde/h4-llm-commentary",
                    ("semantic_context", "explanation", "human_review", "slower"),
                    ("useful for analyst narrative", "not a primary numeric forecaster"),
                ),
            ]
        else:
            self.hypothesis_tree = [
                Hypothesis(
                    "H1",
                    "Rule-based workflow automation baseline",
                    "fde/h1-rules",
                    ("simple", "auditable", "low_cost", "fallback"),
                    ("fast to prove", "low intelligence ceiling"),
                ),
                Hypothesis(
                    "H2",
                    "Classical ML service with explicit acceptance tests",
                    "fde/h2-classical-ml",
                    ("structured_features", "production_ready", "auditable", "low_cost"),
                    ("good for measurable workflows", "requires labeled data"),
                ),
                Hypothesis(
                    "H3",
                    "Agentic workflow with tools and human review gates",
                    "fde/h3-agentic-workflow",
                    ("agentic_workflow", "tool_use", "human_review", "needs_governance", "explanation"),
                    ("good for multi-step work", "must constrain permissions"),
                ),
                Hypothesis(
                    "H4",
                    "RAG assistant with retrieval and escalation",
                    "fde/h4-rag-assistant",
                    ("semantic_context", "explanation", "human_review", "slower"),
                    ("useful when knowledge access is the bottleneck", "not enough for transactional automation"),
                ),
            ]
        return self.hypothesis_tree

    def run_htr(self) -> dict[str, Any]:
        print("\n" + "=" * 76)
        print("FDE SCIENTIFIC SEARCH - hypothesis refinement, held-out promotion")
        print("=" * 76)
        print(f"Problem (Q1): {self.problem.get('q1_process', 'N/A')[:96]}")
        print(f"Decision (Q2): {self.problem.get('q2_decision_type', 'N/A')}")
        print(f"Data (Q3): {self.problem.get('q3_volume', 'N/A')[:96]}")
        print(f"Held-out cases: {len(self.golden_cases)}")
        print("=" * 76)

        print("\n[Coordinator] Generating candidate architecture hypotheses...")
        self.generate_hypothesis_tree()
        for hypothesis in self.hypothesis_tree:
            print(f"  - {hypothesis.hypothesis_id}: {hypothesis.description} [{hypothesis.branch_label}]")

        print("\n[Coordinator] Running development evidence + HELD-OUT GATE...")
        for hypothesis in self.hypothesis_tree:
            result = FDEExecutor(hypothesis).evaluate(self.problem, self.golden_cases)
            self.results.append(result)
            status = "PROMOTED" if result["promoted"] else "PRUNED"
            print(
                "  [{branch}] {status} dev={dev}/100 held_out={held}/100 - {desc}".format(
                    branch=result["branch_label"],
                    status=status,
                    dev=result["development_score"],
                    held=result["held_out_score"],
                    desc=result["description"][:78],
                )
            )
            if result["prune_reason"]:
                print(f"      reason: {result['prune_reason']}")

        promoted = [result for result in self.results if result["promoted"]]
        self.best = max(promoted, key=lambda result: (result["held_out_score"], result["development_score"]), default=None)
        lessons = self._write_lessons()

        print("\n" + "=" * 76)
        print("[Coordinator] SCIENTIFIC SEARCH COMPLETE")
        if self.best:
            print(f"  Best hypothesis: {self.best['hypothesis_id']} - {self.best['description']}")
            print(f"  Development score: {self.best['development_score']}/100")
            print(f"  Held-out score: {self.best['held_out_score']}/100")
            print("  Promote to: Prototype Spec only after recording held-out validation results")
        else:
            print("  No hypothesis passed the held-out merge gate. Do not promote to Stage 3.")
        print(f"  Lessons written: {self.lessons_out}")
        print("=" * 76)

        return {
            "problem": self.problem.get("q1_process", ""),
            "tree_size": len(self.hypothesis_tree),
            "held_out_cases": len(self.golden_cases),
            "results": self.results,
            "best_hypothesis": self.best,
            "lessons_out": str(self.lessons_out),
            "lessons_count": len(lessons["lessons"]),
        }

    def _write_lessons(self) -> dict[str, Any]:
        rejected = [result for result in self.results if not result["promoted"]]
        payload = {
            "schema": "fde-scientific-search-lessons-v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "problem": self.problem.get("q1_process", ""),
            "promoted_hypothesis_id": self.best["hypothesis_id"] if self.best else None,
            "lessons": [
                {
                    "hypothesis_id": result["hypothesis_id"],
                    "description": result["description"],
                    "prune_reason": result["prune_reason"],
                    "lesson": result["lesson"],
                    "failed_cases": [case["id"] for case in result["held_out_cases"] if not case["passed"]],
                    "playbook_update": self._playbook_update(result),
                }
                for result in rejected
            ],
        }
        self.lessons_out.parent.mkdir(parents=True, exist_ok=True)
        self.lessons_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return payload

    def _playbook_update(self, result: dict[str, Any]) -> str:
        failed_cases = [case for case in result["held_out_cases"] if not case["passed"]]
        if not failed_cases:
            return "Record why development evidence was insufficient before expanding the search tree."
        missing = sorted({trait for case in failed_cases for trait in case.get("missing_traits", [])})
        violated = sorted({trait for case in failed_cases for trait in case.get("violated_traits", [])})
        parts = []
        if missing:
            parts.append("missing traits: " + ", ".join(missing))
        if violated:
            parts.append("violated traits: " + ", ".join(violated))
        return "For similar engagements, reject this pattern unless it resolves " + "; ".join(parts) + "."


def load_problem(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Problem file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Problem file must contain a JSON object")
    return data


def load_golden_cases(path: Path | None, problem: dict[str, Any]) -> list[dict[str, Any]]:
    if path is None:
        return default_golden_cases(problem)
    if not path.exists():
        raise FileNotFoundError(f"Golden set file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        cases = payload.get("cases", [])
    elif isinstance(payload, list):
        cases = payload
    else:
        raise ValueError("Golden set must be a list or an object with a 'cases' list")
    if not cases:
        raise ValueError("Golden set contains no cases")
    for case in cases:
        if "id" not in case or "required_traits" not in case:
            raise ValueError("Each golden case needs 'id' and 'required_traits'")
    return cases


def default_golden_cases(problem: dict[str, Any]) -> list[dict[str, Any]]:
    """Create conservative held-out checks from the 6-Q data when no file is provided."""
    q2 = (problem.get("q2_decision_type", "") + " " + problem.get("q2_accuracy_target", "")).lower()
    q4 = (problem.get("q4_direct_cost", "") + " " + problem.get("q4_regulatory", "")).lower()
    latency = (problem.get("q2_latency", "") + " " + problem.get("q6_threshold", "")).lower()
    cases: list[dict[str, Any]] = []

    if "classification" in q2 or "accuracy" in q2 or "precision" in q2:
        cases.append(
            {
                "id": "heldout-quality-target",
                "description": "Candidate must support the primary quality target on unseen cases.",
                "required_traits": ["high_precision"],
                "minimum_score": 60,
                "weight": 1.2,
            }
        )
    elif "regression" in q2 or "forecast" in q2:
        cases.append(
            {
                "id": "heldout-forecast-target",
                "description": "Candidate must support numeric forecast validation on unseen periods.",
                "required_traits": ["forecasting"],
                "minimum_score": 60,
                "weight": 1.2,
            }
        )
    else:
        cases.append(
            {
                "id": "heldout-workflow-target",
                "description": "Candidate must produce an operable workflow artifact, not only advice.",
                "required_traits": ["production_ready"],
                "minimum_score": 50,
            }
        )

    if any(token in latency for token in ["< 200ms", "<200ms", "< 1s", "<1s", "seconds"]):
        cases.append(
            {
                "id": "heldout-operational-constraint",
                "description": "Candidate must survive the latency and operating constraint.",
                "required_traits": ["low_latency"],
                "avoid_traits": ["slower", "high_cost"],
                "minimum_score": 60,
            }
        )

    if any(token in q4 for token in ["regulatory", "fine", "hipaa", "pci", "gdpr", "audit", "breach"]):
        cases.append(
            {
                "id": "heldout-governance-constraint",
                "description": "Candidate must be auditable enough for regulated or high-cost errors.",
                "required_traits": ["auditable", "production_ready"],
                "avoid_traits": ["less_auditable"],
                "minimum_score": 50,
            }
        )

    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="FDE scientific search with held-out promotion")
    parser.add_argument("--problem", required=True, help="Path to 6-Q FDE scoping JSON file")
    parser.add_argument("--golden-set", help="Optional held-out validation JSON. If omitted, conservative cases are derived from 6-Q.")
    parser.add_argument("--lessons-out", default=".fde_lessons.json", help="Where to write rejected-hypothesis lessons")
    args = parser.parse_args()

    try:
        problem = load_problem(Path(args.problem))
        golden_cases = load_golden_cases(Path(args.golden_set) if args.golden_set else None, problem)
        coordinator = FDECoordinator(problem, golden_cases, Path(args.lessons_out))
        summary = coordinator.run_htr()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("\nFinal summary JSON:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
