# Production Handoff Template

> **Use**: Stage 3 output. Production-deployed system with runbooks, ADRs, monitoring.
>
> **Mandatory closure**: every production handoff MUST end with a `## FDE Assurance Score` section (see [references/fde-trust-score.md](../references/fde-trust-score.md)). The runbook + observability stack are the Verification step; the rollback plan is the Contradiction step.

---

# [Project Name] — Production Handoff

**Date**: [YYYY-MM-DD]
**Stage**: 3 of 4 (Production)
**Production Launch Date**: [YYYY-MM-DD]

---

## 1. System Overview

[2-3 paragraphs: what was built, what problem it solves, current state]

**Production URL**: [url]
**Status Page**: [url]
**Runbook**: [link to detailed runbook]
**On-call**: [rotation schedule]

---

## 2. Architecture (Production)

### 2.1 System Diagram (Mermaid)

[Full architecture diagram showing all services, databases, external integrations, trust boundaries, monitoring]

### 2.2 Components

| Component | Tech | Hosting | Owner |
|---|---|---|---|
| Frontend | Next.js 14 | Vercel | [...] |
| API | FastAPI | Fly.io | [...] |
| Database | PostgreSQL 16 | Supabase | [...] |
| LLM | Claude Sonnet 4.5 | Anthropic API | [...] |
| Vector DB | Pinecone | Pinecone Cloud | [...] |
| Cache | Redis | Upstash | [...] |
| Queue | Celery + Redis | Fly.io + Upstash | [...] |
| Observability | Langfuse + PostHog + Sentry | Cloud | [...] |

### 2.3 Data Flow

[Describe production data flow including backups, replication, failover]

### 2.4 Trust Boundaries

[Where security boundaries are — public API, internal services, data storage, etc.]

---

## 3. Deployment

### 3.1 Deployment Process

```bash
# Deploy command
git push origin main
# → CI runs: tests, lint, build, security scan
# → Staging deploy automatic
# → Manual approval for production
# → Production deploy with canary (10% → 50% → 100%)
# → Auto-rollback if error rate > 1%
```

### 3.2 Rollback Procedure

```bash
# Rollback to previous version
vercel rollback
# OR
kubectl rollout undo deployment/api

# Time to rollback: <5 min
# Tested weekly
```

### 3.3 Environments

| Environment | URL | Purpose | Data |
|---|---|---|---|
| Development | dev.app.com | Local dev | Synthetic |
| Staging | staging.app.com | Pre-prod testing | Anonymized production data |
| Production | app.com | Live users | Production data |

### 3.4 Feature Flags

[Which features are gated, current state, rollout plan]

---

## 4. Observability

### 4.1 The Three Pillars

**Logs**:
- Format: Structured JSON
- Storage: Better Stack (or equivalent)
- Retention: 90 days hot, 1 year cold
- Search: by trace_id, user_id, tenant_id

**Metrics**:
- Tool: PostHog + Prometheus
- Key metrics:
  - `requests_total` (counter, by endpoint)
  - `request_duration_seconds` (histogram)
  - `llm_tokens_used` (counter, by model)
  - `errors_total` (counter, by type)
  - `active_users` (gauge)
  - `ai_quality_score` (gauge, from evals)

**Traces**:
- Tool: Sentry + OpenTelemetry
- Sample rate: 100% for errors, 10% for success

### 4.2 Dashboards

| Dashboard | Audience | URL |
|---|---|---|
| Business overview | Execs | [link] |
| System health | On-call | [link] |
| AI quality | FDE team | [link] |
| User analytics | Product team | [link] |

### 4.3 Alerts

| Alert | Condition | Severity | Channel |
|---|---|---|---|
| Error rate spike | >2% for 5min | Critical | PagerDuty |
| Latency spike | p95 >Xs for 10min | High | Slack |
| Cost spike | >$X/day | Medium | Slack |
| Eval drift | Quality score -5% | Medium | Slack |
| Down | Health check fails 3x | Critical | PagerDuty |

---

## 5. Security

### 5.1 Authentication & Authorization

- Auth provider: [Clerk / WorkOS / custom]
- MFA: [required / optional]
- Session management: [...]
- API auth: [JWT / API keys / OAuth]

### 5.2 Data Protection

- Encryption at rest: [provider-managed]
- Encryption in transit: [TLS 1.3]
- PII handling: [masking, retention policy]
- Secrets management: [env vars, Vault, etc.]

### 5.3 Compliance

- [ ] GDPR: data export, deletion, DPA
- [ ] SOC 2: [status]
- [ ] AI Act EU 2026: [tier classification, conformity assessment if needed]
- [ ] Industry-specific: [HIPAA, PCI-DSS, etc.]

### 5.4 Threat Model

