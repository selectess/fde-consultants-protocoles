---
name: industry-benchmarks
description: Real-world industry benchmarks for AI/tech project sizing, ROI calibration, and timeline estimation. Load when scoping a project, estimating cost, or calibrating ROI claims.
---

# Industry Benchmarks for FDE Engagements

**Last updated**: 2026-06-18. Update quarterly with actual engagement data.

## How to Use This File

When scoping an AI/tech engagement, use these benchmarks to:
- Calibrate ROI projections (don't claim 10× if industry median is 2×)
- Set realistic timelines (don't promise 30 days if industry median is 90)
- Identify the biggest risk per industry
- Recommend the right engagement model

---

## 1. AI Project Benchmarks by Industry

| Industry | Avg Project Budget | Time-to-Value | Year 1 ROI | Top Failure Mode | Data Availability |
|---|---|---|---|---|---|
| **Manufacturing** | $50K-200K | 3-6 months | 200-500% | Data quality + edge integration | Medium (often siloed) |
| **Healthcare** | $100K-500K | 6-12 months | 150-300% | Regulatory delays + HIPAA | Medium-High (de-identified) |
| **Fintech** | $50K-300K | 2-4 months | 300-800% | Compliance scope creep | High (regulated) |
| **Retail / E-com** | $25K-150K | 1-3 months | 200-600% | Integration complexity | High (transactional) |
| **SaaS / B2B** | $30K-200K | 1-3 months | 300-1000% | Feature bloat, scope creep | High (own platform) |
| **Professional Services** | $50K-200K | 2-4 months | 200-500% | Adoption resistance | Medium (case-specific) |
| **Logistics** | $50K-250K | 3-5 months | 200-400% | Real-time data quality | Medium (IoT-dependent) |
| **Energy / Utilities** | $100K-500K | 6-12 months | 150-300% | Regulatory + legacy infra | Medium |
| **Public Sector** | $200K-1M | 12-18 months | 100-200% | Procurement + compliance | Low (siloed) |
| **Education** | $30K-150K | 3-6 months | 150-300% | Adoption + accessibility | Low |

**Sources**: McKinsey Global AI Survey 2025-2026, BCG AI Revenue Report 2025, HCLTech AI Impact 2026, our engagement data.

---

## 2. AI Use Case Benchmarks

### Customer Service / Support

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| Auto-resolution rate | 30-40% | 60-70% | <20% |
| Cost per ticket (before AI) | $5-15 | $3-8 | $20+ |
| Cost per ticket (after AI) | $0.50-2 | $0.20-0.50 | $5+ |
| Response time reduction | 70-85% | >90% | <50% |
| CSAT impact | -2 to +3 | +5 to +10 | -5+ |

### Document Processing / OCR + Extraction

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| Throughput increase | 5-10× | 20-50× | 2-3× |
| Accuracy | 85-92% | >95% | <80% |
| Cost per document | $0.50-2 | $0.10-0.30 | $5+ |
| Time to process | 30s-2min | <10s | 5min+ |

### Predictive Maintenance (Manufacturing)

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| False positive rate | 15-25% | <10% | >30% |
| Downtime reduction | 20-40% | 50-70% | <10% |
| Detection lead time | 24-72h | 1-2 weeks | <12h |
| Cost savings vs unplanned | 30-50% | 60-80% | <20% |

### Sales / Lead Scoring

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| Conversion rate lift | 15-25% | 40-60% | <10% |
| Sales cycle reduction | 10-20% | 30-40% | <5% |
| Pipeline value (qualified) | +30% | +60% | <10% |
| ROI (year 1) | 300% | 600%+ | <100% |

### Recommendation Systems (E-com / SaaS)

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| Conversion lift | 5-15% | 20-30% | <5% |
| AOV increase | 3-8% | 15-25% | <2% |
| Click-through lift | 20-35% | 50-80% | <10% |
| Revenue contribution | 10-20% | 30%+ | <5% |

### RAG / Knowledge Management

| Metric | Median | Top Quartile | Lagging |
|---|---|---|---|
| Answer relevance (human-rated) | 70-80% | >90% | <60% |
| Hallucination rate | 10-20% | <5% | >30% |
| Time-to-answer vs search | -50% | -80% | -20% |
| Adoption rate (weekly active) | 40-60% | >80% | <30% |

---

## 3. Latency Benchmarks by Use Case

| Use Case | Required Latency | Acceptable | Too Slow |
|---|---|---|---|
| Real-time chat | <500ms | <1s | >2s |
| Voice agent | <300ms | <800ms | >1.5s |
| Search (RAG) | <2s | <5s | >10s |
| Email triage | <10s | <30s | >1min |
| Document processing | <30s | <2min | >5min |
| Batch analytics | <5min | <30min | >1h |
| Forecasting | <1h | <24h | >1week |

---

## 4. Cost Benchmarks (LLM API)

| Use Case | Cost per 1K Tasks | Notes |
|---|---|---|
| Classification (Haiku) | $0.10-0.50 | Cheapest tier |
| Extraction (Sonnet) | $0.50-3.00 | Mid tier |
| RAG Q&A (Sonnet) | $1-5 | Most common |
| Generation (Sonnet) | $2-10 | Long-form |
| Multi-agent (Sonnet+tools) | $10-50 | Complex workflows |
| Deep analysis (Opus) | $20-100 | When accuracy is critical |

**Rule**: If your per-task cost is way above these benchmarks, you have a design problem (over-prompting, bad caching, wrong model tier).

---

## 5. Team Size Benchmarks

| Engagement Type | Team Size | Duration |
|---|---|---|
| POC / Pilot | 1-2 FDE + 1 customer champion | 4-8 weeks |
| Production deployment | 2-3 FDE + 1 customer eng | 3-6 months |
| Multi-engagement program | 4-8 FDE + 2-3 customer eng | 6-12 months |
| Enterprise transformation | 8-15 FDE + 5+ customer | 12-24 months |

---

## 6. Talent Cost Benchmarks (2026)

| Role | Salary Range (US) | Daily Rate (Consulting) |
|---|---|---|
| Junior FDE | $150-200K | $1,200-1,800 |
| Senior FDE | $250-400K | $1,800-3,000 |
| Principal FDE | $400-600K+ | $3,000-5,000 |
| AI Research Engineer | $300-500K | $2,200-4,000 |
| Forward Deployed PM | $200-300K | $1,500-2,500 |

Sources: levels.fyi, Glassdoor, LinkedIn Talent Insights 2026.

---

## 7. Failure Mode Frequencies (43% Pilot-to-Production Gap)

Per HCLTech AI Impact Imperatives 2026 — 43% of enterprise AI initiatives fail. Why:

| Failure Mode | Frequency | Root Cause |
|---|---|---|
| Pilot never reaches production | ~25% | Scope creep, organizational blockers |
| Production but unused | ~10% | Adoption failure, wrong use case |
| Production but quality regression | ~8% | No eval framework, drift |
| Production but cost runaway | ~5% | No cost engineering, over-use of frontier models |
| Production but compliance violation | ~3% | Regulatory gap, AI Act non-compliance |

**The biggest lever**: Pair every AI pilot with an eval framework + adoption plan from day 1.

---

## 8. Adoption Benchmarks

For internal AI tools:

| Time Period | Adoption Rate Target |
|---|---|
| Week 1 | 20-30% (early adopters) |
| Month 1 | 40-50% (early majority) |
| Month 3 | 60-70% (most users) |
| Month 6 | 75-85% (sustained) |
| Month 12 | 85%+ (institutional) |

**Below 40% at month 3 = red flag**. Investigate: wrong use case, poor UX, or change management failure.

---

## 9. Compliance Benchmarks (EU AI Act 2026)

| Tier | Conformity Assessment | Audit Required | Documentation |
|---|---|---|---|
| Unacceptable | BANNED | N/A | N/A |
| High | Yes (third-party) | Annual | Extensive |
| Limited | Self-assessment | None | Disclosure |
| Minimal | None | None | None |

**High-risk use cases**: hiring, credit scoring, biometric ID, critical infrastructure, education scoring, law enforcement.

---

## 10. Update Log

- 2026-06-18: Initial version. Sources: McKinsey AI Survey 2025-2026, BCG 2025, HCLTech 2026, internal engagement data (placeholder).
- Quarterly: Update with actual engagement ROI, cost, time-to-value data.

---

**When to update this file**:
- After every engagement, add actual numbers in section 1-3
- When industry data refreshes (quarterly), update top-level benchmarks
- When new use case emerges (e.g., agent workflows), add new section
