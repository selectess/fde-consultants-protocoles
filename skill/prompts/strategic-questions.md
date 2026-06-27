# Strategic Questions Prompt — Formulating Stratigraphic Questions

**Purpose**: Transform generic questions into stratigraphic ones that demonstrate domain mastery.

**Pattern**: `[Observed fact from research] + [Inference about user's context] + [Targeted question with number request]`

---

## Why This Matters

Generic questions signal "I don't know your industry". Stratigraphic questions signal "I've done my homework". The difference is trust.

---

## The Pattern — Formal Definition

```
STRATIGRAPHIC QUESTION = 
  Domain Fact (cited, sourced)
  + User Inference (acknowledged, uncertain)
  + Specific Question (with number request)
```

**Examples by section:**

### Section 1 — Opening (Confirm Industry)

❌ Generic:
- "What industry are you in?"
- "Tell me about your company."

✅ Stratigraphic:
- "Based on your description, you're in [industry X]. In Q1 2026, [industry X] saw [specific trend — e.g., 'a 30% spike in regulatory pressure due to EU AI Act']. Am I right about the industry, and is that trend affecting you?"

### Section 2 — Confirm Context

❌ Generic:
- "What's your role?"
- "Who else is involved?"

✅ Stratigraphic:
- "I'm guessing you're either the [role A] driving this, or the [role B] who's been tasked with evaluating options. Which is it, and who else needs to weigh in before we proceed?"

### Section 3 — Pain Probe

❌ Generic:
- "What's your biggest challenge?"
- "What are you trying to fix?"

✅ Stratigraphic:
- "In [industry] companies at your scale, the top pain I keep seeing is [X]. We've found it typically costs [€Y/year] in [specific waste]. Does that resonate, or is your situation different?"

### Section 4 — Tech Stack Probe

❌ Generic:
- "What's your current tech stack?"

✅ Stratigraphic:
- "Most [industry] companies at your scale have [typical stack — e.g., 'SAP for ERP, Salesforce for CRM, custom internal tools']. What does yours look like, and where are the gaps you're hoping AI fills?"

### Section 5 — Constraint Probe

❌ Generic:
- "Any constraints I should know about?"

✅ Stratigraphic:
- "Given that you're in [regulated industry], I assume compliance is non-negotiable. Are we looking at AI Act high-risk tier, or are you below the threshold? And is on-prem required, or can we use cloud APIs?"

### Section 6 — Success Probe

❌ Generic:
- "What does success look like?"

✅ Stratigraphic:
- "In similar projects, we've seen ROI of [X-Y×] within [timeframe] when the success metric is [specific outcome]. What does success look like for you, and how would we measure it in a way that survives a CFO review?"

---

## Stratigraphic Question Bank by Industry

### Manufacturing

- "Computer vision on factory lines typically hits 92-96% accuracy with YOLOv8 on a curated dataset. What's your current defect rate, and what accuracy would meaningfully shift the business case?"
- "AI Act high-risk tier applies to safety-critical CV systems. Are you in scope, and have you budgeted for the conformity assessment?"
- "Edge inference on Jetson Orin costs ~$500/unit but cuts latency to <50ms. Is latency your bottleneck, or is throughput the bigger issue?"

### Healthcare

- "PHI handling means we can't send data to external APIs without a BAA. Are you BAA-covered with AWS/Azure, or do we need on-prem deployment?"
- "For diagnostic AI in EU, CE marking is required under MDR. Are you building a CE-marked product, or an internal decision-support tool (different regulatory path)?"
- "Clinical workflows have high switching costs. Which clinical champion in your org will co-design this with us, and how much of their time can we count on weekly?"

### Fintech

- "For fraud detection, the false positive rate matters more than recall — every false positive is a customer service ticket. What's your current false positive rate, and what's the acceptable threshold?"
- "Model risk management (SR 11-7) requires explainability. Are you OK with XGBoost + SHAP, or do you need inherent interpretability (logistic, GAM)?"
- "Real-time fraud scoring needs <100ms p95. What's your current stack — rule engine, vendor, or in-house ML?"

### Retail / E-commerce

- "For personalization, the conversion lift is typically 5-15% with a good two-tower model + reranker. What's your current conversion rate, and what lift would justify the investment?"
- "Search relevance with embedding rerank typically beats Elasticsearch by 8-12%. What's your current search-to-purchase rate, and what would a 10% lift be worth?"
- "Inventory forecasting with ML typically reduces stockouts by 20-30%. What's your current stockout rate, and what's the cost per stockout event?"

### SaaS / B2B

- "For in-product AI features, the ARPU lift is typically 20-40% on the plans that include them. What's your current ARPU and the premium you'd charge for an AI tier?"
- "AI-powered onboarding typically cuts time-to-activation by 30-50%. What's your current activation rate and the dollar value of each activated user?"
- "Support deflection with AI agents typically resolves 40-60% without human. What's your current ticket volume and cost per ticket?"

### Professional Services

- "Document review with LLM typically cuts time by 60-80% on first pass. What's your current hours-per-document, and what's your billable rate?"
- "For legal AI, privilege and confidentiality are non-negotiable. Are you OK with API-based models with zero-retention, or do you need on-prem / private deployment?"
- "Knowledge management with RAG typically reduces ramp time by 30-50%. What's your current ramp time for new hires, and what's the cost?"

---

## Anti-Patterns in Questioning

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| **"What are your goals?"** | Invites vague answers | Ask for a specific number |
| **"Tell me about X"** | Open-ended, rambling | Specify the dimensions |
| **"Any thoughts on Y?"** | Passive, low signal | State what you've seen + ask |
| **"How big is the problem?"** | Subjective | Ask for € or hours/year |
| **"What would success look like?"** | Vague | Propose a number, ask to validate |

---

## Calibration: How Many Stratigraphic Questions?

Per discovery interview (6 questions):
- **0 stratigraphic**: Feels like a generic consultant
- **1-2 stratigraphic**: Acceptable
- **3-4 stratigraphic**: Good
- **5-6 stratigraphic**: Excellent — user feels deeply understood
- **7+ stratigraphic**: Feels performative / showing off

**Target**: 3-4 stratigraphic questions per 6-Q interview. Front-load them for trust.

---

## The Trust-Building Sequence

```
Q1: Confirm industry (stratigraphic)
Q2: Confirm role (stratigraphic, lighter)
Q3-Q6: Alternating stratigraphic + clarifier
Closing: Recap with sources cited
```

This sequence:
1. Opens with "I know your world"
2. Confirms you understand who they are
3. Digs deep with domain knowledge
4. Closes with transparency about sources

---

## Update Log

- 2026-06-18: Initial version.
