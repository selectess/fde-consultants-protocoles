# Tech Stacks 2026 — Per Use Case & Industry

**Last updated**: 2026-06-18. Update after each engagement — this is a living document.

When recommending a stack, ALWAYS show 2-3 alternatives with explicit trade-offs (cost, latency, ops complexity, team fit).

---

## The Meta-Rule

**No stack is "best". Every choice has 3 trade-offs**:
- **Cost** ($/month at scale)
- **Speed** (latency + dev velocity)
- **Complexity** (ops burden, team skill required)

Always pick the stack where the trade-offs match the customer's context:
- Solo founder → maximize speed, minimize cost, accept managed services
- 10-person team → balanced, mix of managed + custom
- Enterprise → minimize risk, accept higher cost, prefer owned infrastructure

---

## 1. LLM Apps (Chat, Q&A, RAG)

### Tier 1 — Speed-of-prototype (1-7 days)

| Component | Choice | Cost | Why |
|---|---|---|---|
| LLM | Claude Sonnet 4.5 / GPT-4o | $3-15/M tokens | Best reasoning, tool use |
| Orchestration | LangGraph / CrewAI | Free (OSS) | State management, branching |
| Vector DB | Pinecone serverless | $0.33/GB/mo | Zero-ops, fast scale |
| Backend | Next.js API routes | Free tier available | Single repo with frontend |
| Auth | Clerk | Free → $25/mo | Fastest auth setup |
| Deploy | Vercel | Free → $20/mo | Zero-config Next.js |

**Trade-offs**: Lock-in to managed services. At 100× scale, costs grow linearly.

### Tier 2 — Production-grade (1-4 weeks)

| Component | Choice | Cost | Why |
|---|---|---|---|
| LLM | Multi-model (Claude + GPT + local) | $3-50/M tokens | Vendor risk mitigation |
| Orchestration | Claude Agent SDK + LangSmith | Free + $50/mo | Production tracing |
| Vector DB | Qdrant (self-hosted) or Weaviate | $50-500/mo | Better cost at scale |
| Backend | FastAPI (Python) | Self-hosted or Fly.io | Async, AI-native |
| DB | PostgreSQL + pgvector | $30-300/mo | SQL + vectors in one |
| Auth | Supabase Auth | Free → $25/mo | Postgres-native |
| Queue | Celery + Redis | $50-200/mo | Long jobs |
| Observability | Langfuse + PostHog + Sentry | $0-200/mo | LLM tracing + product analytics |
| Deploy | Fly.io or Railway | $50-500/mo | Predictable costs |

### Tier 3 — Enterprise scale (custom)

| Component | Choice | Cost | Why |
|---|---|---|---|
| LLM | Multi-region, multi-vendor with fallback | $50K+/mo | SLA, redundancy |
| Orchestration | Custom on Kubernetes | Significant ops | Full control |
| Vector DB | Self-hosted Qdrant cluster | $1K+/mo | Data residency |
| Backend | Go or Rust | Variable | Latency-critical |
| DB | PostgreSQL on Aurora + pgvector | $1K+/mo | High-availability |
| Auth | Auth0 / WorkOS | $1K+/mo | SSO, SCIM, compliance |
| Queue | Temporal or AWS SQS | $500+/mo | Reliable workflows |
| Observability | Datadog + Honeycomb | $1K+/mo | Full stack tracing |
| Deploy | EKS/GKE | $2K+/mo | Multi-region |

---

## 2. Multi-Agent Systems (Workflow Automation, Complex Tasks)

### The 2026 stack

| Component | Choice | Cost | Notes |
|---|---|---|---|
| Orchestration | **LangGraph** (LangChain) or **Claude Agent SDK** | Free | State machines, branching |
| Multi-agent pattern | **Supervisor + workers** | — | Most reliable pattern |
| Memory | Redis (short-term) + Vector DB (long-term) | $50-200/mo | Conversation + RAG |
| Tool execution | Sandboxed (E2B, Modal, Firecracker) | $50-500/mo | Safe code execution |
| Eval | **Braintrust** or **Langfuse** | $0-500/mo | LLM-as-judge, traces |
| Observability | Helicone + PostHog | $0-200/mo | Cost tracking + product analytics |

