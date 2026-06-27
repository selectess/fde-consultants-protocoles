# Productization Memo Template

> **Use**: Stage 4 output. Identify custom work that should become reusable IP.
>
> **Mandatory closure**: every productization memo MUST end with a `## FDE Assurance Score` section (see [references/fde-trust-score.md](../references/fde-trust-score.md)). The 4-metric FDE scorecard (deal velocity, NRR, productization rate, reusable-asset ratio) is the Verification step.

---

# [Project Name] — Productization Memo

**Date**: [YYYY-MM-DD]
**Stage**: 4 of 4 (Feedback / Productization)
**Memo Author**: [FDE name]

---

## 1. Executive Summary

**Top 3 candidates for productization**:

| # | Candidate | Reusability | Effort to Extract | ROI |
|---|---|---|---|---|
| 1 | [Name] | High | Low | High |
| 2 | [Name] | High | Medium | High |
| 3 | [Name] | Medium | Low | Medium |

**Recommended action**: Extract [Candidate 1] this quarter. Estimated impact: €[X/year] across [N] future engagements.

---

## 2. Productization Scoring Framework

Each candidate scored on 4 dimensions:

| Dimension | Score (1-5) | Definition |
|---|---|---|
| **Reusability** | [X] | How many future engagements need this? |
| **Extraction effort** | [X] | Inverse — higher score = less effort |
| **ROI** | [X] | Time saved × value per engagement |
| **Strategic fit** | [X] | Aligned with our productization roadmap? |

**Priority Score** = (Reusability × ROI × Strategic fit) / Extraction effort

---

## 3. Candidate Analysis

### Candidate 1: [Name]

**Description**: [What is this thing? Why was it built custom?]

**Built for**: [Engagement name, date]

**Why reusable**: [How many other engagements would benefit? Be specific.]

**Extraction plan**:
1. [Step 1 — refactor for reusability]
2. [Step 2 — write docs + tests]
3. [Step 3 — open-source or internal release]
4. [Step 4 — usage tracking]

**Effort estimate**: [X person-weeks]

**ROI projection**:
- Saves [Y hours] per future engagement
- Used in [Z] engagements over next 12 months
- Value: €[amount]
- Build cost: €[amount]
- ROI: [X]%

**Strategic fit**: [Why this aligns with our productization direction]

**Decision**: [EXTRACT / DEFER / SKIP]

---

### Candidate 2: [Name]
[Same structure]

### Candidate 3: [Name]
[Same structure]

---

## 4. Field Insights (Customer → Core Product)

Insights that should feed back to core product / methodology:

### Insight 1
- **Observation**: [What we saw in the field]
- **Implication**: [What this means for our approach]
- **Recommendation**: [Specific change to make]

### Insight 2
[Same structure]

### Insight 3
[Same structure]

---

## 5. Failure → Insight Log

Use this section when Stage 2 ran scientific hypothesis refinement with
`scripts/scientific_search.py`.

**Lessons source**: `.fde_lessons.json`

| Rejected Hypothesis | Why It Failed | Reusable Lesson | Playbook/Template Update |
|---|---|---|---|
| [H1] | [held-out case or development evidence] | [what we learned] | [file/section to update] |
| [H2] | [...] | [...] | [...] |

**Patterns to preserve**:
- [Example: RAG/agentic review is useful for escalation, not primary low-latency classification.]
- [Example: transformer candidate needs stronger auditability before regulated deployment.]

**Methodology change recommended**:
- [Add/update a question, benchmark, template section, eval case, or Academy lesson.]

---

## 6. Updated Playbooks

Based on this engagement, these playbooks should be updated:

- [ ] `references/fde-methodology.md` — [what to add]
- [ ] `references/tech-stacks-2026.md` — [what to add]
- [ ] `prompts/discovery-interview.md` — [what to add]
- [ ] `templates/*.md` — [what to add]

---

## 7. 4-Metric Scorecard (Final)

| Metric | Target | Actual | Notes |
|---|---|---|---|
| Deal velocity | ≤90 days | [...] | [...] |
| NRR | ≥130% | [...] | [...] |
| Productization rate | ≥1 | [...] | This memo is one productization output |
| Reusable-asset ratio | ≥70% | [...] | [...] |

---

## 8. Next Steps

- [ ] Share this memo with product team
- [ ] Schedule extraction kickoff for top candidate
- [ ] Update internal playbooks
- [ ] Capture customer reference (with permission)

---

## Appendix A — Engagement Retrospective

What went well:
- [...]

What went poorly:
- [...]

What we'd do differently:
- [...]

---

## FDE Assurance Score

Every productization memo must close with a FDE Assurance Score (FDE Operating Principle #14, [DeepSCR protocol](../references/fde-trust-score.md)). Compute by hand:

```
FDE Assurance Score = 25×(Claim falsifiable — e.g. "candidate X yields ROI ≥ Y over Z engagements")
            + 25×(≥3 failure modes for the productization decision documented above)
            + 30×(Evidence trail ≥1 concrete pointer: engagement data / metrics / file:line)
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
| 85-100 | ✅ Certified | Productize the candidate as reusable IP |
| 60-84 | ⚠ Needs revision | Address the lowest component, re-score |
| 0-59 | ❌ Rejected | Do not productize; revisit at the next engagement |

**SHA-256** (run `shasum -a 256 <this file>`): ______
**Verdict**: ______
