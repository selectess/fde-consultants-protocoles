# Domain Research Prompt — Stage 1a of Scoping

**Purpose**: Before asking the user any question, research the industry vertical deeply enough to ask intelligent, informed questions.

**When to use**: ALWAYS at the start of every FDE engagement, BEFORE the discovery interview.

---

## The 7 Research Streams

Execute WebSearch + WebFetch on these 7 streams in parallel. Read 3-5 authoritative sources per stream.

### Stream 1 — Market & Industry

**Queries**:
- "[industry] market size 2026"
- "[industry] market trends 2026"
- "[industry] CAGR forecast"
- "[industry] key players competitors"

**Sources to prioritize**:
- Gartner, Forrester, IDC reports
- McKinsey, BCG, Bain industry reports
- Statista, IBISWorld
- Industry trade publications (TechCrunch, VentureBeat for tech; trade pubs for vertical)
- Government data (BLS, EU Eurostat)

**Extract**:
- Market size ($)
- Growth rate
- Top 5 players
- Market segments
- Geographic distribution

### Stream 2 — Pain Points & Top Use Cases

**Queries**:
- "[industry] top challenges 2026"
- "[industry] AI use cases"
- "[industry] digital transformation pain points"
- "[industry] operational bottlenecks"

**Sources**:
- Industry analyst reports
- Customer reviews (G2, Capterra, TrustRadius)
- Reddit, LinkedIn discussions
- Support forums
- Conference talks (YouTube, SlideShare)

**Extract**:
- Top 5 pain points (frequency × severity)
- Common workarounds
- Cost of pain (estimated $)

### Stream 3 — Regulatory Landscape

**Queries**:
- "[industry] regulations 2026"
- "AI Act EU 2026 [industry]"
- "GDPR [industry]"
- "[industry] compliance requirements"
- "[industry] data residency"

**Sources**:
- Official regulatory bodies (.gov, .eu)
- Legal firms specializing in the industry
- Industry associations
- AI Act official documentation

**Extract**:
- AI Act tier (unacceptable / high / limited / minimal)
- GDPR implications
- Industry-specific regulations
- Data residency requirements
- Audit obligations

### Stream 4 — Technology Landscape

**Queries**:
- "[industry] AI tech stack"
- "[industry] machine learning applications"
- "[industry] digital tools"
- "[industry] software vendors"

**Sources**:
- Vendor case studies
- GitHub trending repos
- arXiv papers on the industry
- Tech blogs (Towards Data Science, etc.)

**Extract**:
- Dominant tech stacks
- Top vendors in the space
- Recent innovations
- Open-source projects

### Stream 5 — Benchmarks & KPIs

**Queries**:
- "[industry] KPIs benchmarks 2026"
- "[industry] performance metrics"
- "[industry] operational excellence metrics"

**Sources**:
- Industry benchmarks (Gartner, Forrester)
- Public company 10-Ks for the sector
- Industry reports
- Vendor white papers

**Extract**:
- Industry-standard KPIs
- Top-quartile performance
- Common failure points

### Stream 6 — Recent News & Trends (last 90 days)

**Queries**:
- "[industry] news 2026"
- "[industry] AI adoption 2026"
- "[industry] funding acquisitions 2026"

**Sources**:
- TechCrunch, VentureBeat
- Industry trade press
- LinkedIn news
- Twitter/X discussions
- Crunchbase

**Extract**:
- Recent acquisitions
- Funding rounds
- New product launches
- Regulatory changes
- Major incidents (outages, breaches)

### Stream 7 — Talent & Hiring Market

**Queries**:
- "[industry] AI talent shortage"
- "[industry] engineering salaries 2026"
- "[industry] technical hiring trends"

**Sources**:
- LinkedIn Talent Insights
- Glassdoor, Levels.fyi
- Industry surveys
- Recruiting firm reports

**Extract**:
- Talent availability
- Salary ranges
- Skill gaps

---

## The Domain Dossier Format

After research, compile a structured dossier:

```markdown
# Domain Dossier — [Industry]

## Market Overview
- Market size: $X (2026)
- CAGR: Y%
- Top 3 players: A, B, C
- Geographic split: US 40%, EU 30%, APAC 25%, RoW 5%

## Top Pains (ranked)
1. [Pain 1] — Severity X/5, frequency daily, estimated cost $Y/year
2. [Pain 2] — ...
3. ...

## Regulatory Environment
- AI Act tier: [high / limited / minimal]
- GDPR: [implications]
- Industry-specific: [requirements]
- Audit obligations: [list]

## Tech Stack Dominant Patterns
- ML frameworks: [PyTorch / TensorFlow / etc.]
- Cloud: [AWS / Azure / GCP / hybrid]
- Data: [Snowflake / BigQuery / Databricks]
- Vendors: [list with pricing if known]

## Recent Trends (last 90 days)
- [Trend 1]
- [Trend 2]
- [Trend 3]

## KPIs & Benchmarks
- Top quartile: [numbers]
- Median: [numbers]
- Lagging: [numbers]

## Talent Market
- Senior engineer salary: $X
- AI specialist: $Y
- Talent gap: [description]

## Key Insights for Our Engagement
1. [Insight that informs our approach]
2. [Insight that informs our stack recommendation]
3. [Insight that informs our risk assessment]
4. [Insight that informs our pricing]
5. [Insight that informs our timeline]
```

---

## Use of the Dossier

Once compiled, use the dossier to:

1. **Formulate stratigraphic questions** (see `prompts/strategic-questions.md`)
2. **Validate the user's claims** ("Many companies in your industry report X; is that your experience?")
3. **Anticipate objections** ("I know you'll likely push back on Y because of Z")
4. **Recommend the right stack** (not generic — informed by what others use)
5. **Price realistically** (based on market rates and complexity)

---

## Time Budget

- Stream 1-3: 30 min (mandatory, always do)
- Stream 4-5: 20 min (mandatory for tech-heavy engagements)
- Stream 6: 15 min (highly recommended)
- Stream 7: 10 min (optional)

**Total: 45-75 minutes for a complete dossier.**

For SMB engagements, you can compress to 30 min by combining streams.

---

## Anti-Patterns

- ❌ Skipping research and asking generic questions
- ❌ Researching too broadly (industry + adjacent) without focus
- ❌ Only reading vendor whitepapers (biased)
- ❌ Not validating sources (cross-reference 3+ sources for key facts)
- ❌ Treating dossier as static (update during engagement)

---

## Sources Priority

| Tier | Source Type | Trust Level |
|---|---|---|
| 1 | Government data, peer-reviewed research | Highest |
| 2 | Top analyst firms (Gartner, Forrester, IDC) | Very High |
| 3 | Top consulting firms (McKinsey, BCG) | High |
| 4 | Industry trade publications | High |
| 5 | Vendor case studies | Medium (biased) |
| 6 | Reddit, Twitter, forums | Low (use as signal only) |

Always cite which tier your sources are from.

---

## Update Log

- 2026-06-18: Initial version.
