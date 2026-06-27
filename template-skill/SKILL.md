---
name: template-skill
description: A minimal template for creating a new FDE Consultant Skill (Apache-2.0). Use as starting point for any new skill.
---

# My Skill Name

> **Use this as a starting point** for any new FDE Consultant Skill. Copy this folder, rename it, and customize the content.

## Description

[1 paragraph: what this skill does, when to use it, what problem it solves]

## When to use this skill

Activate this skill when the user:
- [Trigger 1: explicit mention of the skill name]
- [Trigger 2: task matches the skill's domain]
- [Trigger 3: project type matches the skill's target]

## What this skill produces

[1 paragraph: what artifacts the skill generates, what quality bar]

## Operating Principles (subset relevant to this skill)

1. [Principle 1 — pick from skill/SKILL.md 14 OP]
2. [Principle 2]
3. [Principle 3]

## Anti-Patterns to avoid

1. [Anti-pattern 1]
2. [Anti-pattern 2]
3. [Anti-pattern 3]

## Workflow

1. **Stage 1 — Scoping**: [what to do]
2. **Stage 2 — Prototyping**: [what to do]
3. **Stage 3 — Production**: [what to do]
4. **Stage 4 — Feedback**: [what to do, end with FDE Assurance Score]

## Examples

### Example 1: [use case]
```
[input -> output]
```

### Example 2: [use case]
```
[input -> output]
```

## Templates

This skill uses these templates (in `skill/templates/`):
- `scoping-report.md` — Stage 1 output
- `prototype-spec.md` — Stage 2 output
- `production-handoff.md` — Stage 3 output
- `productization-memo.md` — Stage 4 output

## Tools (Python)

This skill uses these scripts (in `skill/scripts/`):
- `decompose_problem.py` — validate 6-Q
- `roi_calculator.py` — compute ROI
- `scientific_search.py` — held-out promotion gate
- `evals_runner.py` — 6-trait scoring
- `ontology_extractor.py` — Palantir-style ontology

## References (loaded on demand)

In `skill/references/`:
- `fde-methodology.md` — core methodology
- `fde-trust-score.md` — FDE Assurance Score formula
- `fde-skeptical-deployment.md` — gate protocol

---

## FDE Assurance Score

This template applies its own FDE Assurance Score:

| Component | Max | Actual |
|---|---|---|
| Claim (falsifiable) | 25 | 25 (a template by definition is verifiable) |
| Contradiction (failure modes) | 25 | 20 (acknowledged: customization risk) |
| Evidence trail | 30 | 25 (cross-references to canonical docs) |
| Anti-patterns clean | 20 | 18 (no fake metrics) |
| **TOTAL** | **100** | **88/100** → Certified |

**Note**: When you customize this template, recompute your FDE Assurance Score with your actual evidence.

## License

Apache-2.0.

## Maintainer

[Your name / contact]
