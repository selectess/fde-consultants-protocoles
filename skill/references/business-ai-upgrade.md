# Business AI Upgrade — Transformation Reference

**Last updated**: 2026-06-18

How to identify, scope, and deliver AI transformations for existing businesses. The most common FDE engagement type.

---

## Part 1 — The 3 Service Tiers (SaaS Pro Tiers)

When selling FDE-as-a-Service, structure around 3 distinct Pro services:

### Service 1 — NEW PROJECT (Build something from scratch)

**Customer profile**: 
- Has a new idea or new product
- Needs full architecture, design, build, deploy
- Timeframe: 30-90 days

**What we deliver**:
- Domain research + opportunity sizing
- Tech stack recommendation with trade-offs
- Full architecture (frontend, backend, AI layer, infra)
- Working prototype (validated with real users)
- Production deployment with observability
- Knowledge transfer to their team

**Pricing**: $5K-25K fixed-price, 30-90 day delivery

**Examples**:
- "Build a SaaS for X industry"
- "Launch an AI copilot for Y use case"
- "Create an MVP for our new product line"

### Service 2 — STARTUP (Accelerate an early-stage company)

**Customer profile**:
- Seed to Series A startup (1-20 people)
- Has product-market fit (or hunting for it)
- Needs to ship faster, with better engineering
- Engineering team is 1-5 people, overloaded

**What we deliver**:
- Engineering audit (what's working, what's slowing them down)
- 90-day engineering roadmap aligned with business goals
- Hands-on implementation of highest-impact features
- Tech debt reduction + performance optimization
- Hiring support (interview rubrics, take-home reviews)
- Founder engineering coaching (architecture decisions, scaling)

**Pricing**: $10K-50K/quarter retainer + equity optional

**Examples**:
- "Help us hit our next milestone faster"
- "Our team is drowning, we need senior engineering firepower"
- "We're about to raise Series A, help us get metrics right"
- "Add AI features without breaking what's working"

### Service 3 — BUSINESS UPGRADE (Transform an existing business)

**Customer profile**:
- Existing business (SMB to mid-market, 50-1000 employees)
- Has legacy systems, manual processes, technical debt
- Sees AI as a competitive necessity
- Doesn't have in-house AI expertise

**What we deliver**:
- Process audit + AI opportunity mapping
- Prioritized roadmap (high-impact, low-risk first)
- Pilot implementation on real workflows
- Production deployment with compliance (GDPR, AI Act, sector)
- Change management + team training
- Handoff with runbooks, ADRs, monitoring

**Pricing**: $25K-100K+ per engagement, 90-day cycles

**Examples**:
- "Automate our customer service triage"
- "Add AI to our factory quality control"
- "Modernize our data infrastructure"
- "Reduce our reporting time from 2 weeks to 2 hours"

---

## Part 2 — The Business Audit Framework

Before proposing any AI solution, run this audit:

### Layer 1 — Business Context

```
- Industry: [vertical, sub-vertical]
- Size: [employees, revenue, growth rate]
- Stage: [startup / growth / mature / declining]
- Geography: [markets served]
- Regulatory: [GDPR, HIPAA, SOC 2, AI Act tier, sector-specific]
- Strategic priorities (next 12 months): [...]
```

### Layer 2 — Current State

```
- Revenue model: [how money is made]
- Key processes: [top 10 by impact]
- Decision-making: [data-driven? intuition? politics?]
- Tech stack: [what they have, what's working, what's broken]
- Data assets: [what data they have, where, quality]
- Team capabilities: [who can do what, gaps]
```

### Layer 3 — Pain Points

For each pain point, score:

| Pain | Severity (1-5) | Frequency | Cost/year | AI Opportunity |
|---|---|---|---|---|
| [Pain 1] | 4 | Daily | $50K | High (CV for QC) |
| [Pain 2] | 5 | Weekly | $200K | Medium (predictive ML) |
| ... | | | | |

### Layer 4 — Opportunity Sizing

For each AI opportunity:
- **Impact**: € saved, hours saved, revenue enabled
- **Effort**: team-weeks to build + deploy
- **Risk**: technical, regulatory, organizational
- **Time-to-value**: weeks until first impact

### Layer 5 — Prioritization

```
Priority = (Impact × Confidence) / (Effort × Risk)

High priority: High impact, low effort, low risk → DO FIRST
Strategic bets: High impact, high effort → PLAN CAREFULLY
Quick wins: Low impact, low effort → BATCH THEM
Avoid: High effort, low impact → DON'T DO
```

---

## Part 3 — Common AI Use Cases by Industry

