# SaaS Playbook — Architecture, Operations, Growth

**Last updated**: 2026-06-18

The complete reference for designing, building, and operating SaaS products — from solo founder MVP to mid-market scale.

---

## Part 1 — SaaS Architecture Patterns

### The 2026 Default Stack (covers 80% of SaaS)

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND                              │
│  Next.js 14 (App Router) + TypeScript + shadcn/ui        │
│  Tailwind + Tremor/Recharts                             │
│  Zustand (client state) + TanStack Query (server state) │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                    BACKEND                               │
│  FastAPI (Python) OR Next.js API routes                 │
│  PostgreSQL + Prisma/Drizzle/SQLAlchemy                 │
│  Redis (Upstash or self-hosted)                         │
│  Celery + Redis (async jobs)                            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  AI LAYER (if applicable)                │
│  Anthropic Claude Sonnet 4.5 (primary)                  │
│  OpenAI GPT-4o-mini (extraction)                        │
│  Pinecone/Qdrant (vector DB)                            │
│  Langfuse or Helicone (observability)                   │
│  LangGraph / Claude Agent SDK (orchestration)           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    INFRA                                 │
│  Vercel (frontend) + Railway/Fly.io (backend)           │
│  Cloudflare (CDN + DDoS)                                │
│  Sentry (errors) + PostHog (analytics)                  │
│  Stripe (billing) + Resend (email)                      │
└─────────────────────────────────────────────────────────┘
```

**Cost at 1K users**: $50-200/mo
**Cost at 10K users**: $500-2K/mo
**Cost at 100K users**: $5K-20K/mo
**Cost at 1M users**: $50K-200K/mo (custom infra required)

---

## Part 2 — Multi-Tenancy Models

Choose based on customer profile:

### Model A — Shared DB, Shared Schema (most common)

```
One PostgreSQL database, all tenants in `tenants` table, all queries filtered by tenant_id
+ Cheapest
+ Easiest to maintain
- Tenant isolation is application-layer responsibility
- Noisy neighbors possible
- Hard to comply with data residency requirements
```

**When**: Startups, SMB SaaS, most use cases.

**Implementation**:
```sql
-- Every table has tenant_id
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  name TEXT,
  -- ...
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Every query filters by tenant_id
CREATE POLICY tenant_isolation ON projects
  USING tenant_id = current_setting('app.tenant_id')::UUID;
```

### Model B — Shared DB, Schema-per-Tenant

```
One PostgreSQL database, one schema per tenant
+ Better isolation
+ Easier data residency
- Schema migrations are N× work
- Higher DB connection count
- Operational complexity grows
```

**When**: Mid-market with enterprise customers, data residency requirements.

### Model C — DB-per-Tenant

```
One database instance per tenant
+ Maximum isolation
+ Easy to extract customer to dedicated infra
- Expensive (1 DB per customer)
- Migration nightmares
- Operational overhead
```

**When**: Enterprise customers paying $100K+/year.

---

## Part 3 — Authentication & Authorization

### Auth Stack (tier by customer)

| Tier | Tool | Cost | Features |
|---|---|---|---|
| **SMB** | Clerk or Supabase Auth | $0-25/mo | Email/password, OAuth, MFA |
| **Mid-market** | WorkOS | $0-500/mo | SSO (SAML, OIDC), SCIM, directory sync |
| **Enterprise** | WorkOS + custom | $500+/mo | SSO, SCIM, RBAC, audit logs, compliance |

### Authorization Patterns

**RBAC** (Role-Based Access Control):
```typescript
// Simple: admin / member / viewer
type Role = 'admin' | 'member' | 'viewer';
const permissions: Record<Role, Permission[]> = { ... };
```

**ABAC** (Attribute-Based): when RBAC isn't expressive enough
```typescript
// User can view project IF
//   they are a member of the project OR
//   they are admin in the tenant
```

**Multi-tenant isolation**: always enforce at the data layer
```typescript
// Repository pattern: every query gets tenant_id automatically
class ProjectRepository {
  async findAll() {
    return db.projects.findMany({
      where: { tenantId: ctx.tenantId } // injected from session
    });
  }
}
```

---

## Part 4 — Billing & Pricing Models

### Pricing Models

| Model | When | Example |
|---|---|---|
| **Flat per seat** | Collaboration tools | $10/user/month |
| **Tiered (Freemium)** | Self-serve SaaS | Free / $99 / $499 |
| **Usage-based** | API products | $0.001/request |
| **Outcome-based** | AI agents | $X per resolved ticket |
| **Platform fee + usage** | Enterprise | $5K/mo + $0.01/user |

**Best practice in 2026**:
- Offer **3 tiers** (Starter / Pro / Enterprise)
- **Starter is freemium or cheap** ($0-99/mo) — drives top-of-funnel
- **Pro is the volume tier** ($299-999/mo) — your core business
- **Enterprise is custom** ($2K+/mo) — requires sales

### Stripe Integration (standard pattern)

```
products/
├── starter
│   ├── monthly: $99
│   └── annual: $990 (2 months free)
├── pro
│   ├── monthly: $499
│   └── annual: $4,990
└── enterprise
    └── custom (sales-led)
