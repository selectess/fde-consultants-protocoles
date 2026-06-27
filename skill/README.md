# fde-consultant - Open-Source FDE Skill

A portable Forward Deployed Engineering skill for AI coding agents and personal agents.

The skill encodes the FDE operating loop into reusable instructions, references, scripts, templates, tests, and examples so agents can produce real delivery artifacts instead of generic advice.

## What It Does

- **Scope** AI and software projects with the 6-Q decomposition framework.
- **Prototype** with architecture candidates, stack trade-offs, and eval baselines.
- **Productionize** with handoff docs, runbooks, security, observability, and cost thinking.
- **Productize** custom work into reusable templates, scripts, benchmarks, and IP.

## 🚀 Quick Start

### Option 1: Zero-Install (Web UI: ChatGPT, Claude.ai)
Just copy-paste the text from [ZERO-INSTALL.md](ZERO-INSTALL.md) into your prompt or Custom Instructions.

### Option 2: Extra High Level Installer (CLI Agents: Claude Code, Cursor)
Run this in your terminal to auto-configure your agents:
```bash
bash mcp-server/install.sh
```

### Option 3: Manual Install
See [INSTALL.md](INSTALL.md) for manual setup.

## Agent Runtime Notes

| Runtime | How to use today |
|---|---|
| Claude Code | Symlink `skill/` into `~/.claude/skills/fde-consultant`. |
| Codex | Load `skill/SKILL.md` as project guidance and keep the skill folder available. |
| Cursor / Windsurf | Add `skill/` as project context and invoke the FDE role explicitly. |
| Hermes / open agents | Use `SKILL.md` plus references, scripts, and templates as local skill assets. |

## Usage

Activate when work needs a shippable artifact:

```text
/fde-consultant scope a customer support AI triage project
/fde-consultant architect a production RAG system
/fde-consultant evaluate this prototype handoff
/fde-consultant productize the reusable parts of this engagement
```

## Quality Standard

Reject outputs that are generic, unquantified, missing evals, missing owners, or missing production path. Every serious output should score against the 6-trait FDE rubric: customer curiosity, ownership, decomposition, empathy, product sense, and communication.

## MCP Beta

The hosted MCP layer in `../mcp-server/` is separate from the open-source skill and should be presented as Beta/coming soon until persistence, billing, monitoring, and production hardening are complete.

## License

Apache-2.0 - free for personal and commercial use.
