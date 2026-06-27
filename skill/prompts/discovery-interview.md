# Discovery Interview Prompt — Stage 1c of Scoping

**Purpose**: Drive the 6-Q decomposition interview after domain research is complete.

**When to use**: AFTER `prompts/domain-research.md` has produced a dossier. NEVER before.

---

## The Pre-Interview Setup

Before asking any question:
1. Review the domain dossier
2. Confirm the industry is correctly identified ("Just to confirm — you're in [X]?")
3. Confirm the engagement type (New Project / Startup / Business Upgrade)
4. Set expectations ("I'll ask 6 specific questions; each requires a concrete answer")

---

## The 6-Q Framework

For EACH question, follow this structure:

1. **Acknowledge** what you know from the dossier
2. **Infer** what their context likely is
3. **Ask** the targeted question with a request for a number

---

### Q1 — The Specific Process

❌ Bad:
- "What problem are you trying to solve?"
- "Tell me about your business"

✅ Good (informed by dossier):
- "Based on my research, the top pain in [industry] is [X]. Which specific process are you targeting? Not 'everything' — pick ONE. Examples: [industry-specific options]."

**Drill deeper**:
- "How often does this process run? Daily? Weekly?"
- "Who currently owns it?"
- "What's the volume? [Number] per [period]?"

**Output**: Specific process named with volume/frequency.

### Q2 — The Decision / Output Type

❌ Bad:
- "What do you want the AI to do?"

✅ Good:
- "What kind of decision or output? Pick one:
  - Classification (this is X / not X)
  - Probability score (X% chance of Y)
  - Ranking (sort these by Z)
  - Generation (write/draft/summarize)
  - Recommendation (suggest action)
  - Prediction (forecast value Y at time T)"

**Drill deeper**:
- "What's the latency requirement? Real-time (<1s), near-real-time (<10s), or batch (hours)?"
- "What's the accuracy/quality threshold? (X%)"

**Output**: Decision type with latency and accuracy targets.

### Q3 — Data Availability

❌ Bad:
- "Do you have data?"

✅ Good:
- "What data is available for this process?
  - Volume: [N records / N GB]
  - Latency: [real-time stream / daily batch / historical only]
  - Quality: [clean / messy / unlabeled / partially labeled]
  - Compliance: [any PII / PHI / regulated data]
  - Retention: [how far back]
  - Format: [structured / unstructured / both]"

**Drill deeper**:
- "If unlabeled, who would label? Cost per label? Time?"
- "Who owns the data? Can we use it for training?"
- "What's the data refresh rate?"

**Output**: Data inventory with quantity, quality, and constraints.

### Q4 — Cost of Error

❌ Bad:
- "How bad is it if the AI is wrong?"

✅ Good:
- "What's the cost of a wrong decision?
  - Direct cost: $X per wrong decision
  - Indirect cost: [rework, customer churn, compliance]
  - Regulatory exposure: [any fines, legal liability]
  - Safety risk: [any physical safety implications]
  - Reputation risk: [public-facing or internal]"

**Drill deeper**:
- "What's the distribution? (95% safe, 5% catastrophic? Or 50/50 mediocre?)"
- "Is human review possible/required for high-stakes cases?"

**Output**: Quantified cost of error with risk distribution.

### Q5 — Current System

❌ Bad:
- "How do you do it now?"

✅ Good:
- "What does the current system look like?
  - Manual: [X people, Y hours per task]
  - Rules-based: [what rules, who maintains]
  - ML model: [what model, when deployed, current accuracy]
  - Vendor SaaS: [which one, cost, satisfaction]
  - Spreadsheet: [how many, who maintains]"

**Drill deeper**:
- "What's the current performance? (X% accuracy, Y hour turnaround)"
- "What works well about it? (Don't fix what's not broken)"
- "What's the biggest frustration?"

**Output**: Current state with performance baseline.

### Q6 — Success Metric

