# SaaS Churn Prediction — Certified Case Study

**Segment**: Startup (funding / growth)
**Vertical**: B2B SaaS customer retention
**Source 6-Q**: [`skill/examples/saas-churn-prediction.json`](../saas-churn-prediction.json)
**Protocol**: [DeepSCR](../../references/fde-trust-score.md) · FDE Operating Principle #14
**FDE Assurance Score**: **90/100 ✅ Certified** (see §4)
**Date**: 2026-06-19

---

## Why this case study exists

This is a worked example of what an FDE Skill-powered agent produces for a **startup founder or VP Product** whose core survival metric is revenue retention. Every claim below is traceable to a 6-Q source, every architecture is falsified against held-out evidence, and the deliverable closes with a verifiable FDE Assurance Score. This is the "before/after": a SaaS team gets a scoping report that an investor can audit during due diligence — not a slide deck.

---

## Context (6-Q decomposition — sourced, not reinvented)

Source: [`saas-churn-prediction.json`](../saas-churn-prediction.json). Claims marked **[HYPOTHESIS]** (forward-looking), **[MEASURED]** (current baseline), or **[ASSERTION]** (stated, unverified).

| Q | Field | Value | Type |
|---|---|---|---|
| Q1 | Process | Customer churn prediction + intervention, B2B SaaS | [MEASURED] |
| Q1 | Volume | 5,000 MAU, **12% monthly churn** | [MEASURED] |
| Q1 | Owner | VP of Product | [MEASURED] |
| Q2 | Decision | classification + prescriptive | [MEASURED] |
| Q2 | Latency | < 5s per user | [HYPOTHÈSE — target] |
| Q2 | Accuracy | > 85% precision@10% | [HYPOTHÈSE — target] |
| Q3 | Data | 2 years behavior data, 150 features | [MEASURED] |
| Q3 | Quality | clean, no PII | [MEASURED] |
| Q3 | Compliance | GDPR/CCPA | [MEASURED] |
| Q4 | Cost | $200 per retained customer | [HYPOTHÈSE — LTV model] |
| Q4 | Distribution | 80% churn from mid-market | [ASSERTION] |
| Q5 | Current | manual, reactive CS, 5% recovery | [MEASURED] |
| Q6 | Primary metric | **$1.2M annual revenue retained** | [HYPOTHÈSE — projection] |
| Q6 | Threshold | > 30% reduction in churn | [HYPOTHÈSE — target] |

**Honesty note**: the headline "$1.2M retained" is a *projection*, not a realized result. DeepSCR requires this be stated explicitly (Stage 4 would otherwise over-certify).

---

## Stage 1 — Scoping (DeepSCR Step 1: Hypothesis)

**Falsifiable claim (1 sentence)**: *"A predictive churn model serving mid-market accounts (80% of churn) can reduce monthly churn from 12% to <8.4% within 90 days, retaining ~$1.2M ARR — falsified if measured churn reduction < 30% over two consecutive monthly cohorts."*

**Stakeholder RACI** (from q1_owner):
| Role | Who | Responsibility |
|---|---|---|
| Decision-maker | VP of Product | Signs off on intervention thresholds |
| Budget owner | Founder / CEO | Approves build spend |
| Daily user | Customer Success team | Acts on churn alerts |
| Technical owner | Eng lead | Maintains model + data pipeline |
| Risk blocker | Legal (GDPR) | Can block PII usage |

**Pain matrix + ROI**:
| Pain | Severity | Frequency | $/year | AI fit |
|---|---|---|---|---|
| Reactive CS (churn detected post-fact) | 5 | Daily | ~$1.2M lost ARR | High |
| No early warning | 4 | Weekly | (bundled) | High |
| 5% recovery rate | 4 | Monthly | (bundled) | High |

**ROI (hypothesis)**: ((1,200,000 − ~150,000 build+run) / 150,000) × 100 ≈ **700% Year 1** — *but unproven until measured; see §4*.

---

## Stage 2 — Prototyping (DeepSCR Step 2: Contradiction)

Three competing architecture hypotheses, falsified against the 6-Q constraints. Each carries its own failure modes.

### H1 — Rule-based alerting on usage decline
- **Traits**: simple, auditable, low_cost, fallback
- **Fit**: catches the obvious "login stopped" signal cheaply. Sets a measurable floor.
- **Failure modes**:
  1. Misses non-usage signals (billing downgrades, support sentiment) → under-detects.
  2. No prescriptive intervention → CS still guesses what to do.
  3. 5% recovery ceiling not broken by rules alone.

