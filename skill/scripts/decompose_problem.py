#!/usr/bin/env python3
"""
Decompose Problem Validator
============================

Stage 1c of Scoping — validates that a vague problem has been decomposed
into the 6-Q framework with concrete, quantified answers.

Usage:
    python decompose_problem.py --problem problem.json
    python decompose_problem.py --interactive

Output:
    Validation report + concrete-ness score (0-100)
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ProblemSpec:
    """The 6-Q decomposed problem specification."""
    q1_process: str = ""           # Specific process
    q1_volume: str = ""            # e.g., "1000/day"
    q1_owner: str = ""             # Who owns it

    q2_decision_type: str = ""     # classification/ranking/generation/recommendation/prediction
    q2_latency: str = ""           # e.g., "<1s", "batch"
    q2_accuracy_target: str = ""   # e.g., ">90%"

    q3_volume: str = ""            # e.g., "100k records, 50GB"
    q3_quality: str = ""           # clean/messy/unlabeled/partial
    q3_compliance: str = ""        # PII/PHI/regulated/none
    q3_refresh: str = ""           # real-time/daily/static

    q4_direct_cost: str = ""       # e.g., "$50 per wrong decision"
    q4_regulatory: str = ""        # e.g., "GDPR fines up to €500k"
    q4_distribution: str = ""      # e.g., "95% safe, 5% catastrophic"

    q5_current_type: str = ""      # manual/rules/ML/vendor/spreadsheet
    q5_current_performance: str = ""  # e.g., "85% accuracy, 10min turnaround"
    q5_frustrations: str = ""      # Top frustrations

    q6_primary_metric: str = ""    # e.g., "€100k/year saved"
    q6_threshold: str = ""         # e.g., ">200% ROI"
    q6_measurement: str = ""       # How measured


def score_concreteness(spec: ProblemSpec) -> dict:
    """
    Score the concreteness of a problem spec.

    Returns a dict with:
        - overall_score: 0-100
        - missing_fields: list of empty fields
        - warnings: list of issues to fix
    """
    fields = asdict(spec)
    total = len(fields)
    filled = sum(1 for v in fields.values() if v and v.strip())

    missing = [k for k, v in fields.items() if not v or not v.strip()]

    # Heuristics for warnings
    warnings = []

    # Q2 should have a specific decision type (accept subtypes like "binary classification")
    _q2 = (spec.q2_decision_type or "").lower()
    if spec.q2_decision_type and not any(
        _q2.startswith(t) or t in _q2 for t in (
            "classification", "ranking", "generation", "recommendation",
            "prediction", "regression", "forecast",
        )
    ):
        warnings.append(
            f"Q2 decision type '{spec.q2_decision_type}' should be one of: "
            "classification, ranking, generation, recommendation, prediction, regression, forecast"
        )

    # Q4 should have quantified cost
    if spec.q4_direct_cost and not any(c.isdigit() for c in spec.q4_direct_cost):
        warnings.append(f"Q4 direct cost should be quantified: '{spec.q4_direct_cost}'")

    # Q5 should describe current performance
    if spec.q5_current_performance and not any(c.isdigit() for c in spec.q5_current_performance):
        warnings.append(f"Q5 current performance should be quantified: '{spec.q5_current_performance}'")

    # Q6 should have a threshold
    if spec.q6_threshold and not any(c.isdigit() for c in spec.q6_threshold):
        warnings.append(f"Q6 threshold should be quantified: '{spec.q6_threshold}'")

    overall_score = int((filled / total) * 100)

    return {
        "overall_score": overall_score,
        "filled_count": filled,
        "total_count": total,
        "missing_fields": missing,
        "warnings": warnings,
        "is_ready": overall_score >= 80 and len(warnings) == 0,
    }


def interactive_mode():
    """Walk the user through the 6-Q framework interactively."""
    print("=" * 70)
    print("PROBLEM DECOMPOSITION — 6-Q Framework")
    print("=" * 70)
    print()
    print("This tool helps you transform a vague problem into a concrete spec.")
    print("Answer each question as specifically as possible.")
    print()

    spec = ProblemSpec()

    # Q1
    print("Q1 — THE SPECIFIC PROCESS")
    print("-" * 70)
    spec.q1_process = input("What specific process are you targeting? (Not 'everything', ONE process): ").strip()
    spec.q1_volume = input("Volume/frequency? (e.g., '1000/day', '50/week'): ").strip()
    spec.q1_owner = input("Who currently owns this process? (role/title): ").strip()
    print()

    # Q2
    print("Q2 — THE DECISION / OUTPUT TYPE")
    print("-" * 70)
    spec.q2_decision_type = input(
        "Decision type? (classification / ranking / generation / recommendation / prediction): "
    ).strip().lower()
    spec.q2_latency = input("Latency requirement? (e.g., '<1s real-time', 'batch daily'): ").strip()
    spec.q2_accuracy_target = input("Accuracy target? (e.g., '>90%'): ").strip()
    print()

    # Q3
    print("Q3 — DATA AVAILABILITY")
    print("-" * 70)
    spec.q3_volume = input("Data volume? (e.g., '100k records', '50GB', '10M events/day'): ").strip()
    spec.q3_quality = input("Data quality? (clean / messy / unlabeled / partial): ").strip()
    spec.q3_compliance = input("Compliance constraints? (PII / PHI / regulated / none): ").strip()
    spec.q3_refresh = input("Data refresh rate? (real-time / daily batch / static): ").strip()
    print()

    # Q4
    print("Q4 — COST OF ERROR")
    print("-" * 70)
    spec.q4_direct_cost = input("Direct cost per wrong decision? (e.g., '$50', '2hr rework'): ").strip()
    spec.q4_regulatory = input("Regulatory exposure? (e.g., 'GDPR fines €500k', 'safety risk'): ").strip()
    spec.q4_distribution = input("Error distribution? (e.g., '95% safe, 5% catastrophic'): ").strip()
    print()

    # Q5
    print("Q5 — CURRENT SYSTEM")
    print("-" * 70)
    spec.q5_current_type = input(
        "Current system type? (manual / rules-based / ML model / vendor SaaS / spreadsheet): "
    ).strip().lower()
    spec.q5_current_performance = input(
        "Current performance? (e.g., '85% accuracy, 10min turnaround'): "
    ).strip()
    spec.q5_frustrations = input("Top frustrations with current system? (comma-separated): ").strip()
    print()

    # Q6
    print("Q6 — SUCCESS METRIC")
    print("-" * 70)
    spec.q6_primary_metric = input("Primary success metric? (e.g., '€100k/year saved', '10hr/week freed'): ").strip()
    spec.q6_threshold = input("Success threshold? (e.g., '>200% ROI', '>90% accuracy'): ").strip()
    spec.q6_measurement = input("How will you measure this? (e.g., 'quarterly review', 'dashboard'): ").strip()
    print()

    return spec


def load_from_file(path: str) -> ProblemSpec:
    """Load problem spec from JSON file."""
    with open(path) as f:
        data = json.load(f)
    return ProblemSpec(**data)


def main():
    parser = argparse.ArgumentParser(
        description="Validate 6-Q problem decomposition",
    )
    parser.add_argument(
        "--problem",
        help="Path to JSON file with problem spec",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Walk through 6-Q interactively",
    )

    args = parser.parse_args()

    if args.interactive:
        spec = interactive_mode()
    elif args.problem:
        spec = load_from_file(args.problem)
    else:
        parser.print_help()
        sys.exit(1)

    # Score
    result = score_concreteness(spec)

    # Output
    print("=" * 70)
    print("DECOMPOSITION VALIDATION REPORT")
    print("=" * 70)
    print()
    print(f"Overall Concreteness Score: {result['overall_score']}/100")
    print(f"Filled Fields: {result['filled_count']}/{result['total_count']}")
    print()

    if result['is_ready']:
        print("✅ READY — Problem is sufficiently concrete to proceed.")
    else:
        print("❌ NOT READY — Problem needs more concreteness.")
        print()
        if result['missing_fields']:
            print("Missing fields:")
            for field in result['missing_fields']:
                print(f"  - {field}")
        if result['warnings']:
            print()
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")

    print()
    print("=" * 70)
    print("PROBLEM SPEC")
    print("=" * 70)
    print(json.dumps(asdict(spec), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