```

**Always**:
- Annual discount (locks in revenue)
- Free trial (14-30 days)
- Self-serve cancellation
- Dunning sequence (failed payment recovery)

---

## Part 5 — Async Jobs & Long-Running Operations

For AI workloads that take >30s, you need a queue:

```python
# Celery task
@celery.task(bind=True, max_retries=3)
def generate_study(self, project_id: str):
    try:
        result = long_running_ai_call()
        update_project(project_id, status='done', result=result)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

**Pattern**:
1. User triggers action → API creates job → returns `job_id`
2. Frontend polls `/api/jobs/{job_id}` or subscribes via SSE/WebSocket
3. Worker processes job → updates DB
4. Frontend shows progress + final result

**Tools**:
- SMB: Celery + Redis
- Mid-market: Celery + Redis or Temporal
- Enterprise: Temporal or AWS Step Functions

---

## Part 6 — Observability

### The Three Pillars

**Logs**: Structured JSON, searchable, with trace_id
```python
logger.info("project.created", extra={
    "tenant_id": tenant_id,
    "project_id": project_id,
    "user_id": user_id,
    "trace_id": trace_id,
})
```

**Metrics**: Counters, gauges, histograms
- `projects_created_total` (counter)
- `ai_request_duration_seconds` (histogram)
- `active_users` (gauge)
- `stripe_revenue_monthly` (gauge)

**Traces**: Distributed tracing with OpenTelemetry
- Each request gets a trace_id
- Spans for: API call, DB query, LLM call, external API

### Tools by Tier

| Tier | Logs | Metrics | Traces | Cost |
|---|---|---|---|---|
| **SMB** | Vercel/Railway built-in | PostHog | Sentry | $0-50/mo |
| **Mid-market** | Better Stack or Logtail | PostHog + Prometheus | Sentry + OpenTelemetry | $100-500/mo |
| **Enterprise** | Datadog Logs | Datadog Metrics | Datadog APM | $1K+/mo |

---

## Part 7 — Security Checklist

For every SaaS, ship with:

- [ ] HTTPS everywhere (Let's Encrypt or Cloudflare)
- [ ] Auth: strong passwords + MFA option
- [ ] Secrets in env vars (never in code)
- [ ] Database encryption at rest (provider-managed)
- [ ] Database backups (daily, tested restore)
- [ ] Rate limiting (per IP, per user, per API key)
- [ ] Input validation (Zod, Pydantic)
- [ ] SQL injection prevention (parameterized queries / ORM)
- [ ] XSS prevention (React escaping + CSP headers)
- [ ] CSRF protection (SameSite cookies + tokens)
- [ ] Dependency scanning (Snyk, Dependabot)
- [ ] Container scanning (Trivy)
- [ ] Audit logs (who did what when)
- [ ] GDPR: data export + deletion
- [ ] SOC 2: if mid-market+
- [ ] Penetration test: if enterprise

**Cost**: SMB basic = $0-100/mo tools. Enterprise SOC 2 = $30K+ audit + $500/mo monitoring.

---

## Part 8 — Growth Loops & Metrics

### The Pirate Metrics (AAARRR)

```
Acquisition → Activation → Retention → Revenue → Referral
```

**For each stage, define one metric and one lever**:
- Acquisition: visitors / signups → SEO, ads, content
- Activation: completed onboarding → better onboarding flow
- Retention: weekly active users → value delivery, notifications
- Revenue: paying users, ARPU → pricing, expansion
- Referral: viral coefficient → referral program, shareable artifacts

### North Star Metric

Pick ONE number that captures value delivery:
- Slack: messages sent
- Notion: weekly active editors
- Stripe: payment volume processed
- Linear: issues closed
- OpenAI: tokens consumed (now evolving to outcomes)

For your SaaS: what action, if taken more, means the customer is succeeding?

### Growth Loop Types

1. **Content loop** (SEO) — slow, compounding
2. **Viral loop** (referrals) — needs strong incentive
3. **Sales loop** (outbound) — predictable, expensive
4. **Product loop** (usage → invites) — best long-term

---

## Part 9 — Production Handoff Checklist

When handing off to the customer's team:

- [ ] **Deployment runbook**: every command needed to deploy
- [ ] **Rollback procedure**: tested, <5min to revert
- [ ] **On-call rotation**: who responds when, how
- [ ] **Incident response plan**: severity levels, escalation
- [ ] **Architecture Decision Records (ADRs)**: why we chose X over Y
- [ ] **Cost projections**: at 1×, 10×, 100× current scale
- [ ] **Performance baselines**: p50/p95/p99 latency, throughput
- [ ] **Security review**: threat model + mitigations
- [ ] **Compliance docs**: SOC 2, GDPR, AI Act (if applicable)
- [ ] **Eval baselines**: AI system performance, drift detection
- [ ] **Knowledge transfer session**: 2-4h walkthrough with the team

---

## Part 10 — The 4-Metric FDE Scorecard (Adapted for SaaS)

| Metric | Target | Why |
|---|---|---|
| **Time to value** | <30 days from signup to first value | Onboarding speed |
| **Activation rate** | >40% of signups complete onboarding | Onboarding quality |
| **NRR** | >130% | Expansion - churn |
| **Productionization rate** | >1 feature/quarter from customer feedback | Reusable IP building |

---

## Update Log

- 2026-06-18: Initial version. Sources: GetPerspective FDE Tech Stack 2026, Stripe best practices, PostHog analytics, industry blogs.
