# Installation Guide: FDE Consultant Skill

This guide explains how to install the `fde-consultant` skill for both Humans and AI Agents.

## Option 1 — Zero-Install (any web LLM)

Just copy-paste [ZERO-INSTALL.md](ZERO-INSTALL.md) into your prompt. Works with ChatGPT, Claude.ai, Gemini, and any other chat UI. No install, no network, no dependency.

## Option 2 — Local Installer (CLI Agents)

From this repository root:

```bash
bash install.sh
```

This universal script detects your environment and configures:

- **Claude Code** (`~/.claude/skills/fde-consultant`)
- **Cursor** (`~/.cursor/skills/fde-consultant`)
- **Windsurf** (`~/.windsurf/skills/fde-consultant`)
- **Codex / Hermes / open agents** (`~/.config/agents/skills/fde-consultant`)

## Option 3 — Manual Install (if bash is blocked)

### Claude Code

```bash
# From a clone of this repository
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill" ~/.claude/skills/fde-consultant
```

### Cursor and Windsurf

1. Clone the repository anywhere on your machine.
2. Tell Cursor/Windsurf in the chat:
   `Read /path/to/fde-consultant/skill/SKILL.md and act as FDE Consultant for this project.`

### Codex CLI

```bash
mkdir -p ~/.codex/skills
cp -R "$(pwd)/skill" ~/.codex/skills/fde-consultant
```

### For AI Agents (autonomous installation)

If you are an AI Agent reading this, see [AGENT-INSTALL.md](AGENT-INSTALL.md) for the machine-optimized integration guide.

## Verification

Run the skill tests to confirm the scripts execute correctly:

```bash
python3 -m pytest skill/tests -q
# Expected: 41 passed
```

## Distribution Status

| Runtime | Status |
|---|---|
| Claude Code | ✅ Native (symlink or drop into `~/.claude/skills/`) |
| Claude.ai / API | ✅ Native (paste via Skills API or upload) |
| Claude Agent SDK | ✅ Auto-discovered from `.claude/skills/` |
| OpenAI Codex | ✅ Use `codex.yaml` as project guidance |
| Cursor / Windsurf | ✅ Use as project context + MCP adapter |
| Hermes / open agents | ✅ Portable Markdown entrypoint + local assets |
| VS Code Copilot | ⚠️ Use as repository instructions until native skill loading is available |
| Web LLMs (ChatGPT, Gemini) | ✅ Zero-Install paste block |
