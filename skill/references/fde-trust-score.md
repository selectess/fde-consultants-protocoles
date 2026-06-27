---
title: FDE Assurance Score — DeepSCR Protocol Applied
description: Operational scoring protocol for FDE deliverables, derived from the DeepSCR scientific method.
---

# FDE Assurance Score — DeepSCR Protocol Applied

> *"A claim without an evidence trail is a hypothesis, not a deliverable."*

This document defines the **FDE Assurance Score**, an operational scoring system that adapts the DeepSCR protocol (Deep Sceptical Contextual Research) to FDE deliverables. It is the technical backbone of [Operating Principle #14](../SKILL.md) of the FDE Skill.

## 1. The 4-Step DeepSCR Loop, FDE Version

For every deliverable (scoping report, prototype spec, production handoff, productization memo, code artifact), the Skill enforces this loop before the deliverable is considered complete:

```
┌─────────────────────────────────────────────────────────┐
│   Step 1: HYPOTHESE                                    │
│   State what the deliverable claims to prove.           │
│   Output: 1-sentence claim + 6-Q anchor.                │
├─────────────────────────────────────────────────────────┤
│   Step 2: CONTRADICTION (Skeptical Deployment)          │
│   Active attempt to falsify the claim.                  │
│   Output: List of failure modes + edge cases.           │
├─────────────────────────────────────────────────────────┤
│   Step 3: VERIFICATION                                 │
│   Cite concrete evidence: file, command, page, test.    │
│   Output: Evidence trail (paths + line ranges + hashes).│
├─────────────────────────────────────────────────────────┤
│   Step 4: CERTIFICATION                                │
│   Compute the FDE Assurance Score. If <60, return to Step 1.    │
│   Output: FDE Assurance Score (0-100) + SHA-256 of deliverable. │
└─────────────────────────────────────────────────────────┘
```

## 2. FDE Assurance Score Formula

```
FDE Assurance Score = round(
    25 * (Claim present and falsifiable)
  + 25 * (At least 3 failure modes documented)
  + 30 * (Evidence trail contains ≥1 file/command/test)
  + 20 * (Anti-patterns check passed; see SKILL.md §Anti-Patterns)
)
```

| Component | Weight | What it measures |
|---|---|---|
| **Claim** | 25 | Is the deliverable's claim explicit and testable? |
| **Contradiction** | 25 | Did the author attempt to falsify it (Skeptical Deployment)? |
| **Evidence** | 30 | Are there concrete pointers (file paths, commands, screenshots)? |
| **Anti-pattern check** | 20 | Did the deliverable avoid all 9 anti-patterns in SKILL.md? |

## 3. Decision Thresholds

| Score | Verdict | Action |
|---|---|---|
| **85-100** | ✅ Certified | Ship with FDE Assurance Score badge. |
| **60-84** | ⚠ Needs revision | Address the lowest component, then re-score. |
| **0-59** | ❌ Rejected | Return to Step 1 with new hypothesis. |

## 4. Worked Example: The 3 Entity Splinter Pages

The Skill itself was tested against this protocol during the Skeptical Deployment decision on a high-risk growth method.

| Step | Output | Score |
|---|---|---|
| 1. Hypothesis | "Three minimal HTML pages with JSON-LD + internal links can be indexed by Google in <7 days." | — |
| 2. Contradiction | Documented 5 failure modes in [fde-skeptical-deployment.md](fde-skeptical-deployment.md) §3 | +25 |
| 3. Verification | Concrete files exist: three test pages with JSON-LD and internal links | +30 |
| 4. Anti-pattern check | No "use AI" generic, no slides, no quantified trade-off missing | +20 |
| **Claim present?** | Yes (1-sentence in entity-splinter-test-3.html §"Decision rule") | +25 |
| **Total** | | **100** |

Decision: ship the 3 pages as the cheapest possible test, defer scaling.

## 5. Worked Examples: The 3 Certified Case Studies

Beyond the entity-splinter test above, the protocol has been applied to **three full case studies**, one per business-pro segment. Each starts from a raw 6-Q example, runs the full 4-stage DeepSCR loop, and closes with a hand-computed FDE Assurance Score + SHA-256. They live in [`examples/case-studies/`](../examples/case-studies/README.md).

| Segment | Case study | Vertical | FDE Assurance Score | Held-out gate? |
|---|---|---|---|---|
| **Startup** (due diligence) | [case-study-saas-churn.md](../examples/case-studies/case-study-saas-churn.md) | B2B SaaS retention | **90/100 ✅** | cohort gate (described) |
| **SET / team** (quality gate) | [case-study-retail-forecasting.md](../examples/case-studies/case-study-retail-forecasting.md) | Retail forecasting | **91/100 ✅** | SKU-cohort gate (described) |
| **Enterprise** (procurement) | [case-study-fintech-fraud.md](../examples/case-studies/case-study-fintech-fraud.md) | Neobank fraud | **93/100 ✅** | **literal gate file** ([fintech-fraud-golden-set.json](../examples/fintech-fraud-golden-set.json)) |

These three are the public proof that the FDE Assurance Score is not a single worked example but a **repeatable protocol** that produces comparable scores across industries and segments. The enterprise case study is the strongest: it quotes the held-out gate file literally, so the Contradiction step is a shipped artifact, not prose.

Verify them by hand:
```bash
cd <repo-root>
shasum -a 256 skill/examples/case-studies/case-study-*.md
```

## 6. How to Apply This in Practice

When you generate any FDE artifact, end it with a section titled `## FDE Assurance Score` that contains:

1. The 4-step loop summary (1 line each).
2. The computed FDE Assurance Score.
3. The SHA-256 hash of the deliverable file (use `shasum -a 256 <file>`).

If you cannot compute a FDE Assurance Score, you have not shipped a deliverable. You have shipped a hypothesis.

## 7. Why This Document Exists

DeepSCR was originally designed to certify arbitrary code via AWS Bedrock agents. The FDE Skill does not depend on Bedrock; instead, it encodes the same epistemic discipline (Hypothesis → Contradiction → Verification → Conclusion) as a portable, runtime-agnostic markdown protocol. This means:

- No external SaaS dependency.
- No paid API.
- Works in Claude Code, Cursor, Windsurf, Codex, Hermes, and any web LLM.
- The score is human-computable and verifiable.

This is the bridge between Deeposit's certification model and the FDE open-core distribution model.
