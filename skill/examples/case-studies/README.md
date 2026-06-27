# Certified Case Studies — FDE Skill × DeepSCR

> **One case study per business-pro segment. Each carries a hand-computed FDE Assurance Score ≥85 and a verifiable SHA-256. Reproducible by any human with a text editor and a terminal.**

These case studies are the **public proof** that the FDE Skill produces auditable, comparable, RFP-grade deliverables. They transform the raw 6-Q examples (in `skill/examples/`) into full DeepSCR-certified artifacts: every claim is labeled `[MEASURED]` / `[HYPOTHESIS]` / `[ASSERTION]`, every architecture is falsified against held-out evidence, and every deliverable closes with a FDE Assurance Score + SHA-256.

---

## The 3 case studies

| Segment | Case study | Vertical | FDE Assurance Score | SHA-256 (prefix) |
|---|---|---|---|---|
| **Startup** (funding / growth) | [SaaS churn prediction](case-study-saas-churn.md) | B2B SaaS retention | **90/100 ✅** | `34090281…` |
| **SET / team** (operations quality) | [Retail demand forecasting](case-study-retail-forecasting.md) | 50-store retail chain | **91/100 ✅** | `1b5a0a19…` |
| **Enterprise** (procurement / risk) | [Fintech fraud detection](case-study-fintech-fraud.md) | Neobank real-time fraud | **93/100 ✅** | `b28d8fff…` |

---

## What each segment buys

- **Startup** — the FDE Assurance Score is the **due-diligence asset**. A founder hands an investor a scoping report where every number is labeled and falsifiable, carrying a 90/100 score. Comparable across startups on one 0-100 scale.
- **SET / team** — the FDE Assurance Score is the **quality gate**. A team adopts "no deliverable touches production without FDE Assurance Score ≥85." The retail case study speaks ops language (MAPE, SKU Pareto, runtime) and turns review objective.
- **Enterprise** — the FDE Assurance Score is the **procurement standard**. A risk officer writes "FDE Assurance Score ≥85 + held-out gate pass required" into a fraud-system RFP and verifies it by hand. The fintech case study quotes the literal gate (`fintech-fraud-golden-set.json`).

---

## How they were built (and how to verify them)

1. Each case study **starts from a 6-Q JSON** in `skill/examples/` — no reinvention. Claims are lifted and labeled by type.
2. Each applies the **4-stage DeepSCR loop** (Hypothesis → Contradiction → Verification → Certification), as proven in [`work/deepscr-4-stages-proof.md`](../../../work/deepscr-4-stages-proof.md).
3. Each FDE Assurance Score is **computed by hand** using the formula in [`skill/references/fde-trust-score.md`](../../references/fde-trust-score.md): `25×Claim + 25×Contradiction + 30×Evidence + 20×Anti-patterns`.
4. Each SHA-256 is a real `shasum -a 256` output, reproducible:

```bash
cd /Users/mehdiwhb/Documents/trae_projects/fde
shasum -a 256 skill/examples/case-studies/case-study-*.md
```

Expected:
```
1257f39963b929aaee65d382b785a5d4222d48071979ee4ecab6f9771f69888e  case-study-saas-churn.md
33fa4a3ee14e8c86b2c222bd8f214bb7e0f1d90ca7a850b9938ba85b52a04be3  case-study-retail-forecasting.md
0ed878da407c1c910fd3858c557952acf772f4b926fc10bde63829d54b40fa04  case-study-fintech-fraud.md
```

---

## What these are NOT

- **Not realized results.** The "$1.2M retained", "$240k saved", "$2.5M reduction" are all **projections** (labeled `[HYPOTHESIS]`), not measured outcomes. The FDE Assurance Score certifies *epistemic rigor* (claims honest, failures named, trail traceable), not that the projected dollars will materialize. Realization requires the held-out cohort eval and 90-day post-launch measurement named in each Stage 3.
- **Not customer engagements.** They are constructed from the skill's own example 6-Q data. They prove the *method* and the *output format*, not a specific customer's outcome.
- **Not marketing.** They are reference artifacts. The marketing surface (landing/academy) may cite them, but they exist first as **verifiable technical proof**.

---

## Next (once these are validated)

- An **Enterprise RFP clause** ready to copy-paste: *"All AI-generated deliverables must include an FDE Assurance Score ≥85 per the DeepSCR protocol, with a held-out gate pass where applicable. Verify with `shasum -a 256`."*
- A **Team Integration Guide**: how a SET enforces FDE Assurance Score ≥85 as a CI/CD quality gate (pre-commit hook refusing a deliverable without a `## FDE Assurance Score` section).
- Turning `manufacturing-notes.md` (the richest raw engagement material) into a 4th certified case study once structured into 6-Q.