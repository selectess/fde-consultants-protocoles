# AI & Agent Engineering — 2026 Reference

**Last updated**: 2026-06-18

The complete reference for designing, building, evaluating, and productionizing AI/agent systems in 2026.

---

## Part 1 — The 2026 AI Stack

### Model Selection Matrix

| Model | Best For | Cost (per 1M tokens) | Context | Notes |
|---|---|---|---|---|
| **Claude Sonnet 4.5** | Reasoning, tool use, code | $3 in / $15 out | 200K | Default for production |
| **Claude Haiku 4** | Fast classification, extraction | $0.80 in / $4 out | 200K | When speed matters |
| **Claude Opus 4** | Deep analysis, complex reasoning | $15 in / $75 out | 200K | When accuracy is critical |
| **GPT-4o** | Multimodal, broad knowledge | $5 in / $15 out | 128K | When Claude isn't best |
| **GPT-4o-mini** | Cheap extraction, classification | $0.15 in / $0.60 out | 128K | High-volume tasks |
| **Open-source (Llama 3.3, Mistral)** | Data-sensitive, cost-critical | Self-hosted | Variable | When you need control |

**Default strategy 2026**: Multi-model with Claude as primary, GPT-4o-mini for extraction, local models for sensitive data.

---

## Part 2 — Prompt Engineering Patterns

### Pattern 1 — System Prompt Structure

```markdown
# Role
You are [specific role with specific expertise]

# Context
[User's situation, what they need, why]

# Constraints
- Constraint 1
- Constraint 2
- Never do X

# Output Format
[Specific structure, e.g., JSON, markdown, 5 bullets]

# Examples
[2-3 examples of good outputs]

# Reasoning
[Step-by-step thinking before responding]
```

### Pattern 2 — Chain of Thought (CoT)

For complex reasoning:
```
Before answering, think through:
1. What is being asked?
2. What context is needed?
3. What are the trade-offs?
4. What's the best answer given the constraints?
5. How confident am I? (high/medium/low)
```

### Pattern 3 — Few-Shot Examples

```markdown
Extract the user's pain point from this interview transcript.

Example 1:
Input: "We waste 3 hours per day copying data between systems"
Output: {
  "pain": "Manual data entry between systems",
  "frequency": "daily",
  "cost": "3 hours/day = $X/year"
}

Example 2:
...
```

### Pattern 4 — Structured Outputs

Use JSON schema with tool use for guaranteed structure:
```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    tools=[{
        "name": "extract_pain_points",
        "description": "Extract pain points from interview",
        "input_schema": {
            "type": "object",
            "properties": {
                "pains": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                            "cost_estimate": {"type": "string"}
                        }
                    }
                }
            }
        }
    }],
    messages=[...]
)
```

### Pattern 5 — Context Stuffing vs RAG

**Context stuffing**: Put everything in the prompt. Good when:
- Total context < 50K tokens
- Latency-critical
- All context always relevant

**RAG**: Retrieve relevant chunks. Good when:
- Total corpus > 100K tokens
- Most context is irrelevant to query
- Updates happen frequently
- Cost matters

---

## Part 3 — RAG Architecture (2026 Best Practices)

### The Pipeline

```
Documents
  ↓ Ingestion
  ↓ Chunking (semantic, ~500 tokens with overlap)
  ↓ Embedding (voyage-3 or text-embedding-3)
  ↓ Storage (Pinecone/Qdrant/pgvector)
  ↓
Query
  ↓ Embedding
  ↓ Retrieval (top-K with reranking)
  ↓ Reranking (Cohere rerank-3 or similar)
  ↓ Context assembly
  ↓ LLM with retrieved context
  ↓ Answer + citations
```

### Chunking Strategies

| Strategy | When | Trade-off |
|---|---|---|
| **Fixed size (500 tokens)** | Generic text | Simple but breaks mid-thought |
| **Semantic chunking** | Long-form content | Slower ingestion, better retrieval |
| **Document structure** | Markdown, code | Preserves context |
| **Agent-based** | Mixed content | Expensive but adaptive |

**Default in 2026**: Semantic chunking with 500-token target, 50-token overlap.

### Embedding Models