**Pattern of choice in 2026**:
```
Supervisor Agent
  ├── Decomposes task into sub-tasks
  ├── Assigns to specialized Worker Agents
  ├── Aggregates results
  └── Validates output (LLM-as-judge + rules)
```

**Don't use**:
- ❌ AutoGen (Microsoft) — still unstable in prod
- ❌ CrewAI for >5 agents — coordination becomes chaos
- ❌ LangChain agents (use LangGraph instead)

---

## 3. Computer Vision (Manufacturing, Healthcare, Retail)

### Tier 1 — POC (2-4 weeks)

| Component | Choice | Cost |
|---|---|---|
| Framework | PyTorch + YOLOv8 or SAM | Free |
| Training | Lambda Labs / Vast.ai GPU | $1-3/hr |
| Deploy | Modal or Replicate | $0.0001-0.01/sec |
| Edge | NVIDIA Jetson Orin ($500) | One-time |

### Tier 2 — Production

| Component | Choice | Cost |
|---|---|---|
| Framework | PyTorch | Free |
| Training infra | AWS SageMaker or GCP Vertex AI | $1K-10K/mo |
| Inference | Triton Inference Server on K8s | $500-2K/mo |
| Edge | Jetson + managed OTA updates | Variable |
| MLOps | Weights & Biases | $50-500/mo |
| Monitoring | EvidentlyAI + Grafana | $100-300/mo |

### Tier 3 — Enterprise

| Component | Choice | Cost |
|---|---|---|
| Full MLOps platform | Databricks MLflow or Palantir Foundry | $10K+/mo |
| Edge | Custom + OTA | Variable |
| Compliance | FDA / CE marking process | Significant |

---

## 4. Predictive Analytics (Forecasting, Risk, Churn)

| Component | Choice | Cost | When |
|---|---|---|---|
| Gradient boosting | **XGBoost** or **LightGBM** | Free | Tabular, fast, explainable |
| Time-series | **Prophet** or **NeuralForecast** | Free | Forecasting specifically |
| Feature store | **Feast** | Free (OSS) | When you have many models |
| Real-time serving | BentoML or Ray Serve | Free | Low-latency requirements |
| Batch | Spark or Polars | Free | Large datasets |

**Default stack for 80% of predictive use cases**:
```
Python + Polars + XGBoost + FastAPI + PostgreSQL + Grafana
Cost: ~$200/mo infra, 1 engineer can run this
```

---

## 5. SaaS Multi-Tenant Architecture

See `references/saas-playbook.md` for deep dive. Quick reference:

| Layer | SMB Choice | Enterprise Choice |
|---|---|---|
| Frontend | Next.js 14 + shadcn/ui | Same |
| API | FastAPI or Next.js API | FastAPI or Go |
| DB | Postgres + Prisma/Drizzle | Postgres + custom ORM |
| Cache | Redis (Upstash) | Redis Cluster |
| Queue | Celery + Redis | Celery + Redis or Temporal |
| Auth | Clerk or Supabase | WorkOS or Auth0 |
| Billing | Stripe | Stripe + custom contracts |
| Storage | S3 or Cloudflare R2 | Same with compliance |
| Email | Resend | Same |
| Search | Postgres FTS or Meilisearch | Elasticsearch |
| Analytics | PostHog | PostHog or Mixpanel |
| Monitoring | Sentry + PostHog | Datadog |
| CI/CD | GitHub Actions | GitHub Actions + manual gates |

---

## 6. Real-Time / Streaming

| Component | Choice | Cost |
|---|---|---|
| Stream processing | Apache Flink or Materialize | $500+/mo |
| Message queue | Kafka or Redpanda | $200-2K/mo |
| Real-time DB | ClickHouse or TimescaleDB | $200-1K/mo |
| Event sourcing | EventStoreDB or custom | Variable |

**Default for 80% of "real-time" needs**: you don't actually need streaming. Use Postgres LISTEN/NOTIFY or Redis pub/sub first.

---

## 7. Data Engineering (Pipelines, Warehousing)

