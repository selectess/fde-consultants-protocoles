# FDE Modex Memory — Local Schema

> The swarm's memory lives **in the project**, as files. Zero server required. Zero dependency. Any agent resuming the work reads this directory and has the full state.

---

## Why local-first

A swarm that depends on a remote memory store cannot run offline, cannot be audited by a human with a text editor, and cannot be diffed in git. The FDE Modex stores memory as plain files in the project under `fde-memory/`. The MCP server becomes an **optional sync layer later** (paid, recurring) — not a prerequisite for the swarm to function.

This is consistent with FDE Operating Principle #11 (Runtime-portable: never depend on one SaaS; express work as local files).

---

## Directory layout

```
<project-root>/
└── fde-memory/
    ├── context.json          # contextual memory (current state)
    ├── episodes/             # episodic memory (one file per decision/action)
    │   ├── 2026-06-19-scoping-claim.md
    │   ├── 2026-06-19-h2-promoted.md
    │   └── ...
    ├── lessons.json          # accumulated lessons (compounds across engagements)
    └── trust-score.json      # latest certification verdict
```

---

## 1. `context.json` — Contextual memory

The swarm's "what is true right now" state. Updated at every stage transition by the Lead.

```json
{
  "schema": "fde-modex-context-v1",
  "project": "<one-line project description>",
  "current_stage": "scoping | prototyping | production | feedback",
  "claim": "<the 1-sentence falsifiable claim, anchored on Q6>",
  "six_q": {
    "q1_process": "...",
    "q1_volume": "...",
    "q1_owner": "...",
    "q2_decision_type": "...",
    "q2_latency": "...",
    "q2_accuracy_target": "...",
    "q3_volume": "...",
    "q3_quality": "...",
    "q3_compliance": "...",
    "q4_direct_cost": "...",
    "q4_regulatory": "...",
    "q5_current_type": "...",
    "q5_current_performance": "...",
    "q6_primary_metric": "...",
    "q6_threshold": "..."
  },
  "stakeholders": {
    "decision_maker": "...",
    "budget_owner": "...",
    "daily_user": "...",
    "technical_owner": "...",
    "risk_blocker": "..."
  },
  "open_questions": ["..."],
  "updated_at": "<ISO 8601 timestamp>"
}
```

---

## 2. `episodes/*.md` — Episodic memory

One markdown file per **major action or decision**. This is the audit trail — what was decided, why, with what evidence, and the outcome. An agent resuming later reads these to reconstruct the reasoning.

Filename convention: `YYYY-MM-DD-short-slug.md`.

```markdown
# Episode: <short title>

**Date**: YYYY-MM-DD
**Stage**: scoping | prototyping | production | feedback
**Agent role**: lead | researcher | builder | certifier

## What happened
<1-3 sentences>

## Decision
<what was decided>

## Evidence
- <file:line or command or test that supports the decision>

## Outcome
<what resulted — promoted/pruned/certified/rejected/deferred>

## Lesson (if any)
<reusable insight, also appended to lessons.json>
```

---

## 3. `lessons.json` — Accumulated lessons

Compounds across engagements. Extends the existing `fde-scientific-search-lessons-v1` schema already produced by `skill/scripts/scientific_search.py`. Every pruned hypothesis and every failed certification feeds this file — so the swarm gets smarter over time.

```json
{
  "schema": "fde-scientific-search-lessons-v1",
  "generated_at": "<ISO 8601>",
  "project": "<project description>",
  "promoted_hypothesis_id": "<id or null>",
  "lessons": [
    {
      "hypothesis_id": "H3",
      "description": "Fine-tuned transformer for fraud detection",
      "prune_reason": "held-out gate failed: fraud-low-latency-serving (slower is avoid-trait)",
      "lesson": "Rejected by held-out validation: GPU inference risks the <200ms SLA.",
      "failed_cases": ["fraud-low-latency-serving"],
      "playbook_update": "For similar engagements, reject this pattern unless it resolves the latency trait."
    }
  ]
}
```

---

## 4. `trust-score.json` — Latest certification

Written by the **Certifier** (independent role). See `roles/certifier.md`. This is the gate: a deliverable without a `trust-score.json` of ≥85 has not shipped.

```json
{
  "schema": "fde-trust-score-v1",
  "deliverable": "<path>",
  "claim": "<1-sentence falsifiable claim>",
  "components": {
    "claim": 25,
    "contradiction": 25,
    "evidence": 22,
    "antipatterns": 20
  },
  "trust_score": 92,
  "verdict": "certified",
  "sha256": "<shasum -a 256 of the deliverable>",
  "lowest_component": "evidence",
  "independent_of_lead": true
}
```

---

## Rules

- **Append-only episodes.** Never edit an episode file after writing it — write a new one that supersedes. The audit trail must be linear.
- **`context.json` is mutable.** It is the current snapshot; overwrite it at each stage transition.
- **`lessons.json` grows.** Never delete a lesson. Mark superseded ones with `"superseded": true`.
- **No secrets.** API keys, tokens, passwords never go in memory files. The Certifier's anti-pattern check rejects any memory file containing `sk_`, `password`, `token=`.
- **Human-readable.** Every file is plain JSON or Markdown — openable in any editor, diffable in git, greppable.