| Model | Dimensions | Cost | When |
|---|---|---|---|
| **voyage-3** | 1024 | $0.06/M tokens | Best quality (Anthropic) |
| **text-embedding-3-large** | 3072 | $0.13/M tokens | OpenAI alternative |
| **text-embedding-3-small** | 1536 | $0.02/M tokens | Cost-optimized |
| **BGE-large-en-v1.5** | 1024 | Self-hosted | When data can't leave |

### Retrieval Optimization

**Hybrid search**: Combine BM25 (keyword) + vector (semantic)
```python
results = hybrid_search(
    query="user's question",
    alpha=0.7,  # weight: 0.7 semantic, 0.3 keyword
    top_k=20,
)
```

**Reranking**: Always rerank top-K for production
```python
results = vector_search(query, top_k=50)
reranked = cohere.rerank(query, results, top_k=5)
```

**Multi-query**: Generate 3-5 query variants, merge results
**HyDE**: Generate hypothetical answer, embed that, search
**Self-query**: Extract filters from query ("docs from 2025 only")

---

## Part 4 — Agent Architectures

### Pattern 1 — Single Agent + Tools

```
Agent (Claude)
  ├── Web Search
  ├── Database Query
  ├── Calculator
  ├── Email Send
  └── Code Execution
```

**When**: Tasks are sequential, single domain, <10 tools.
**Risk**: Context can blow up with too many tool results.

### Pattern 2 — Supervisor + Workers

```
Supervisor Agent
  ├── Decomposes task
  ├── Assigns to Worker 1 (Researcher)
  ├── Assigns to Worker 2 (Analyst)
  ├── Assigns to Worker 3 (Writer)
  └── Aggregates & validates
```

**When**: Complex multi-step tasks, different specializations needed.
**Tools**: LangGraph, CrewAI, Claude Agent SDK.

### Pattern 3 — Pipeline / DAG

```
Input → Agent 1 → Agent 2 → Agent 3 → Output
```

**When**: Predictable sequence, each step is well-defined.
**Tools**: Temporal, custom Celery chains.

### Pattern 4 — Debate / Reflection

```
Agent A generates answer
  ↓
Agent B critiques
  ↓
Agent A revises
  ↓
Final answer
```

**When**: Quality is critical, latency is acceptable.
**Cost**: 2-3× the tokens.

### Pattern 5 — Plan-and-Execute

```
Planner: Decompose into steps
  ↓
Executor: Execute step 1, observe result
  ↓
Re-planner: Adjust plan based on observation
  ↓
Executor: Execute step 2
  ↓
...
```

**When**: Long-horizon tasks, dynamic environments.
**Tools**: LangGraph, AutoGPT (avoid), Claude Agent SDK.

---

## Part 5 — Multi-Agent Best Practices

1. **Single source of truth**: Shared state in a database, not in agent memory
2. **Idempotent actions**: Each tool call should be safe to retry
3. **Timeout everything**: Every agent step has a max duration
4. **Cost budgets**: Hard cap on $/task, fail gracefully if exceeded
5. **Human-in-the-loop checkpoints**: For high-stakes decisions
6. **Eval every transition**: Between agents, validate handoffs
7. **Log everything**: Every prompt, every tool call, every response
8. **Version control prompts**: Git-versioned, reviewed like code

---

## Part 6 — Eval Framework (CRITICAL)

**No AI system ships without an eval framework. Non-negotiable.**

### The 4-Layer Eval Stack

**Layer 1 — Deterministic checks** (always run)
- Schema validation (JSON shape)
- Regex matches (no banned phrases)
- Length checks
- Required fields present
- Type checks

**Layer 2 — Reference-based** (when ground truth exists)
- Exact match
- BLEU / ROUGE for text
- Embedding similarity
- F1 score for classification

**Layer 3 — LLM-as-judge** (when ground truth is hard)
- Use Claude/GPT-4 to score outputs 1-5
- Provide rubric
- Sample 100+ cases, validate against human labels
- Cost: ~$0.01-0.05/eval

**Layer 4 — Human-in-the-loop** (for critical paths)
- Random sample review
- Edge case review
- Disagreement adjudication

### Eval Set Design

```python
eval_set = {
    "happy_path": [...],        # 50% — typical cases
    "edge_cases": [...],        # 25% — unusual but valid
    "adversarial": [...],       # 15% — attacks, jailbreaks
    "regression": [...],        # 10% — known past failures
}
```

### The Eval Pipeline