### Manufacturing
- **Defect detection** (CV): Replace manual inspection. ROI: $X/year per line.
- **Predictive maintenance** (ML): Reduce downtime. ROI: $X/hour saved.
- **Demand forecasting** (ML): Optimize inventory. ROI: $X in working capital freed.
- **Worker safety** (CV): PPE compliance, hazard detection. ROI: regulatory + insurance.
- **Process optimization** (RL/optimization): Yield improvement. ROI: $X/year.

### Healthcare
- **Triage routing** (NLP): Faster intake. ROI: wait time ↓, throughput ↑.
- **Medical imaging** (CV): Diagnostic assistance. ROI: radiologist time saved.
- **Documentation** (LLM): Auto-generate clinical notes. ROI: physician time saved.
- **Drug discovery** (ML): Accelerate R&D. ROI: time-to-market ↓.

### Fintech
- **Fraud detection** (ML): Real-time + batch. ROI: fraud losses ↓.
- **Credit scoring** (ML): Alternative data. ROI: approval rate ↑, defaults ↓.
- **Customer service** (LLM): Triage + response. ROI: cost per ticket ↓.
- **Compliance** (NLP): KYC/AML automation. ROI: analyst time saved.
- **Document AI** (LLM): Contract extraction. ROI: legal ops efficiency.

### Retail / E-commerce
- **Recommendation** (ML): Personalization. ROI: AOV ↑, conversion ↑.
- **Search** (vector + LLM): Better relevance. ROI: search-to-purchase ↑.
- **Inventory forecasting** (ML): Reduce stockouts. ROI: lost sales ↓.
- **Customer support** (LLM agent): Deflection. ROI: support cost ↓.
- **Marketing content** (LLM): Scale creative. ROI: CAC ↓.

### SaaS / B2B
- **In-product AI features**: Copilot, automation, insights. ROI: ARPU ↑, churn ↓.
- **Customer success**: Churn prediction, expansion signals. ROI: NRR ↑.
- **Sales**: Lead scoring, outreach personalization. ROI: win rate ↑.
- **Support**: AI-first deflection. ROI: cost per ticket ↓.
- **Onboarding**: Personalized paths. ROI: activation ↑.

### Professional Services
- **Document review** (LLM): Legal, accounting, consulting. ROI: hours saved.
- **Research** (RAG + agents): Faster insight generation. ROI: project margins.
- **Knowledge management**: Internal Q&A. ROI: ramp time ↓.

---

## Part 4 — ROI Calculation Framework

### The Formula

```
Annual ROI = (Gains - Costs) / Costs × 100%

Where:
Gains = (Hours saved × Hourly cost) + (Revenue enabled) + (Risk reduced × Probability × Impact)
Costs = (Build cost) + (Run cost/year) + (Maintenance cost/year)
```

### Worked Example: Customer Service Triage

```
Baseline:
- 1000 tickets/day
- Avg handling time: 10 minutes
- Agent cost: $30/hour fully loaded
- Cost per ticket: $5

AI System:
- Auto-resolves 60% of tickets
- Cuts handling time by 50% for remaining 40%
- Latency: <30s per response
- Quality: >90% accuracy on routing

Annual Savings:
- Tickets auto-resolved: 600/day × 365 = 219,000/year
- Saved time: 219,000 × 10min = 36,500 hours/year
- Cost saved: 36,500 × $30/hr = $1,095,000/year
- For remaining 400/day: 146,000 × 5min saved = 12,167 hours × $30 = $365,000/year
- Total: $1,460,000/year

Costs:
- Build: $80,000 one-time
- Run: $2,000/month × 12 = $24,000/year
- Maintenance: $30,000/year
- Total year 1: $134,000

ROI year 1: ($1,460,000 - $134,000) / $134,000 = 989%
Payback: 25 days
```

**Every project must produce this analysis with realistic numbers, not aspirational ones.**

---

## Part 5 — Change Management

The hardest part isn't the AI. It's the people.

### The Adoption Curve

```
Innovators (2.5%) → Early Adopters (13.5%) → Early Majority (34%) → Late Majority (34%) → Laggards (16%)
```

**For AI tools, the curve is shifted** because people fear replacement.

### Strategies by Stakeholder

**Champions** (early adopters, often 1-2 people per team):
- Involve them in design
- Give them early access
- Make them co-creators

**The Middle** (early/late majority):
- Show them concrete wins from champions
- Address fear with empathy
- Train them, don't just deploy

**Skeptics** (late majority, laggards):
- Don't waste time on them early
- They come around when others succeed
- Mandatory adoption is a last resort

### Communication Template

Every internal communication about the AI rollout should answer:
1. **What is it?** (one sentence, no jargon)
2. **What's in it for me?** (specific benefit to this person)
3. **What changes for me?** (workflow, daily work)
4. **When does it happen?** (specific date)
5. **Who do I ask if confused?** (named person, not a ticket)

