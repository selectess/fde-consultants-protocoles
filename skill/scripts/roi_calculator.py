#!/usr/bin/env python3
"""
ROI Calculator
==============

Calculates ROI for AI/tech projects with sensitivity analysis.

Usage:
    python roi_calculator.py --problem roi.json
    python roi_calculator.py --interactive

Output:
    Year 1/2/5 ROI, payback period, sensitivity analysis
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class ROISpec:
    """ROI calculation inputs."""
    # Baseline
    baseline_volume_per_period: float = 0
    baseline_period: str = "year"  # day/week/month/year
    baseline_cost_per_unit: float = 0
    baseline_cost_currency: str = "EUR"

    # AI system
    ai_auto_resolution_rate: float = 0.0  # 0-1, fraction auto-resolved
    ai_time_reduction_remaining: float = 0.0  # 0-1, time saved for non-auto
    ai_cost_per_task: float = 0.0
    ai_latency_improvement: str = ""

    # One-time costs
    build_cost: float = 0
    design_cost: float = 0
    infra_setup_cost: float = 0

    # Recurring costs
    llm_api_cost_per_year: float = 0
    infra_cost_per_year: float = 0
    maintenance_cost_per_year: float = 0  # typically 15-20% of build

    # Risk adjustments
    confidence: float = 0.7  # 0-1, baseline confidence in estimates

    # Optional: revenue enabled
    revenue_enabled_per_year: float = 0
    risk_reduced_per_year: float = 0


@dataclass
class ROIResult:
    """ROI calculation outputs."""
    annual_baseline_cost: float
    annual_ai_cost_savings: float
    annual_ai_running_cost: float
    annual_net_impact: float

    year_1_total_cost: float
    year_1_roi_percent: float
    year_2_roi_percent: float

    payback_months: float

    five_year_npv: float  # at 10% discount rate

    # Sensitivity
    optimistic_roi: float
    realistic_roi: float
    conservative_roi: float

    recommendations: List[str] = field(default_factory=list)


def calculate(spec: ROISpec, discount_rate: float = 0.10) -> ROIResult:
    """Calculate ROI from spec."""

    # Normalize baseline to annual
    period_multiplier = {
        "day": 365,
        "week": 52,
        "month": 12,
        "year": 1,
    }
    annual_volume = spec.baseline_volume_per_period * period_multiplier.get(spec.baseline_period, 1)
    annual_baseline_cost = annual_volume * spec.baseline_cost_per_unit

    # AI savings
    auto_resolved = annual_volume * spec.ai_auto_resolution_rate
    remaining = annual_volume - auto_resolved
    time_saved_on_remaining = remaining * spec.ai_time_reduction_remaining

    # Convert time saved back to cost
    # If baseline_cost_per_unit is fully time, then time_reduction saves that fraction
    cost_saved_on_remaining = time_saved_on_remaining * spec.baseline_cost_per_unit
    cost_saved_on_auto = auto_resolved * spec.baseline_cost_per_unit

    annual_savings = cost_saved_on_auto + cost_saved_on_remaining

    # Add revenue + risk reduction
    annual_savings += spec.revenue_enabled_per_year + spec.risk_reduced_per_year

    # Apply confidence
    annual_savings_realistic = annual_savings * spec.confidence

    # Costs
    annual_running_cost = (
        spec.llm_api_cost_per_year
        + spec.infra_cost_per_year
        + spec.maintenance_cost_per_year
    )
    year_1_one_time = spec.build_cost + spec.design_cost + spec.infra_setup_cost
    year_1_total_cost = year_1_one_time + annual_running_cost

    # Year 1
    year_1_net = annual_savings_realistic - year_1_total_cost
    year_1_roi = (year_1_net / year_1_total_cost * 100) if year_1_total_cost > 0 else 0

    # Year 2+
    year_2_net = annual_savings_realistic - annual_running_cost
    year_2_roi = (year_2_net / annual_running_cost * 100) if annual_running_cost > 0 else float('inf')

    # Payback period (months)
    if annual_savings_realistic > 0:
        months_to_payback = (year_1_total_cost / annual_savings_realistic) * 12
    else:
        months_to_payback = float('inf')

    # 5-year NPV
    cash_flows = []
    for year in range(1, 6):
        if year == 1:
            cf = year_1_net
        else:
            cf = annual_savings_realistic - annual_running_cost
        pv = cf / ((1 + discount_rate) ** year)
        cash_flows.append(pv)

    five_year_npv = sum(cash_flows)

    # Sensitivity
    # Optimistic: impact +20%, cost -10%
    optimistic_savings = annual_savings * 1.2
    optimistic_cost = year_1_total_cost * 0.9
    optimistic_roi = ((optimistic_savings - optimistic_cost) / optimistic_cost * 100) if optimistic_cost > 0 else 0

    # Conservative: impact -30%, cost +20%
    conservative_savings = annual_savings * 0.7
    conservative_cost = year_1_total_cost * 1.2
    conservative_roi = (
        (conservative_savings - conservative_cost) / conservative_cost * 100
        if conservative_cost > 0 else 0
    )

    # Recommendations
    recommendations = []
    if year_1_roi < 200:
        recommendations.append(
            "Year 1 ROI < 200% — consider whether this is the highest-leverage opportunity."
        )
    if months_to_payback > 12:
        recommendations.append(
            f"Payback period {months_to_payback:.1f} months — consider smaller pilot first."
        )
    if conservative_roi < 100:
        recommendations.append(
            "Conservative scenario ROI < 100% — high risk, validate assumptions with pilot."
        )
    if spec.confidence < 0.5:
        recommendations.append(
            "Confidence < 50% — gather more data before committing budget."
        )
    if not recommendations:
        recommendations.append("Strong business case. Recommend proceeding to prototype.")

    return ROIResult(
        annual_baseline_cost=annual_baseline_cost,
        annual_ai_cost_savings=annual_savings_realistic,
        annual_ai_running_cost=annual_running_cost,
        annual_net_impact=annual_savings_realistic - annual_running_cost,
        year_1_total_cost=year_1_total_cost,
        year_1_roi_percent=year_1_roi,
        year_2_roi_percent=year_2_roi,
        payback_months=months_to_payback,
        five_year_npv=five_year_npv,
        optimistic_roi=optimistic_roi,
        realistic_roi=year_1_roi,
        conservative_roi=conservative_roi,
        recommendations=recommendations,
    )


def print_report(spec: ROISpec, result: ROIResult):
    """Pretty-print ROI report."""
    print("=" * 70)
    print("ROI CALCULATION REPORT")
    print("=" * 70)
    print()
    print("BASELINE STATE")
    print(f"  Volume: {spec.baseline_volume_per_period:,.0f}/{spec.baseline_period}")
    print(f"  Cost per unit: {spec.baseline_cost_per_unit:.2f} {spec.baseline_cost_currency}")
    print(f"  Annual baseline cost: {result.annual_baseline_cost:,.0f} {spec.baseline_cost_currency}")
    print()
    print("AI SYSTEM ASSUMPTIONS")
    print(f"  Auto-resolution rate: {spec.ai_auto_resolution_rate*100:.0f}%")
    print(f"  Time reduction on remaining: {spec.ai_time_reduction_remaining*100:.0f}%")
    print(f"  Cost per AI task: {spec.ai_cost_per_task:.3f} {spec.baseline_cost_currency}")
    print(f"  Confidence in estimates: {spec.confidence*100:.0f}%")
    print()
    print("FINANCIAL IMPACT")
    print(f"  Annual AI savings (realistic): {result.annual_ai_cost_savings:,.0f} {spec.baseline_cost_currency}")
    print(f"  Annual running cost: {result.annual_ai_running_cost:,.0f} {spec.baseline_cost_currency}")
    print(f"  Annual net impact: {result.annual_net_impact:,.0f} {spec.baseline_cost_currency}")
    print()
    print("ROI METRICS")
    print(f"  Year 1 ROI: {result.year_1_roi_percent:,.0f}%")
    print(f"  Year 2+ ROI: {result.year_2_roi_percent:,.0f}%")
    print(f"  Payback period: {result.payback_months:.1f} months")
    print(f"  5-year NPV (10% discount): {result.five_year_npv:,.0f} {spec.baseline_cost_currency}")
    print()
    print("SENSITIVITY ANALYSIS")
    print(f"  Optimistic: {result.optimistic_roi:,.0f}% ROI")
    print(f"  Realistic:  {result.realistic_roi:,.0f}% ROI")
    print(f"  Conservative: {result.conservative_roi:,.0f}% ROI")
    print()
    print("RECOMMENDATIONS")
    for rec in result.recommendations:
        print(f"  • {rec}")
    print()
    print("=" * 70)


def interactive_mode():
    """Interactive ROI calculator."""
    print("=" * 70)
    print("ROI CALCULATOR — Interactive")
    print("=" * 70)
    print()

    spec = ROISpec()

    # Baseline
    spec.baseline_volume_per_period = float(input("Baseline volume per period? (e.g., 1000): "))
    spec.baseline_period = input("Period? (day/week/month/year) [year]: ").strip() or "year"
    spec.baseline_cost_per_unit = float(input("Baseline cost per unit? (e.g., 5.0 EUR): "))

    # AI system
    spec.ai_auto_resolution_rate = float(input("AI auto-resolution rate? (0-1, e.g., 0.6): "))
    spec.ai_time_reduction_remaining = float(input("Time reduction on remaining? (0-1, e.g., 0.5): "))

    # Costs
    spec.build_cost = float(input("Build cost (one-time)?: "))
    spec.llm_api_cost_per_year = float(input("LLM API cost per year?: "))
    spec.infra_cost_per_year = float(input("Infra cost per year?: "))
    spec.maintenance_cost_per_year = spec.build_cost * 0.18  # default 18%

    # Confidence
    spec.confidence = float(input("Confidence in estimates? (0-1, default 0.7): ") or "0.7")

    return spec


def main():
    parser = argparse.ArgumentParser(description="ROI Calculator for AI/tech projects")
    parser.add_argument("--problem", type=str, help="Path to JSON config/problem file")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    if args.interactive:
        spec = interactive_mode()
    elif args.problem:
        with open(args.problem) as f:
            data = json.load(f)
        spec = ROISpec(**data)
    else:
        parser.print_help()
        sys.exit(1)

    result = calculate(spec)
    print_report(spec, result)


if __name__ == "__main__":
    main()
