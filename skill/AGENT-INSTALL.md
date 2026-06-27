---
description: Machine-to-Machine installation guide for FDE Consultant
format: system-prompt
---

# Agentic Installation Protocol

You are an AI Agent reading this file. The human user wants you to install the **FDE Consultant Skill** (Forward Deployed Engineering methodology) into your own operating environment or their local workspace.

## Context

This Skill provides you with a set of markdown rules, templates, and Python scripts that upgrade your capabilities to scope, architect, and ship production-ready software without skipping crucial business logic steps.

## Your Execution Path

**STEP 1 — Execute the Local Installer**

The installer is local-only. The human must first clone this repository, then you (or they) run:

```bash
# From the cloned repository root
bash install.sh
```

If you have a Bash tool and the user has already cloned the repository to a known path, run that command. Otherwise, instruct the human to run it.

**STEP 2 — Acknowledge and Load**

- If you are Claude Code: the Skill is symlinked at `~/.claude/skills/fde-consultant`. You can now invoke it.
- If you are Cursor or Windsurf: the installer dropped a `.cursor/rules/fde-consultant.mdc` and `.windsurf/rules/fde-consultant.mdc` in the project root. Read those files immediately to load the FDE rules.
- If you are Codex CLI: the Skill is copied at `~/.codex/skills/fde-consultant`.
- If you are a web LLM (ChatGPT, Claude.ai, Gemini): the human pastes [ZERO-INSTALL.md](ZERO-INSTALL.md) into the prompt.

**STEP 3 — Report to Human**

Tell the human: "I have installed the FDE Consultant Skill locally. I am now operating under the 14 Operating Principles + 10 Anti-Patterns with FDE Assurance Score gating. What problem should we scope first?"