```python
# 1. Define success metrics
def success_metric(output, expected):
    return llm_judge(output, expected) >= 4

# 2. Run on eval set
results = run_eval(model, eval_set, success_metric)

# 3. Report
print(f"Pass rate: {results.pass_rate}%")
print(f"By category: {results.by_category}")
print(f"Failures: {results.failures[:10]}")
```

### Drift Detection

- Run eval set weekly on production model
- Alert if pass rate drops >5%
- Alert if p95 latency increases >20%
- Alert if cost per task increases >15%

---

## Part 7 — Guardrails

### Input Guardrails
- PII detection (Presidio, regex)
- Prompt injection detection (separate model)
- Topic filtering
- Length limits
- Rate limiting per user

### Output Guardrails
- Schema validation
- Toxicity detection (Perspective API, custom)
- Hallucination detection (self-consistency, citation check)
- PII filtering in output
- Action validation (don't call dangerous tools without approval)

### Implementation Pattern

```python
def safe_agent_call(user_input):
    # Input guardrails
    if contains_pii(user_input):
        return redact_pii(user_input)
    if is_prompt_injection(user_input):
        return "I can't process that request"
    
    # Agent execution with timeout
    try:
        with timeout(30):
            output = agent.run(user_input)
    except TimeoutError:
        return "Request took too long"
    
    # Output guardrails
    if not validate_schema(output):
        return retry_with_feedback()
    if contains_toxicity(output):
        return safe_fallback()
    
    return output
```

---

## Part 8 — Cost Engineering

### Cost Model

```
Total cost = (LLM tokens × $/token) + (embedding × $/token) + (vector DB queries × $/query) + (compute × $/hr) + (storage × $/GB)
```

### Optimization Levers

1. **Model selection**: Use smallest model that meets quality bar
2. **Caching**: Semantic cache for repeated queries (Redis + embedding)
3. **Batching**: Group requests to share prompts
4. **Truncation**: Don't send full conversation if not needed
5. **Streaming**: For user-facing, improves perceived latency
6. **Speculative execution**: Pre-compute likely responses

### Cost Targets (2026)

| Use Case | Target $/task |
|---|---|
| Classification | $0.0001 |
| Extraction | $0.001 |
| Q&A (RAG) | $0.01 |
| Generation | $0.05 |
| Multi-agent task | $0.50 |
| Complex reasoning | $1.00+ |

**If your cost is way above target, you have a design problem, not a cost problem.**

---

## Part 9 — Production Patterns

### Deployment

```yaml
# Standard production deployment
api:
  image: myagent:latest
  replicas: 3
  resources:
    cpu: 500m
    memory: 1Gi
  env:
    - ANTHROPIC_API_KEY
    - DATABASE_URL
    - REDIS_URL
  liveness:
    path: /health
    interval: 30s
  readiness:
    path: /ready
    interval: 10s
```

### Observability

Every AI request should log:
- `request_id`
- `user_id`
- `tenant_id`
- `model`
- `prompt_tokens`
- `completion_tokens`
- `cost_usd`
- `latency_ms`
- `eval_scores`
- `tool_calls`
- `trace_id`

### Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| LLM API down | Health check | Retry with exponential backoff, fallback to different model |
| Output malformed | Schema validation fails | Retry with feedback, or fall back to default |
| Cost spike | Cost tracking alert | Switch to cheaper model, throttle |
| Quality regression | Eval drift detection | Roll back to previous version |
| Hallucination | Citation check, self-consistency | Add human-in-the-loop |
| Prompt injection | Input classifier | Reject, log, alert |

---

## Part 10 — AI Act EU 2026 Compliance

Tiers:
- **Unacceptable risk**: Banned. Don't build (social scoring, manipulation, etc.)
- **High risk**: Bias audits, conformity assessment, human oversight, accuracy/robustness evals, documentation
- **Limited risk**: Transparency obligations (disclose AI interaction)
- **Minimal risk**: No obligations

For every AI system you build, classify its tier BEFORE shipping.

---

## Sources

- Anthropic — Claude docs, Claude Agent SDK, Skills
- OpenAI — Function calling, structured outputs, evals
- LangChain/LangGraph — Orchestration patterns
- Braintrust / Langfuse / Helicone — Eval & observability
- arXiv 2602.12430 — Agent Skills Survey
- EU AI Act official documentation
- GetPerspective — FDE Tech Stack 2026

---

## Update Log

- 2026-06-18: Initial version.