### H2 — Gradient boosting on 150 behavior features (recommended candidate)
- **Traits**: structured_features, production_ready, auditable, high_precision
- **Fit**: matches q2 (classification), exploits q3 (150 features, 2 yrs), meets q2 latency (<5s trivially).
- **Failure modes**:
  1. Feature drift as product changes → precision decays; needs monitoring.
  2. Cold-start: new users (<30 days) have thin feature history → under-served.
  3. "prescriptive" half of q2 not solved by a classifier alone — needs an intervention recommender on top.
  4. Mid-market focus (80% of churn) means the model must be *calibrated on mid-market labels*, not blended with enterprise/SMB.

### H3 — LLM-assisted churn commentary + intervention drafting
- **Traits**: semantic_context, explanation, human_review, slower
- **Fit**: solves the "prescriptive" gap (drafts save-play for CS), but not a numeric churn predictor.
- **Failure modes**:
  1. Latency budget (<5s) tight for an LLM call in-loop.
  2. Hallucinated interventions could erode CS trust.
  3. Cost per call may exceed the $200/retained-customer margin at scale.

### Held-out gate (what must be true before promoting H2)
Before H2 is promoted to Production:
- Measured precision@10% ≥ 85% on a **held-out monthly cohort** (not the training cohort).
- False-positive rate low enough that CS intervention cost < $200/retained-customer margin.
- Calibrated on mid-market labels (q4 distribution), not blended.

---

## Stage 3 — Production (DeepSCR Step 3: Verification)

Evidence trail — each falsifiable claim points to a concrete test:

| Claim | Evidence / falsifier |
|---|---|
| 12% monthly churn baseline | Segment analytics export, 2 trailing months — **falsified if ≠ 12% ±2** |
| 150 features usable | `feature_store` schema dump — falsified if >20% features >30% null |
| >85% precision@10% | Held-out cohort eval (Stage 2 gate) — falsified if <85% |
| >30% churn reduction | Two consecutive monthly cohorts post-launch — falsified if <30% |
| $1.2M retained | ARR retention report, 90 days post-launch — falsified if <$1.2M |
| GDPR compliance | PII redaction in feature pipeline — falsified by data-flow audit |

**Compliance map** (q3): GDPR/CCPA. PII redaction required in the feature pipeline; no special-scope data (no health/finance). Low regulatory friction → startup-friendly.

---

## Stage 4 — Feedback (DeepSCR Step 4: Certification)

FDE Assurance Score, computed by hand per [fde-trust-score.md](../../references/fde-trust-score.md): `25×Claim + 25×Contradiction + 30×Evidence + 20×Anti-patterns`.

| Component | Weight | Score | Reason |
|---|---|---|---|
| **Claim falsifiable** | 25 | 23 | 1-sentence claim anchored on Q6, with explicit falsifier (<30% reduction). Slight deduction: "$1.2M" is a projection, honestly labeled. |
| **Contradiction (≥3 failure modes)** | 25 | 25 | 3 architectures, each with ≥3 failure modes + held-out gate. |
| **Evidence trail (≥1 concrete)** | 30 | 24 | Each claim maps to a falsifier (Segment export, eval cohort, ARR report). Deduction: none of the evidence is *collected yet* — these are tests-to-run, not results. |
| **Anti-patterns check** | 20 | 18 | No "use AI" generic, no slides, no unquantified trade-off. Minor: ROI 700% is arithmetically derived from unproven inputs (honestly flagged). |

**FDE Assurance Score = 23 + 25 + 24 + 18 = 90/100 → ✅ Certified** (threshold ≥85)

**SHA-256** of this case study: see [`README.md`](README.md) registry.

**Limit**: this score certifies the **epistemic rigor** of the case study (claims honest, failures named, trail traceable, no anti-patterns). It does **not** certify that $1.2M will be retained — that requires the Stage-2 held-out cohort and 90-day post-launch measurement.

---

## Business outcome — why a startup buyer cares

For a **founder in a funding round**, this case study demonstrates the difference an FDE-certified scoping report makes:

- **Investor due diligence**: instead of a slide saying "we'll reduce churn 30%", the founder hands over a document where every number is labeled `[HYPOTHESIS]`/`[MEASURED]`, every architecture has named failure modes, and the deliverable carries a **verifiable 90/100 FDE Assurance Score + SHA-256**. The investor can reproduce the score by hand.
- **Auditable, not aspirational**: the "$1.2M retained" is explicitly a projection with a falsifier (two cohorts <30% → claim dies). This is the opposite of the optimistic pitch decks investors discount.
- **Comparable across startups**: two startups using FDE produce scoping reports scored on the **same 0-100 scale**. An investor can compare apples-to-apples — the analog of a credit score for technical scoping quality.

This is the FDE wedge for startups: **the FDE Assurance Score is the due-diligence asset.**