❌ Bad:
- "How will you measure success?"

✅ Good:
- "What does success look like, in business terms?
  - Revenue: [€X/year enabled]
  - Cost: [€Y/year saved]
  - Time: [Z hours/week freed up]
  - Risk: [€A/year risk reduced]
  - Customer: [NPS +X, churn -Y%]
  - Employee: [morale, retention]"

**Drill deeper**:
- "How will we measure this? [dashboard, quarterly review, audit]"
- "What's the threshold for 'good enough'? [specific number]"
- "What's the minimum viable improvement to proceed? [baseline + X%]"

**Output**: Quantified success metric with measurement plan.

---

## Handling Vague Answers

When the user can't give a number, push back:

```
"That's helpful context, but I need a number to scope this properly. Let me help you estimate:
- Based on [research from dossier], companies like yours typically see [X]
- If we assume [reasonable assumption], the impact would be [Y]
- Can you confirm this is in the right ballpark, or do you have a better number?"
```

**Never accept**:
- "We'll see"
- "It should be significant"
- "Around [vague descriptor]"
- "Compared to current, much better"

---

## Closing the Interview

After Q1-6 are answered:

1. **Recap** what you heard (in their words)
2. **Identify gaps** in your understanding
3. **Propose next step**:
   - "I have enough to draft a Scoping Report. I'll send it within [X days]."
   - "I need to research [Y] before I can scope this. Expect the report by [date]."
4. **Set expectations**:
   - "The scoping report will include [deliverables]"
   - "You'll review and we iterate"
   - "Then we decide whether to proceed to prototype"

---

## Tone Guidance

- **Be a peer, not an interrogator**
- **Show what you know** (cite dossier facts)
- **Ask for numbers, not adjectives**
- **Push back on vagueness**
- **Be willing to say "I don't know, let me research that"**
- **Never fake expertise** — admit when you need to dig

---

## Common Patterns to Watch

| User Type | Tendency | Your Response |
|---|---|---|
| **CEO/Founder** | Strategic, vague on details | "Help me understand the operational reality" |
| **CTO/Engineer** | Technical detail, misses business | "How does this translate to $ impact?" |
| **Product Manager** | Feature-focused | "What's the underlying problem vs the feature?" |
| **Operations Lead** | Process-focused, may not see tech | "Here's what similar companies built..." |
| **Consultant** | May be selling you something | "What's YOUR stake in this project?" |

---

## Output Format

After the interview, compile:

```markdown
# Discovery Interview Notes — [Project Name]

## Engagement Type
[New Project / Startup / Business Upgrade]

## Customer Context
- Industry: [X]
- Size: [employees, revenue]
- Stage: [seed / growth / mature]
- Geography: [markets]

## Q1 — Specific Process
- Target process: [name]
- Volume: [N/period]
- Owner: [role/name]

## Q2 — Decision/Output
- Type: [classification / ranking / generation / etc.]
- Latency target: [X]
- Accuracy target: [Y%]

## Q3 — Data
- Volume: [N records / GB]
- Quality: [clean / messy / unlabeled]
- Compliance: [PII / PHI / regulated]
- Refresh: [real-time / batch / static]

## Q4 — Cost of Error
- Direct cost: [$/wrong decision]
- Indirect cost: [description]
- Regulatory: [exposure]
- Distribution: [e.g., 95% safe, 5% catastrophic]

## Q5 — Current System
- Type: [manual / rules / ML / vendor / spreadsheet]
- Performance: [accuracy, time]
- Frustrations: [list]

## Q6 — Success Metric
- Primary: [$/year / hours / risk / customer]
- Threshold: [number]
- Measurement: [how]

## Gaps to Research
- [Gap 1]
- [Gap 2]

## Initial Recommendation
[1-2 sentences on the highest-leverage opportunity]

## Next Step
[Scoping report, prototype, or further research]
```

---

## Update Log

- 2026-06-18: Initial version.