---

## Part 6 — Pilot-to-Production Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|---|---|---|
| **Pilot Purgatory** | 50 pilots, 0 in production | Force "production-or-kill" decision at 30 days |
| **AI Theater** | AI in name only, no measurable impact | Force metric definition before pilot |
| **Vendor Lock-in** | One vendor, no exit strategy | Design swap-ability from day 1 |
| **No Owner** | Everyone's job, no one's job | Single accountable name per project |
| **No Eval** | "It looks good" | Eval framework required at pilot start |
| **Scaled Too Fast** | 100 users day 1 | Ramp: 5 → 25 → 100 → all |
| **Compliance Last** | "We'll add GDPR later" | Compliance review in pilot design |

---

## Part 7 — Engagement Pricing Models

### Fixed-Price Engagements

**When**: Well-defined scope, single deliverable
**Risk**: Customer (us if scope changes)
**Example**: "Build this AI feature in 6 weeks for $30K"

### Time & Materials

**When**: Evolving scope, ongoing partnership
**Risk**: Shared
**Example**: "$250/hour, monthly billing"

### Retainer

**When**: Long-term partnership, ongoing work
**Risk**: Customer (utilization)
**Example**: "$15K/month for 60 hours + ad-hoc availability"

### Outcome-Based

**When**: Customer wants pay-for-performance
**Risk**: Us
**Example**: "$X per ticket auto-resolved, capped at $Y/month"

**Default in 2026**: Hybrid (base retainer + outcome bonus).

---

## Part 8 — The 90-Day Business Upgrade Cycle

### Days 1-10 — Scoping (already documented in SKILL.md)
- Domain research
- Stakeholder mapping
- Decomposition (6-Q)
- Scoping report

### Days 11-30 — Quick Win
- Pick the highest-priority, lowest-risk opportunity
- Build PoC
- Validate with 1-2 users in the actual workflow
- Measure ROI on the pilot

### Days 31-60 — Production Pilot
- Harden the PoC
- Roll out to 5-10 users
- Daily feedback collection
- Weekly iteration

### Days 61-90 — Production Rollout
- Roll out to all relevant users
- Training sessions
- Documentation
- Handoff to internal team

### Day 91+ — Continuous Improvement
- Track KPIs
- Iterate based on usage data
- Identify next opportunity (back to Day 1)

---

## Part 9 — Industry Benchmarks (Update Quarterly)

| Industry | Avg AI Project Budget | Avg Time-to-Value | Avg ROI (Year 1) | Common Failure |
|---|---|---|---|---|
| Manufacturing | $50K-200K | 3-6 months | 200-500% | Data quality |
| Healthcare | $100K-500K | 6-12 months | 150-300% | Regulatory delays |
| Fintech | $50K-300K | 2-4 months | 300-800% | Compliance scope creep |
| Retail | $25K-150K | 1-3 months | 200-600% | Integration complexity |
| SaaS / B2B | $30K-200K | 1-3 months | 300-1000% | Feature bloat |
| Professional Services | $50K-200K | 2-4 months | 200-500% | Adoption resistance |

**Sources**: Industry surveys, our own engagement data (update quarterly).

---

## Part 10 — Selling the Engagement

### The Pitch Structure (for Service 3: Business Upgrade)

**1. The Setup** (2 min)
- "I noticed [specific observation about their business]"
- "Based on our work with [X similar companies], we see [common pattern]"

**2. The Pain** (3 min)
- "In [industry], the typical cost of [pain] is [number]"
- "We've seen [X] companies lose $Y/year to this"

**3. The Opportunity** (5 min)
- "Here's a concrete path to capture $Z/year"
- "The first step is a 10-day scoping study for $15K"
- "If we find a >5× ROI opportunity, we proceed to a 90-day pilot"
- "If not, you keep the scoping report, no further obligation"

**4. The Proof** (5 min)
- "Here's a similar engagement: [case study]"
- Before/after metrics
- Reference customer (with permission)

**5. The Close**
- "Want to schedule the scoping kickoff?"
- Don't oversell. Let the math sell.

---

## Sources

- HCLTech AI Impact Imperatives 2026
- McKinsey Global AI Survey 2025-2026
- BCG AI Revenue Report 2025
- Accenture GenAI Bookings Report
- Our own engagement data (placeholder, update quarterly)
- GetPerspective — FDE Tech Stack 2026
- Vinoo Ganesh — Definitive Guide to FDE

---

## Update Log

- 2026-06-18: Initial version with 3 service tiers (New Project, Startup, Business Upgrade).
