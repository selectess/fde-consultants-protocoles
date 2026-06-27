# Retail Demand Forecasting — Certified Case Study

**Segment**: SET / team (operations & engineering quality)
**Vertical**: Mid-market retail supply chain
**Source 6-Q**: [`skill/examples/retail-demand-forecasting.json`](../retail-demand-forecasting.json)
**Protocol**: [DeepSCR](../../references/fde-trust-score.md) · FDE Operating Principle #14
**FDE Assurance Score**: **91/100 ✅ Certified** (see §4)
**Date**: 2026-06-19

---

## Why this case study exists

This is a worked example of what an FDE Skill-powered agent produces for a **team lead / VP Supply Chain / eng manager** who wants to replace an Excel moving-average baseline with a defensible forecasting system. It speaks the operational language a mid-market ops team expects (MAPE, SKU Pareto, runtime budget, manual-hours), and it closes with a verifiable FDE Assurance Score. This is the "quality gate" story: a team can require FDE Assurance Score ≥85 on any forecasting deliverable before it touches production.

---

## Context (6-Q decomposition — sourced, not reinvented)

Source: [`retail-demand-forecasting.json`](../retail-demand-forecasting.json). Claims marked **[HYPOTHESIS]** / **[MEASURED]** / **[ASSERTION]**.

| Q | Field | Value | Type |
|---|---|---|---|
| Q1 | Process | Demand forecasting, 50-store chain | [MEASURED] |
| Q1 | Volume | 10k SKUs, daily updates | [MEASURED] |
| Q1 | Owner | VP of Supply Chain | [MEASURED] |
| Q2 | Decision | regression (units/SKU/store/week) | [MEASURED] |
| Q2 | Latency | <15 min full forecast run | [HYPOTHÈSE — target] |
| Q2 | Accuracy | >85% weighted MAPE, top 20% SKUs | [HYPOTHÈSE — target] |
| Q3 | Data | 5 yrs POS + inventory + weather + events | [MEASURED] |
| Q3 | Quality | clean, 100% stores, no PII | [MEASURED] |
| Q3 | Compliance | PCI DSS only if payment data (not used) → low risk | [MEASURED] |
| Q4 | Cost | **$50k/month overstock/stockout** ($600k/yr) | [ASSERTION] |
| Q4 | Distribution | 70% losses from top 100 SKUs | [ASSERTION] |
| Q5 | Current | Excel moving average, 75% MAPE, 4h manual/week | [MEASURED] |
| Q6 | Primary | 40% loss reduction, <30 min manual/week | [HYPOTHÈSE — target] |
| Q6 | Threshold | >85% MAPE top 20%, <15 min runtime | [HYPOTHÈSE — target] |

**Honesty note**: $50k/month loss and "70% from top 100 SKUs" are stated as facts but unverified — they must be confirmed from the inventory/shrink report before the ROI claim is certified.

---

## Stage 1 — Scoping (DeepSCR Step 1: Hypothesis)

**Falsifiable claim (1 sentence)**: *"A regression model targeting the top 100 SKUs (70% of losses) can raise weighted MAPE from 75% to >85% and cut overstock/stockout losses by 40% (~$20k/month) within one season — falsified if measured MAPE on the top-20% SKU cohort stays <85% over 8 consecutive weekly forecasts."*

**Stakeholder RACI** (from q1_owner):
| Role | Who | Responsibility |
|---|---|---|
| Decision-maker | VP of Supply Chain | Signs off on forecast trust + reorder policy |
| Budget owner | COO / Finance | Approves build + infra spend |
| Daily user | Demand planners | Override/interpret forecasts |
| Technical owner | Data/Eng team | Pipeline + model maintenance |
| Risk blocker | Merchandising lead | Can reject if new-product forecasts hurt launches |

**Pain matrix + ROI**:
| Pain | Severity | Frequency | $/year | AI fit |
|---|---|---|---|---|
| 75% MAPE → overstock/stockout | 5 | Monthly | ~$600k | High |
| 4h/week manual forecast work | 3 | Weekly | ~52 × planner hrs | Medium |
| Inaccurate for new products | 4 | Per launch | (margin loss) | Medium |

**ROI (hypothesis)**: 40% of $600k = ~$240k/yr saved. Build ~$80k + ~$15k/yr run. **Year 1 ~170%, Year 2+ ~1500%** — *unproven until measured; see §4*.

---

## Stage 2 — Prototyping (DeepSCR Step 2: Contradiction)

Three competing architecture hypotheses, each falsified against the 6-Q constraints (regression, top-SKU focus, <15 min runtime, 5 yrs POS data).

### H1 — Seasonal naive / moving-average baseline (the floor to beat)
- **Traits**: simple, auditable, low_cost, fallback
- **Fit**: this is literally the *current* Excel system (q5). Its purpose is to set the floor: any candidate must beat it or be rejected.
- **Failure modes**:
  1. Already the baseline — by definition cannot improve on itself.
  2. Cannot incorporate weather/events signals (q3 data wasted).
  3. Fails on new products (q5 frustration), which is where margin leaks.

