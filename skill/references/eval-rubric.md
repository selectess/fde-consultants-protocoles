# FDE 6-Trait Eval Rubric

**Last updated**: 2026-06-18

The self-scoring rubric for every FDE deliverable. Use as LLM-as-judge prompt template.

---

## The 6 Traits

| # | Trait | What it means | Score 1 (fail) | Score 5 (exceptional) |
|---|---|---|---|---|
| 1 | **Customer Curiosity** | Shows real understanding of the user's world | Generic assumptions | Specific observations from real domain knowledge |
| 2 | **Ownership** | Commits to a concrete outcome | "Could be valuable" | "We'll deliver X by date Y, or we don't get paid" |
| 3 | **Decomposition** | Problem broken into testable pieces | Vague problem restated | 6-Q answered with numbers |
| 4 | **Empathy** | Reflects stakeholder reality | Ignores constraints | Names political, technical, organizational realities |
| 5 | **Product Sense** | Shippable, not theoretical | Slides without implementation | Working code + runbook |
| 6 | **Communication** | Translates between tech and business | Jargon-heavy or oversimplified | One exec summary + one technical detail, both clear |

---

## LLM-as-Judge Prompt Template

```markdown
# Eval Rubric Application

You are scoring an FDE deliverable on 6 traits. Be ruthless. Generic, vague, or theoretical work scores low.

## The Deliverable
[PASTE DELIVERABLE HERE]

## The Context
[Industry, customer profile, engagement stage]

## The 6 Traits — Score 1-5 each

### 1. Customer Curiosity (1-5)
- Does it show real understanding of the user's world?
- Does it reference specific industry facts, regulations, or competitive dynamics?
- Or is it generic advice that could apply to anyone?

Score: [1-5]
Justification: [Specific quotes or absences from the deliverable]

### 2. Ownership (1-5)
- Does it commit to a concrete outcome?
- Are there specific dates, numbers, deliverables?
- Or is it hedged with "could", "might", "potentially"?

Score: [1-5]
Justification: [...]

### 3. Decomposition (1-5)
- Is the problem broken into testable sub-problems?
- Are the 6-Qs (specific process, decision, data, cost of error, current system, success metric) answered?
- Or is the problem restated vaguely?

Score: [1-5]
Justification: [...]

### 4. Empathy (1-5)
- Does it acknowledge stakeholder realities (political, technical, organizational)?
- Does it propose changes the customer can actually adopt?
- Or does it ignore how the organization works?

Score: [1-5]
Justification: [...]

### 5. Product Sense (1-5)
- Is the recommendation shippable?
- Is there code, configuration, runbook — or just slides?
- Can a team start building tomorrow?

Score: [1-5]
Justification: [...]

### 6. Communication (1-5)
- Is there both an executive summary AND technical detail?
- Is it jargon-free where possible, precise where needed?
- Or is it either too high-level or too in-the-weeds?

Score: [1-5]
Justification: [...]

## Overall Verdict

PASS if:
- All 6 scores ≥ 3
- Ownership ≥ 4
- Decomposition ≥ 4
- No anti-pattern detected

FAIL otherwise.

If FAIL, list the top 3 specific changes that would make it pass.
```

---

## Anti-Pattern Detection

Scan every deliverable for these patterns. Auto-fail if any present:

| Anti-pattern | Regex / Heuristic | Example |
|---|---|---|
| **AI buzzword without substance** | "AI will transform" / "leverage AI" / "ML magic" | "Use AI to revolutionize customer service" |
| **No quantified trade-off** | No €/time/% in tradeoff | "Postgres is better for this use case" |
| **Slide-only deliverable** | No code, no runbook, no diagram | Just a 20-slide deck |
| **Recommendation without owner** | No name attached to action item | "Someone should..." |
| **Eval-less AI system** | AI system without eval framework | "Here's a RAG system" (no evals) |
| **"We'll figure it out later"** | Compliance, security, scale punted | "Add auth later" |
| **Hidden assumptions** | Unstated prerequisites | "Assuming clean data" |
| **Single-option recommendation** | No alternatives shown | "Use Kubernetes" (no others) |
| **No failure mode** | No "what could go wrong" | Architecture without failure analysis |

---

## Score Distribution Targets

For a healthy FDE practice over many deliverables:

| Trait | Median | P25 | P75 |
|---|---|---|---|
| Customer Curiosity | 4 | 3 | 5 |
| Ownership | 4 | 4 | 5 |
| Decomposition | 4 | 4 | 5 |
| Empathy | 4 | 3 | 4 |
| Product Sense | 4 | 3 | 5 |
| Communication | 4 | 4 | 5 |

**Red flag**: If a single trait consistently scores <3 across deliverables, that's a training/coaching gap.

---

## Score Examples

### Example 1 — PASS (exceptional)

**Deliverable**: Scoping report for AI-powered customer service triage at a SaaS company.

- Customer Curiosity: **5** — References specific industry (B2B SaaS support benchmarks, Zendesk 2026 trends)
- Ownership: **5** — "We commit to 60% auto-resolution in 90 days, or we extend free"
- Decomposition: **5** — All 6-Q answered with numbers (1000 tickets/day, $5/ticket, 60% baseline target)
- Empathy: **4** — Acknowledges support team morale risk, change management
- Product Sense: **4** — Includes code scaffold, eval framework, runbook
- Communication: **5** — Executive summary + technical detail + customer-facing FAQ

**Verdict**: PASS

### Example 2 — FAIL (typical)

**Deliverable**: "AI Strategy for Customer Service"

- Customer Curiosity: **2** — "Most companies could benefit from AI in support"
- Ownership: **2** — "We recommend exploring AI opportunities"
- Decomposition: **1** — No 6-Q answered
- Empathy: **2** — No mention of team, constraints, change management
- Product Sense: **1** — No code, no architecture, no runbook
- Communication: **3** — Clear writing, but nothing concrete to communicate

**Verdict**: FAIL — Reject. Rewrite with concrete numbers and shippable artifacts.

---

## Calibration Process

Every quarter:
1. Score 20 random deliverables with 3 different judges
2. Compute inter-rater agreement (Cohen's kappa >0.7 = good)
3. Compare scores to actual customer outcomes
4. Adjust rubric to favor traits that correlate with customer success

The rubric is a living artifact. It improves with data.

---

## Sources

- Vinoo Ganesh — 6 traits of exceptional FDEs
- Anthropic — Claude evaluation best practices
- Braintrust / Langfuse — LLM-as-judge patterns
- Our own engagement data (placeholder)

---

## Update Log

- 2026-06-18: Initial version.
