# Scoping Report Template

> **Use**: Stage 1 output. One per engagement. Maximum 5 pages (1-page exec summary + 4 pages detail).
>
> **Mandatory closure**: every scoping report MUST end with a `## FDE Assurance Score` section (see [references/fde-trust-score.md](../references/fde-trust-score.md)). A scoping report without a FDE Assurance Score is a hypothesis, not a deliverable.

---

# [Project Name] — Scoping Report

**Date**: [YYYY-MM-DD]
**Author**: [FDE name / AI agent]
**Customer**: [Company name]
**Engagement Type**: [New Project / Startup / Business Upgrade]
**Stage**: 1 of 4 (Scoping)

---

## Executive Summary (1 page)

**Problem**: [One sentence — the specific process and its cost]

**Opportunity**: [One sentence — the AI/system solution and its projected impact]

**Recommendation**: [GO / NO-GO / FURTHER RESEARCH needed]

**Key Numbers**:
- Estimated annual impact: €[X]
- Estimated build cost: €[Y]
- Estimated payback: [Z] months
- Confidence: [High / Medium / Low]

**Risks** (top 3):
1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

**Next Step**: [Scoping → Prototype / More research / Stop]

---

## 1. Customer Context

### 1.1 Company Snapshot

| Field | Value |
|---|---|
| Industry | [vertical, sub-vertical] |
| Size | [employees, revenue, growth rate] |
| Stage | [seed / growth / mature / declining] |
| Geography | [markets served] |
| Strategic priorities (12 months) | [...] |

### 1.2 Stakeholder Map (RACI)

| Role | Name | Responsibility |
|---|---|---|
| **Decision-maker** | [name] | Signs off on engagement |
| **Budget owner** | [name] | Approves spend |
| **Daily user** | [name/role] | Will use the system |
| **Technical owner** | [name/role] | Will maintain after handoff |
| **Risk blocker** | [name/role] | Can kill the project (legal, IT, exec) |

### 1.3 Engagement Type

- [ ] **New Project** — building from scratch
- [ ] **Startup** — accelerating an existing team
- [ ] **Business Upgrade** — transforming an existing process

---

## 2. The Problem (Decomposed via 6-Q)

### Q1 — Specific Process
[Description, volume, frequency, owner]

### Q2 — Decision / Output
[Type, latency target, accuracy target]

### Q3 — Data Availability
[Volume, quality, compliance, refresh, format]

### Q4 — Cost of Error
[Direct cost, indirect cost, regulatory, distribution]

### Q5 — Current System
[Type, performance, frustrations]

### Q6 — Success Metric
[Primary metric, threshold, measurement plan]

---

## 3. Pain-Point Matrix

| Pain | Severity (1-5) | Frequency | Cost/year (€) | AI Opportunity |
|---|---|---|---|---|
| [Pain 1] | 5 | Daily | €X | High |
| [Pain 2] | 4 | Weekly | €Y | Medium |
| [Pain 3] | 3 | Monthly | €Z | Low |

---

## 4. Opportunity Sizing

### 4.1 Impact Estimate

```
Baseline state:
- [Metric 1]: [value]
- [Metric 2]: [value]

Future state (post-AI):
- [Metric 1]: [value] ([+/-]X%)
- [Metric 2]: [value] ([+/-]Y%)

Annual financial impact:
- Direct savings: €[A]
- Revenue enabled: €[B]
- Risk reduced: €[C]
- Total: €[A+B+C]
```

### 4.2 Cost Estimate

```
Build (one-time):
- Engineering: €[X]
- Infrastructure setup: €[Y]
- Design / UX: €[Z]
- Subtotal: €[X+Y+Z]

Run (annual):
- LLM API: €[A]
- Infrastructure: €[B]
- Maintenance (15-20% of build): €[C]
- Subtotal: €[A+B+C]

Year 1 total: €[build + run]
Year 2+ annual: €[run]
```

### 4.3 ROI Calculation

```
Year 1 ROI: ((Impact - Cost) / Cost) × 100%
Year 2+ ROI: ((Impact - Annual Cost) / Annual Cost) × 100%
Payback period: [months]
5-year NPV (at 10% discount): €[value]
```

### 4.4 Sensitivity Analysis

| Scenario | Impact | Cost | ROI | Recommendation |
|---|---|---|---|---|
| **Optimistic** (impact +20%) | €X | €Y | Z% | Stretch goal |
| **Realistic** (as estimated) | €X | €Y | Z% | Plan target |
| **Conservative** (impact -30%) | €X | €Y | Z% | Floor target |

**Decision threshold**: Proceed if conservative scenario ROI > 200%.

---

## 5. Recommended Approach

### 5.1 Solution Direction
[2-3 sentences on the proposed approach]

### 5.2 Tech Stack Recommendation (high level)

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | [...] | [...] |
| Backend | [...] | [...] |
| AI Layer | [...] | [...] |
| Infrastructure | [...] | [...] |
| Observability | [...] | [...] |

### 5.3 Architecture Sketch

[Mermaid diagram here — see template structure]

### 5.4 Key Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| [Risk 1] | Medium | High | [mitigation] |
| [Risk 2] | Low | High | [mitigation] |
| [Risk 3] | Medium | Medium | [mitigation] |

---

## 6. 90-Day Roadmap (High Level)

### Stage 2 — Prototyping (Days 11-30)
- [Milestone 1]
- [Milestone 2]
- [Milestone 3]

### Stage 3 — Production (Days 31-90)
- [Milestone 1]
- [Milestone 2]
- [Milestone 3]

### Stage 4 — Feedback (Day 91+)
- KPI tracking starts
- Weekly digest
- Productization analysis

---

## 7. Open Questions

- [Question 1 that needs customer input before proceeding]
- [Question 2]
- [Question 3]

---

## 8. Recommendation

**[GO / NO-GO / FURTHER RESEARCH]**

**Rationale**: [2-3 sentences]

**If GO**: Propose kickoff date for Stage 2.
**If FURTHER RESEARCH**: Specify what needs to be learned (cost: [X days / €Y]).

---

## Appendix A — Sources Cited

- [Source 1 — domain research]
- [Source 2]
- [Source 3]

## Appendix B — Stakeholder Interview Notes

[Link to discovery interview notes]

## Appendix C — Raw Dossier

[Link to domain dossier from `prompts/domain-research.md`]

---

## FDE Assurance Score

Every scoping report must close with a FDE Assurance Score (FDE Operating Principle #14, [DeepSCR protocol](../references/fde-trust-score.md)). Compute by hand:

```
FDE Assurance Score = 25×(Claim falsifiable, 1 sentence anchored on Q6)
            + 25×(≥3 failure modes documented above)
            + 30×(Evidence trail ≥1 concrete pointer: file/command/test)
            + 20×(Anti-patterns check passed — see SKILL.md §Anti-Patterns)
```

| Component | Score | Reason |
|---|---|---|
| Claim (falsifiable) | /25 | |
| Contradiction (≥3 failure modes) | /25 | |
| Evidence trail | /30 | |
| Anti-patterns check | /20 | |
| **Total** | **/100** | |

| Score | Verdict | Action |
|---|---|---|
| 85-100 | ✅ Certified | Advance to Stage 2 (Prototype Spec) |
| 60-84 | ⚠ Needs revision | Address the lowest component, re-score |
| 0-59 | ❌ Rejected | Return to Stage 1 with a new claim |

**SHA-256** (run `shasum -a 256 <this file>`): ______
**Verdict**: ______

---

**Next deliverable**: Prototype Spec (Stage 2 output, if GO)
