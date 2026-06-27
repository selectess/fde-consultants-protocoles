---
title: FDE Document Output — render deliverables as real files via Agent Skills
description: Map each FDE deliverable to an Anthropic document skill (docx/pptx/xlsx/pdf) and how to invoke it.
---

# FDE Document Output

> **Status (2026-06).** Rendering is performed by composing Anthropic document skills (docx/pptx/xlsx) as a deliberate agent step — it is **not auto-invoked** by `modex engage` or the Collective, which emit the deliverable as Markdown. To get a real file today, instruct the agent to render the Markdown deliverable (e.g. "render this scoping report as a polished .docx"). Automated rendering inside the engage flow is on the roadmap.

FDE deliverables are drafted as markdown, then **rendered into client-ready files** using the official
Anthropic document skills (`docx`, `pptx`, `xlsx`, `pdf`). This is the "ship artifacts, not slides"
principle made literal: the customer receives a real Word/PowerPoint/Excel/PDF, not a chat transcript.

## Deliverable → skill map

| FDE deliverable | Stage | Render with | Format |
|---|---|---|---|
| Scoping report (`templates/scoping-report.md`) | 1 | **docx** | `.docx` (TOC, headings, tables) |
| Prototype spec (`templates/prototype-spec.md`) | 2 | **docx** | `.docx` |
| ROI model / sensitivity (`scripts/roi_calculator.py`) | 1-2 | **xlsx** | `.xlsx` (formulas, charts) |
| Architecture diagram (Mermaid) | 2 | **pdf** | `.pdf` (export the rendered diagram) |
| Production handoff (`templates/production-handoff.md`) | 3 | **docx** or **pdf** | runbook/ADRs |
| Executive AI strategy (cloud `fde_executive`) | 4 | **pptx** | `.pptx` deck |
| Productization memo (`templates/productization-memo.md`) | 4 | **docx** | `.docx` |
| FDE Assurance Score certificate | cross | **pdf** | signed `.pdf` (badge + SHA-256) |

## How to invoke

**A. Claude Code (local skills installed in `~/.claude/skills/`)** — the document skill triggers
automatically when the agent is asked to produce a `.docx`/`.pptx`/`.xlsx`/`.pdf`. After drafting the
markdown deliverable, instruct: *"Render this scoping report as a polished .docx."* The `docx` skill runs.

**B. Messages API / MCP cloud (`container.skills`)** — for the hosted product, attach the skill to the
container and run code execution:

```python
client.beta.messages.create(
    model="claude-opus-4-8", max_tokens=8192,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={"skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]},
    tools=[{"type": "code_execution_20260521", "name": "code_execution"}],
    messages=[{"role": "user", "content": "<the drafted exec-strategy markdown> — render as a 6-slide .pptx"}],
)
# download the generated file via client.beta.files.download(file_id)
```

Up to 8 skills per request. The cloud tool that maps cleanly: `fde_executive` → `pptx`,
`fde_scope` → `docx`, `fde_roadmap` → `xlsx`.

## Operating principle
A deliverable is not "shipped" until it exists as a **real file the customer can open** and it carries
its `## FDE Assurance Score` section. Markdown is the draft; the document skill produces the artifact.