| Threat | Mitigation | Status |
|---|---|---|
| Prompt injection | Input classifier + output validation | Mitigated |
| Data exfiltration | RBAC + audit logs | Mitigated |
| Account takeover | MFA + anomaly detection | Mitigated |
| DDoS | Cloudflare + rate limiting | Mitigated |
| Supply chain (dep) | Dependabot + Snyk | Monitored |

---

## 6. Cost Projections

### 6.1 Current State

| Item | Cost/month | Notes |
|---|---|---|
| LLM API | $X | Claude Sonnet 4.5 |
| Database | $X | Supabase Pro |
| Hosting | $X | Vercel + Fly.io |
| Observability | $X | Langfuse + PostHog |
| **Total** | **$X** | |

### 6.2 Scale Projections

| Scale | DAU | LLM | DB | Hosting | Total/month |
|---|---|---|---|---|---|
| 1× | 100 | $X | $X | $X | $X |
| 10× | 1,000 | $X | $X | $X | $X |
| 100× | 10,000 | $X | $X | $X | $X |
| 1000× | 100,000 | $X | $X | $X | $X |

### 6.3 Cost Optimization Levers

1. **Caching**: Semantic cache for repeated queries (target: 30% cache hit)
2. **Model selection**: Use Haiku for simple tasks, Sonnet for complex (target: 40% Haiku)
3. **Batching**: Group requests where possible
4. **Truncation**: Don't send full conversation history
5. **Eval-driven**: Cut cost while maintaining quality bar

---

## 7. Knowledge Transfer

### 7.1 Documentation

- [ ] API documentation (OpenAPI spec)
- [ ] Architecture decision records (ADRs)
- [ ] Operational runbook
- [ ] User-facing documentation
- [ ] Onboarding guide for new engineers

### 7.2 Training Sessions

| Session | Audience | Duration | Recording |
|---|---|---|---|
| Architecture overview | Eng team | 2h | [link] |
| Deployment + rollback | On-call | 1h | [link] |
| Eval framework | AI team | 2h | [link] |
| User support | Support team | 1h | [link] |

### 7.3 On-Call Rotation

| Week | Primary | Secondary |
|---|---|---|
| Week 1 | [name] | [name] |
| Week 2 | [name] | [name] |
| ... | ... | ... |

### 7.4 Escalation Path

```
L1: On-call engineer → Slack #oncall
L2: Tech lead → Phone
L3: FDE team → Original engagement owner
L4: CEO → For major incidents only
```

---

## 8. Architecture Decision Records (ADRs)

### ADR-001: [Decision Title]
- **Date**: [YYYY-MM-DD]
- **Status**: Accepted
- **Context**: [What was the question?]
- **Decision**: [What we chose]
- **Consequences**: [Trade-offs accepted]
- **Alternatives considered**: [Other options]

[Repeat for each major decision]

---

## 9. Success Metrics (Post-Launch Tracking)

| Metric | Target | Current | Status |
|---|---|---|---|
| Adoption (DAU) | X | [...] | 🟡 |
| Task success rate | Y% | [...] | 🟢 |
| User satisfaction | Z/5 | [...] | 🟡 |
| Cost per task | $W | [...] | 🟢 |
| System uptime | 99.9% | [...] | 🟢 |

---

## 10. Open Issues & Follow-Ups

- [ ] [Issue 1]
- [ ] [Issue 2]
- [ ] [Issue 3]

---

## 11. The 4-Metric FDE Scorecard (Updated)

| Metric | Target | Actual | Status |
|---|---|---|---|
| Deal velocity (kickoff → production) | ≤90 days | [X] days | 🟢/🟡/🔴 |
| NRR on engagement | ≥130% | TBD (90 days post-launch) | — |
| Productization rate | ≥1 feature | [X] features | 🟢/🟡/🔴 |
| Reusable-asset ratio | ≥70% | [X]% | 🟢/🟡/🔴 |

---

## FDE Assurance Score

Every production handoff must close with a FDE Assurance Score (FDE Operating Principle #14, [DeepSCR protocol](../references/fde-trust-score.md)). Compute by hand:

```
FDE Assurance Score = 25×(Claim falsifiable, 1 sentence anchored on Q6)
            + 25×(≥3 failure modes / threat-model entries documented above)
            + 30×(Evidence trail ≥1 concrete pointer: file:line / command / test / dashboard)
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
| 85-100 | ✅ Certified | Advance to Stage 4 (Productization Memo) |
| 60-84 | ⚠ Needs revision | Address the lowest component, re-score |
| 0-59 | ❌ Rejected | Return to Stage 3 with a new handoff plan |

**SHA-256** (run `shasum -a 256 <this file>`): ______
**Verdict**: ______

---

**Next deliverable**: Productization Memo (Stage 4, at month 3)
