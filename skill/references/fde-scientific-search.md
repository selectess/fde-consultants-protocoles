# FDE Scientific Search

This reference explains how FDE Consultant turns scientific research discipline
into a portable workflow for coding agents and personal agents.

The goal is not to copy an external framework. The goal is to make every agent
behave like a field scientist before it hardens a prototype:

1. Generate competing hypotheses.
2. Evaluate them against development evidence.
3. Validate the winner against held-out constraints.
4. Promote only what survives production ownership.
5. Convert rejected paths into reusable lessons.

Historical note: Arbor-style hypothesis refinement is one inspiration for this
pattern. FDE Consultant does not depend on Arbor, does not claim the Arbor
runtime, and does not create autonomous lab worktrees by default.

## When To Use It

Use FDE Scientific Search during Stage 2 when:

- multiple architectures could plausibly work;
- the user or agent is emotionally attached to one impressive solution;
- production constraints could invalidate the obvious prototype;
- eval data exists or can be carved into development and held-out sets;
- the project needs a defensible handoff, not just a demo.

Do not use it for tiny tasks where one deterministic implementation is enough.

## The FDE-Native Loop

### 1. Start From 6-Q Scoping

The search starts from the same six questions used in the FDE method:

- Q1: process or pain;
- Q2: decision/output;
- Q3: data;
- Q4: cost of error;
- Q5: owner;
- Q6: success threshold.

Without this input, the search becomes architecture theater.

### 2. Generate Candidate Hypotheses

Each hypothesis must name:

- the architecture;
- the operating assumptions;
- required data quality;
- expected latency/cost;
- governance and handoff implications;
- failure modes.

The point is not to generate many ideas. The point is to create real alternatives
that can be compared.

### 3. Score Development Evidence

Development evidence can include:

- fit to the decision type;
- fit to available data;
- explainability needs;
- implementation speed;
- cost of ownership;
- likely operator burden.

This score is useful, but it is not enough for promotion.

### 4. Apply The Held-Out Promotion Gate

Before tuning the prototype, keep validation cases outside the development loop.
The winner must pass this held-out gate before moving toward Stage 3.

Held-out cases should capture constraints such as:

- strict latency;
- auditability;
- regulatory exposure;
- human review requirements;
- low-cost deployment;
- maintainability by the customer's team.

If no candidate passes, do not promote. Return to hypothesis generation or reduce
scope.

### 5. Preserve Failed Paths

Rejected hypotheses are not garbage. They are field intelligence.

Capture:

- why the candidate failed;
- which held-out case blocked it;
- what trait was missing or violated;
- which future playbook, benchmark, template, Academy lesson, or MCP feature
  should learn from the failure.

This is how the Skill compounds.

## Script

Run:

```bash
python3 scripts/scientific_search.py \
  --problem examples/fintech-fraud-detection.json \
  --golden-set examples/fintech-fraud-golden-set.json \
  --lessons-out .fde_lessons.json
```

If no `--golden-set` is provided, the script derives conservative held-out cases
from the 6-Q problem file. For serious engagements, create the golden set
manually before prototype tuning.

## Promotion Rule

A candidate is promoted only if:

- development score meets the threshold; and
- every held-out case passes.

Final selection is ordered by:

1. held-out score;
2. development score;
3. handoff simplicity.

This means a simpler model can beat a more impressive architecture when it is
more auditable, cheaper, faster, or easier to own in production.

## Artifacts To Attach

Attach these to the Prototype Spec:

- candidate comparison table;
- promoted hypothesis;
- held-out validation cases;
- rejected-hypothesis lessons;
- decision rationale.

Attach recurring lessons to the Productization Memo and update playbooks when a
failure pattern appears more than once.

## What To Claim

Do claim:

- FDE-native scientific search;
- held-out promotion gate;
- failure-to-insight learning;
- portable workflow for coding agents and personal agents.

Do not claim:

- Arbor runtime integration;
- autonomous scientific lab;
- parallel multi-agent executors;
- real Git worktrees unless they are actually created;
- automatic merge to production.

## Why It Matters

The biggest FDE failure is not choosing an imperfect architecture. It is choosing
one too early, making it look polished, and discovering the production constraint
too late.

FDE Scientific Search prevents that failure. It makes an agent slow down just
enough to compare paths, protect a held-out gate, and promote only the option
that can survive the customer's real operating environment.
