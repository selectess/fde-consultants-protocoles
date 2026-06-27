# FDE Methodology — Deep Reference

The Forward Deployed Engineering discipline originated at Palantir (~2010) and has been adopted by OpenAI, Anthropic, Microsoft, Databricks, Scale AI, Harvey, Cohere, Mistral, and 100+ Series A AI startups.

## Why This Methodology Exists

> *"You can't easily hire your way to a true FDE organization. The skill set is too rare, too specific. Traditional engineering jobs don't build this skill set because they're structured to insulate engineers from customer reality."*
> — Vinoo Ganesh, creator of Palantir's Project Frontline (sent 250+ engineers into live deployments)

The fundamental insight: **most engineering is insulated from the customer**. FDEs are not.

## The 4-Stage Loop

```
┌──────────────────────────────────────────────────────────┐
│  1. SCOPING        Days 1-10     Vague → Concrete        │
│     ↓                                                    │
│  2. PROTOTYPING    Days 11-30    Idea → Working demo     │
│     ↓                                                    │
│  3. DEPLOYMENT     Days 31-90    Demo → Production       │
│     ↓                                                    │
│  4. FEEDBACK       Continuous    Production → Insight    │
└──────────────────────────────────────────────────────────┘
```

### Stage 1 — SCOPING (Days 1-10)

**Goal**: Transform a vague problem into a concrete, scoped, sized opportunity.

**Inputs**:
- Customer's stated problem ("we want AI")
- Observed context (industry, competitors, constraints)

**Process**:
1. **Domain research** — read industry reports, talk to practitioners, understand the actual landscape
2. **Stakeholder mapping** — who decides, who uses, who pays, who can kill
2. **Decomposition** — vague problem → 6 specific questions answered
3. **Sizing** — € saved, hours saved, risk reduced

**Principle (Doubt First, Then Ship)**: Before producing any artifact or adopting a method (AI Overviews, NADE, etc.), an FDE must explicitly question what could make the chosen path a dead-end. Document this as a "Failure Modes" list in the scoping report before shipping. See [fde-skeptical-deployment.md](fde-skeptical-deployment.md).
   
**Outputs**:
- 1-page scoping report
- Concrete spec (testable, falsifiable)
- Stakeholder map
- Pain-point matrix

**Failure modes**:
- ❌ Accepting the stated problem without decomposition
- ❌ Optimizing for the wrong stakeholder
- ❌ Building a solution before sizing the opportunity
- ❌ Confusing "interesting" with "valuable"

### Stage 2 — PROTOTYPING (Days 11-30)

**Goal**: Build the smallest thing that proves or disproves the hypothesis.

**Inputs**:
- Scoping report
- Concrete spec

**Process**:
1. **Stack selection** — pick the fastest path to a working demo
2. **Architecture** — draw the boxes, name the boundaries
3. **Scientific search** — when several architectures are plausible, generate competing hypotheses and compare them before code hardens
4. **Eval framework** — define success/failure BEFORE building
5. **Held-out promotion gate** — keep a golden set separate from development evidence; no candidate moves to Stage 3 unless it passes
6. **Build** — ship code, not slides
7. **Demo** — show to the actual end users, not just the buyer

**Outputs**:
- Working demo on real customer data
- Eval baseline numbers
- Held-out validation results for the promoted hypothesis
- Rejected-hypothesis lessons captured in `.fde_lessons.json`
- Architecture diagram
- Integration plan