| Component | Choice | Cost |
|---|---|---|
| ETL | dbt + Airflow or Prefect | $200-1K/mo |
| Warehouse | Snowflake or BigQuery | $500+/mo |
| Lakehouse | Databricks or Iceberg + Trino | $1K+/mo |
| CDC | Debezium | Free |
| Orchestration | Dagster or Prefect | Free-OSS |
| Quality | Great Expectations or Soda | Free |

---

## 8. AI Compliance Stack (EU AI Act 2026, GDPR, HIPAA)

| Layer | Tool | Cost |
|---|---|---|
| Model registry | MLflow | Free |
| Bias detection | Fairlearn, Aequitas | Free |
| Evals | Braintrust, Langfuse | $0-500/mo |
| Audit logging | OpenTelemetry + custom | Variable |
| Data lineage | DataHub, Amundsen | Free |
| Explainability | SHAP, LIME | Free |
| Human-in-the-loop | Label Studio or Scale AI | Variable |

**AI Act EU 2026 tiers**:
- **Unacceptable risk**: Banned. Don't build.
- **High risk**: Bias audits, conformity assessment, human oversight, accuracy/robustness evals
- **Limited risk**: Transparency obligations (disclose AI interaction)
- **Minimal risk**: No obligations

---

## 9. Agent & LLM Eval Stack (CRITICAL)

Per [arXiv survey 2602.12430](https://arxiv.org/pdf/2602.12430.pdf) and 2026 best practices:

| Eval Type | Tool | Use Case |
|---|---|---|
| **Deterministic** | Custom Python | Exact match, regex, schema validation |
| **LLM-as-judge** | Braintrust, Langfuse | Open-ended quality, relevance |
| **Human-in-the-loop** | Label Studio, Scale | Ground truth for critical paths |
| **A/B testing** | PostHog, Statsig | Production comparisons |
| **Red teaming** | Custom + Garak | Safety, jailbreak detection |
| **Cost tracking** | Helicone, Langfuse | $/task at scale |
| **Latency tracking** | OpenTelemetry | p50, p95, p99 |

**Rule**: No LLM system ships without at least 2 of these.

---

## Industry-Specific Recommendations

### Manufacturing
- **CV**: PyTorch + YOLOv8 + Jetson Orin at edge
- **Predictive maintenance**: XGBoost + vibration/temp sensors
- **Real-time control**: PLC integration via OPC-UA
- **Compliance**: ISO 9001 + industry-specific (AS9100 aerospace, etc.)

### Healthcare
- **NLP**: Claude + careful PII handling (PHI)
- **CV**: PyTorch + MONAI (medical imaging)
- **Compliance**: HIPAA + FDA for diagnostics
- **Hosting**: BAA with AWS/GCP/Azure required

### Fintech
- **Fraud detection**: XGBoost on transactions + graph features
- **Document AI**: Claude + human-in-the-loop for high-value
- **Compliance**: SOC 2 + PCI-DSS + KYC/AML

### Retail / E-commerce
- **Recommendation**: Two-tower + reranker
- **Search**: Elasticsearch + embedding rerank
- **Inventory**: Time-series forecasting
- **Personalization**: Multi-armed bandits or contextual bandits

### SaaS / B2B
- **Multi-tenant**: Postgres RLS or schema-per-tenant
- **Auth**: Clerk/WorkOS + RBAC
- **Billing**: Stripe + metered billing
- **Onboarding**: PostHog funnels + custom analytics

---

## The Decision Heuristic

When choosing a stack, ask in order:

1. **What's the team's experience?** Don't recommend K8s to a 2-person team.
2. **What's the budget?** Match infra cost to <30% of expected revenue.
3. **What's the time-to-value requirement?** POC vs production changes everything.
4. **What are the compliance constraints?** HIPAA, SOC2, AI Act tier?
5. **What's the scale projection?** 100 DAU vs 1M DAU = different stacks.
6. **What's the lock-in tolerance?** Startups accept lock-in for speed; enterprises avoid it.

---

## Update Log

- 2026-06-18: Initial version. Sources: GetPerspective FDE Tech Stack 2026, Palantir Architecture Center, arXiv Agent Skills Survey, Anthropic Skills docs.
- After each engagement: capture which stack actually shipped, what failed, what surprised us.