### H2 — Gradient boosting with lagged + external features (recommended candidate)
- **Traits**: forecasting, structured_features, production_ready, auditable, low_cost
- **Fit**: matches q2 (regression), exploits q3 (5 yrs POS + weather + events), trivially meets q2 latency (<15 min for 10k SKUs).
- **Failure modes**:
  1. Cold-start on new SKUs / new stores → top-20% focus must exclude or flag cold SKUs.
  2. Feature freshness dependency: weather/events feed latency can break the 2 AM refresh (q3_refresh).
  3. "70% from top 100 SKUs" Pareto means the model must be **evaluated on that cohort specifically**, not blended across all 10k SKUs (which would dilute the metric).
  4. Overfitting to 5 years of POS data if promo calendar shifts → needs time-series cross-validation, not random split.

### H3 — Temporal transformer for high-volume SKUs
- **Traits**: forecasting, complex_patterns, requires_gpu, higher_cost
- **Fit**: could capture complex seasonality + event interactions, but overkill for a 50-store, 10k-SKU problem.
- **Failure modes**:
  1. GPU serving cost may exceed the $20k/month savings margin.
  2. Harder handoff to a small eng team (q5 → low ML maturity).
  3. <15 min runtime budget tight for transformer inference on 10k SKUs.

### Held-out gate (before H2 is promoted to Production)
- Measured weighted MAPE on **top-20% SKU held-out weeks** ≥ 85% (q2/q6 target), not blended MAPE.
- Runtime on a production-sized batch (10k SKUs × 50 stores) < 15 min.
- New-product (cold-SKU) forecasts flagged separately and excluded from the headline metric until they have ≥4 weeks of history.

---

## Stage 3 — Production (DeepSCR Step 3: Verification)

Evidence trail — each falsifiable claim points to a concrete test:

| Claim | Evidence / falsifier |
|---|---|
| 75% MAPE baseline | Excel forecast vs actuals, last 8 weeks — **falsified if MAPE ≠ 75% ±5** |
| $50k/month losses | Inventory shrink + stockout report, 3 trailing months — falsified if ≠ $50k ±$10k |
| 70% losses from top 100 SKUs | Pareto analysis on the loss report — falsified if ratio <60% |
| >85% MAPE top 20% SKUs | Held-out weekly eval (Stage 2 gate) — falsified if <85% over 8 weeks |
| <15 min runtime | Timed production batch run — falsified if >15 min |
| 40% loss reduction | 8-week post-launch shrink/stockout delta — falsified if <40% |
| <30 min manual work/week | Planner time-log — falsified if >30 min |

**Compliance map** (q3): PCI DSS only applies if payment data is used — it isn't (POS units only), so risk is low. No health/finance special-scope data. Low regulatory friction → team-friendly.

---

## Stage 4 — Feedback (DeepSCR Step 4: Certification)

FDE Assurance Score, computed by hand per [fde-trust-score.md](../../references/fde-trust-score.md): `25×Claim + 25×Contradiction + 30×Evidence + 20×Anti-patterns`.

| Component | Weight | Score | Reason |
|---|---|---|---|
| **Claim falsifiable** | 25 | 25 | 1-sentence claim anchored on Q2/Q6, with explicit falsifier (8-week MAPE <85% → claim dies). Pareto focus (top 100 SKUs) is specific. |
| **Contradiction (≥3 failure modes)** | 25 | 25 | 3 architectures, each with ≥3 failure modes + cohort-specific held-out gate. |
| **Evidence trail (≥1 concrete)** | 30 | 25 | Each claim maps to a falsifier (loss report, timed run, MAPE eval). Strong: baseline + target both operationally measurable. Deduction: evidence is tests-to-run, not results-yet-collected. |
| **Anti-patterns check** | 20 | 16 | No "use AI" generic, no slides. Minor deduction: ROI 170%/1500% derived from unproven $50k/month and 40% reduction (both flagged as [ASSERTION]/[HYPOTHESIS]). |

**FDE Assurance Score = 25 + 25 + 25 + 16 = 91/100 → ✅ Certified** (threshold ≥85)

**SHA-256** of this case study: see [`README.md`](README.md) registry.

**Limit**: certifies the **epistemic rigor** of the forecasting plan (baseline honest, Pareto focus explicit, runtime budget testable, failure modes named). Does **not** certify that 40% loss reduction will materialize — that needs the 8-week post-launch measurement.

---

## Business outcome — why a SET / team buyer cares

For a **team lead / VP Supply Chain / eng manager**, this case study demonstrates the FDE wedge for teams:

- **Quality gate, not just a model**: the team can adopt the rule "no forecasting deliverable touches production unless it carries a FDE Assurance Score ≥85." It's the supply-chain equivalent of a lint gate — but for epistemic rigor. A junior planner's spreadsheet forecast and an eng team's ML forecast are scored on the **same 0-100 scale**, making review objective.
- **Operational language**: MAPE, SKU Pareto, runtime budget, manual-hours — this case study speaks the team's dialect, so it's adoptable without translation. The held-out gate ("evaluate on top-20% SKU weeks, not blended") is a concrete review rule, not a platitude.
- **Auditable handoff**: every number is labeled `[MEASURED]`/`[HYPOTHESIS]`/`[ASSERTION]` with a falsifier. When the VP Supply Chain asks "how do you know it'll save $240k?", the answer is a traceable trail, not "trust the model."
- **Comparable across teams**: two retail chains (or two teams inside one) using FDE produce forecasting plans on the same scale. A COO can benchmark team output quality objectively — the analog of an ISO 9001 audit, but per-deliverable and computable by hand.

This is the FDE wedge for SETs/teams: **the FDE Assurance Score is the quality gate.**