**Failure modes**:
- ❌ Demo on toy data, not customer data
- ❌ No eval framework (can't tell if it works)
- ❌ Promoting the most impressive architecture before it passes held-out constraints
- ❌ Throwing away failed hypotheses instead of turning them into reusable lessons
- ❌ Over-engineering the prototype
- ❌ Showing demo to execs only, not end users

### Stage 3 — DEPLOYMENT (Days 31-90)

**Goal**: Move the working demo to production-grade, secure, observable, cost-controlled.

**Inputs**:
- Working prototype
- Customer's production environment

**Process**:
1. **Hardening** — error handling, retries, idempotency, timeouts
2. **Security review** — auth, secrets, encryption, audit logs, AI Act compliance
3. **Observability** — logs, metrics, traces, evals in production
4. **Cost engineering** — projections at 1×, 10×, 100× scale
5. **Knowledge transfer** — customer's team can own it after we leave

**Outputs**:
- Production-deployed system
- Runbooks
- ADRs (architecture decision records)
- Eval dashboards
- Cost projections

**Failure modes**:
- ❌ "It worked in dev, ship it"
- ❌ No eval in production (can't tell if it still works)
- ❌ Single-region, no disaster recovery
- ❌ Customer team can't maintain it

### Stage 4 — FEEDBACK (Continuous)

**Goal**: Capture insights from production to feed back into product and methodology.

**Inputs**:
- Production telemetry
- User feedback
- Customer team interactions

**Process**:
1. **Track 4-metric scorecard** (velocity, NRR, productization rate, reusable-asset ratio)
2. **Identify productization candidates** — what custom work is reusable across customers?
3. **Capture field insights** — what surprised us? What's the customer doing that we didn't expect?
4. **Feed back to core product** — the company's own engineering team benefits from FDE insights

**Outputs**:
- Weekly KPI digest
- Productization memo (top 3 candidates)
- Field insights report
- Updated playbooks

**Failure modes**:
- ❌ FDE insights don't make it back to product team
- ❌ Custom work stays custom (no productization)
- ❌ No measurement of customer outcomes
- ❌ FDE team becomes a cost center, not a learning engine

---

## The 4-Metric FDE Scorecard

Every engagement is measured on:

| Metric | Definition | Target |
|---|---|---|
| **Deal Velocity** | Kickoff → Production | ≤ 90 days |
| **NRR on Engagement** | Net revenue retention on customer | ≥ 130% |
| **Productization Rate** | Reusable features extracted per engagement | ≥ 1.0 |
| **Reusable-Asset Ratio** | % of codebase in shared repo | ≥ 70% by month 12 |

These metrics force FDEs to:
- Ship fast (velocity)
- Drive expansion (NRR)
- Build reusable IP (productization)
- Contribute to core (reusable-asset ratio)

---

## The 6 Traits of an Exceptional FDE

Per Vinoo Ganesh, distilled from 250+ trained FDEs:

1. **Relentless Customer Curiosity**
   - Become a user before becoming a builder
   - Spend time on the factory floor, in the war room, with the spreadsheet
   - Surface problems the customer gave up on or never articulated

2. **Radical Ownership**
   - Whatever it takes
   - The customer's outcome is your outcome
   - Don't blame "the requirements" or "the timeline"

3. **Problem Decomposition**
   - Vague → concrete in 30 minutes
   - Break every problem into testable sub-problems
   - Identify the highest-uncertainty assumption first

4. **Customer Empathy**
   - Understand the politics, the constraints, the history
   - Don't ship something the customer can't maintain
   - Respect what already exists

5. **Product Sense**
   - Ship what's useful, not what's elegant
   - Cut scope aggressively
   - The best architecture is the one that ships

6. **Communication**
   - Translate between tech and business
   - One update = one decision
   - Don't hide uncertainty; name it

---

## The Decomposition Framework (6-Q)

Every vague problem MUST pass through these 6 questions before any solution is proposed:

```
Q1: What is the SPECIFIC process?
    Bad: "improve customer service"
    Good: "triage tier-1 support tickets for the SaaS product line"

Q2: What is the decision/output?
    Bad: "be smarter"
    Good: "classify each ticket into one of 8 categories with >90% accuracy"

Q3: What data is available?
    Bad: "we have data"
    Good: "120k historical tickets with labels, avg 200 words each, English only,
           PII redacted, 24-month retention"

Q4: What is the cost of error?
    Bad: "errors are bad"
    Good: "misclassification costs €15/ticket in re-routing + 2hr customer wait;
           regulatory exposure on PII leakage is €500k fine per incident"

Q5: What is the current system?
    Bad: "manual"
    Good: "2 human agents, avg 8min per ticket, 14hr backlog, 88% first-pass accuracy"

Q6: What is the success metric?
    Bad: "better"
    Good: ">92% accuracy + <30s response + €0.50/ticket cost + 80% auto-resolution"
```

**Until all 6 are answered with numbers, the problem is not yet scoped.**

---

## The Stratigraphic Question Pattern

Questions should NOT be generic. They should show domain mastery:

❌ **Generic**:
- "Tell me about your business"
- "What are your biggest challenges?"
- "What's your budget?"

✅ **Stratigraphic**:
- "I noticed your industry is moving from batch to continuous processing. Does your target process run batch or continuous? Because that changes the latency target by 100×."
- "Given that AI Act EU 2026 classifies your use case as high-risk, you'll need a conformity assessment. Have you budgeted for that compliance overhead?"
- "The last three PoCs in your space failed at the eval baseline, not at the model choice. What's your current accuracy on [specific task]?"

**Pattern**: `[Observed industry fact] + [Inference about user's context] + [Specific question]`

---

## The Anti-Patterns (Kill the Project)

| Anti-Pattern | Symptom | Fix |
|---|---|---|
| **Slide Engineering** | Lots of decks, no code | Force demo on real data |
| **Generic AI Advice** | "Add an LLM" without stack | Force concrete stack + cost |
| **Hidden Trade-offs** | "Just use Kubernetes" | Always show 2-3 alternatives |
| **Toy Data Demos** | 100-row CSV in a notebook | Force production-scale data |
| **Eval-Less Systems** | "It looks good" | Force eval framework in Stage 2 |
| **No Production Path** | "We'll figure it out" | Production path in Stage 1 spec |
| **Insulation** | FDE never visits customer site | Force ≥30% field time |

---

## The Customer Engagement Spectrum

Not every customer engagement is the same. Adjust the loop:

| Customer Type | Velocity | Decomposition Depth | Eval Rigor |
|---|---|---|---|
| **Startup ($1-10M ARR)** | Ultra-fast (30-day cycle) | Minimal (move fast) | Light (smoke tests) |
| **SMB ($10-100M ARR)** | Fast (90-day cycle) | Medium | Medium (offline evals) |
| **Mid-market ($100M-1B ARR)** | Standard (90-day) | Deep | Heavy (online evals) |
| **Enterprise ($1B+ ARR)** | Slow (180+ day) | Maximum | Maximum (regulatory) |

---

## Origin and Evolution

- **2010**: Palantir hires first "Deltas" (later FDEs)
- **2014-2018**: FDE model becomes Palantir's competitive moat
- **2020-2023**: Some OpenAI, Anthropic, Cohere engineers experience FDE-style work
- **2024**: OpenAI forms explicit FDE team under Colin Jarvis (grows 2→10+ in 2025)
- **2025**: Anthropic creates "Solutions Architects" (FDE-equivalent)
- **May 2026**: OpenAI announces Deployment Company ($10B valuation); Anthropic + Microsoft+EY pile in ($11.5B combined)
- **2026**: "FDE" becomes the hottest tech job title, +800% spike in postings

---

## Sources

- Vinoo Ganesh — "The Definitive Guide to Forward Deployed Engineering" (Feb 2026)
- Hashnode — "Complete 2026 Guide to the Forward Deployed Engineer"
- Sundeep Teki — "Definitive Guide to FDE Interviews in 2026"
- Youngju Kim — "Palantir FDE Complete Analysis"
- Palantir Architecture Center — Foundry, AIP, Apollo docs
- GetPerspective — "FDE Tech Stack 2026"
- arXiv 2602.12430 — Agent Skills Survey
- Anthropic — "Building agents with Skills"
- Badal Khatri — "OpenAI and Anthropic Enter Consulting" (May 2026)
- Beri.net — "Microsoft & EY's $1B Bet to Kill 43% AI Failure Rate"
