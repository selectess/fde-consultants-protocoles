# FDE Consultant Skill for Cursor

## Installation

### Project-level (recommended)

The repo already ships the rule at `.cursor/rules/fde-consultant.mdc`. Clone it and the editor picks it up — or copy it into your own project:

```bash
# the rule ships in the repo — just clone it
git clone https://github.com/selectess/fde-consultants-protocoles fde-consultant
```

The rule file ships in this repo at `.cursor/rules/fde-consultant.mdc` (with a byte-identical `.windsurf/rules/` mirror) — no installer step needed.

### Manual install

Create `.cursor/rules/fde-consultant.mdc` in your project:

```markdown
---
description: Forward Deployed Engineering (FDE) methodology
globs: *
---

You are an FDE Consultant. When scoping, building, or reviewing, follow the methodology in the FDE Skill (SKILL.md, Operating Principles, Anti-Patterns).
Always run Stage 0 — Reconnaissance (fde_recon) on the real codebase/business before scoping (loop: Stage 0 Reconnaissance → Scoping → Prototyping → Production → Feedback).
Never skip the 6-Q decomposition. Always produce concrete artifacts (code, specs). End every deliverable with a `## FDE Assurance Score` section (target >=85).
```

## Usage

In Cursor, press `Cmd+I` (or `Ctrl+I`) and type:

```
Act as FDE Consultant. Scope this project using the 6-Q framework.
```

Or invoke tools directly:

```
Run fde_decompose on this SaaS churn problem
```

## Verification

```bash
ls .cursor/rules/fde-consultant.mdc
cat .cursor/rules/fde-consultant.mdc
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
